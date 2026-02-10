"""
Schema Markup Checker
Detects and validates JSON-LD, Microdata, and RDFa structured data on a page.
"""

import json
import re


class SchemaAnalyzer:
    """Analyzes structured data markup on a webpage."""

    COMMON_TYPES = {
        'Article': ['headline', 'author', 'datePublished', 'image'],
        'Product': ['name', 'image', 'description', 'offers'],
        'LocalBusiness': ['name', 'address', 'telephone'],
        'Organization': ['name', 'url', 'logo'],
        'Person': ['name'],
        'WebSite': ['name', 'url'],
        'BreadcrumbList': ['itemListElement'],
        'FAQPage': ['mainEntity'],
        'HowTo': ['name', 'step'],
        'Event': ['name', 'startDate', 'location'],
        'Recipe': ['name', 'image', 'author', 'recipeIngredient'],
        'VideoObject': ['name', 'description', 'thumbnailUrl', 'uploadDate'],
    }

    def __init__(self, soup):
        self.soup = soup
        self.issues = []
        self.recommendations = []

    def analyze(self):
        """Run full schema analysis."""
        jsonld_data = self._extract_jsonld()
        microdata = self._detect_microdata()
        rdfa = self._detect_rdfa()

        all_schemas = []
        for item in jsonld_data:
            schema_type = item.get('@type', 'Unknown')
            if isinstance(schema_type, list):
                schema_type = ', '.join(schema_type)
            validation = self._validate_schema(item)
            all_schemas.append({
                'type': schema_type,
                'format': 'JSON-LD',
                'valid': validation['valid'],
                'fields_found': validation['fields_found'],
                'fields_missing': validation['fields_missing'],
                'raw': item
            })

        has_any = len(all_schemas) > 0 or microdata['count'] > 0 or rdfa['count'] > 0

        if not has_any:
            self.issues.append({
                'severity': 'high',
                'message': 'No structured data found on this page'
            })
            self.recommendations.append({
                'category': 'Schema',
                'recommendation': 'Add JSON-LD structured data to improve rich snippet eligibility'
            })

        # Score
        score = self._calculate_score(all_schemas, has_any)

        return {
            'score': score,
            'has_structured_data': has_any,
            'jsonld_schemas': all_schemas,
            'jsonld_count': len(all_schemas),
            'microdata_count': microdata['count'],
            'microdata_types': microdata['types'],
            'rdfa_count': rdfa['count'],
            'total_schemas': len(all_schemas) + microdata['count'] + rdfa['count'],
            'issues': self.issues,
            'recommendations': self.recommendations
        }

    def _extract_jsonld(self):
        """Extract JSON-LD structured data from script tags."""
        schemas = []
        scripts = self.soup.find_all('script', type='application/ld+json')

        for script in scripts:
            try:
                text = script.string
                if text:
                    data = json.loads(text)
                    if isinstance(data, list):
                        schemas.extend(data)
                    elif isinstance(data, dict):
                        # Handle @graph
                        if '@graph' in data:
                            schemas.extend(data['@graph'])
                        else:
                            schemas.append(data)
            except (json.JSONDecodeError, TypeError):
                self.issues.append({
                    'severity': 'medium',
                    'message': 'Invalid JSON-LD found — could not parse'
                })

        return schemas

    def _detect_microdata(self):
        """Detect Microdata (itemscope/itemprop) usage."""
        itemscopes = self.soup.find_all(attrs={'itemscope': True})
        types = []
        for el in itemscopes:
            t = el.get('itemtype', '')
            if t:
                # Extract type name from URL like "https://schema.org/Article"
                name = t.rstrip('/').split('/')[-1]
                if name not in types:
                    types.append(name)
        return {'count': len(itemscopes), 'types': types}

    def _detect_rdfa(self):
        """Detect RDFa attributes."""
        rdfa_elements = self.soup.find_all(attrs={'typeof': True})
        return {'count': len(rdfa_elements)}

    def _validate_schema(self, schema):
        """Validate a JSON-LD schema against known required fields."""
        schema_type = schema.get('@type', '')
        if isinstance(schema_type, list):
            schema_type = schema_type[0] if schema_type else ''

        required = self.COMMON_TYPES.get(schema_type, [])
        fields_found = []
        fields_missing = []

        for field in required:
            if field in schema and schema[field]:
                fields_found.append(field)
            else:
                fields_missing.append(field)

        valid = len(fields_missing) == 0

        if fields_missing:
            self.issues.append({
                'severity': 'medium',
                'message': f'{schema_type}: Missing fields — {", ".join(fields_missing)}'
            })

        return {
            'valid': valid,
            'fields_found': fields_found,
            'fields_missing': fields_missing
        }

    def _calculate_score(self, schemas, has_any):
        """Calculate schema markup score (0-100)."""
        if not has_any:
            return 0

        score = 40  # Base score for having any structured data

        # Points for JSON-LD (preferred format)
        if schemas:
            score += 20

        # Points for valid schemas
        valid_count = sum(1 for s in schemas if s['valid'])
        if schemas:
            validity_ratio = valid_count / len(schemas)
            score += int(validity_ratio * 30)

        # Points for multiple schemas
        if len(schemas) >= 2:
            score += 10

        return min(score, 100)
