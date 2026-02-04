"""
SEO Scorer Module
Aggregates all analyzer scores into an overall SEO score
"""


class SEOScorer:
    """Calculates overall SEO score from individual analyzer results"""
    
    # Weights for each category (must sum to 1.0)
    WEIGHTS = {
        'title': 0.15,
        'meta_description': 0.12,
        'url_structure': 0.10,
        'headings': 0.13,
        'content': 0.18,
        'images': 0.10,
        'links': 0.12,
        'performance': 0.10
    }
    
    PRIORITY_THRESHOLDS = {
        'high': 40,
        'medium': 70,
        'low': 85
    }
    
    def __init__(self):
        self.results = {}
    
    def set_results(self, results: dict):
        """Set analyzer results"""
        self.results = results
    
    def calculate_overall_score(self) -> int:
        """Calculate weighted overall SEO score"""
        total_score = 0
        total_weight = 0
        
        for category, weight in self.WEIGHTS.items():
            if category in self.results and 'score' in self.results[category]:
                total_score += self.results[category]['score'] * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0
        
        # Normalize if not all categories present
        return round(total_score / total_weight)
    
    def get_priority_issues(self) -> dict:
        """Categorize all issues by priority level"""
        priority_issues = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for category, data in self.results.items():
            if 'issues' not in data:
                continue
            
            score = data.get('score', 100)
            
            for issue in data['issues']:
                issue_with_category = {
                    'category': category,
                    'type': issue.get('type', 'info'),
                    'message': issue.get('message', '')
                }
                
                # Determine priority based on issue type and category score
                if issue['type'] == 'critical' or score < self.PRIORITY_THRESHOLDS['high']:
                    priority_issues['high'].append(issue_with_category)
                elif issue['type'] == 'warning' or score < self.PRIORITY_THRESHOLDS['medium']:
                    priority_issues['medium'].append(issue_with_category)
                else:
                    priority_issues['low'].append(issue_with_category)
        
        return priority_issues
    
    def get_all_recommendations(self) -> list:
        """Collect all recommendations from analyzers"""
        recommendations = []
        
        for category, data in self.results.items():
            if 'recommendations' not in data:
                continue
            
            for rec in data['recommendations']:
                recommendations.append({
                    'category': category,
                    'recommendation': rec,
                    'score': data.get('score', 100)
                })
        
        # Sort by score (lowest first - most urgent)
        recommendations.sort(key=lambda x: x['score'])
        
        return recommendations
    
    def get_summary(self) -> dict:
        """Generate summary statistics"""
        priority_issues = self.get_priority_issues()
        
        return {
            'overall_score': self.calculate_overall_score(),
            'total_issues': sum(len(issues) for issues in priority_issues.values()),
            'high_priority': len(priority_issues['high']),
            'medium_priority': len(priority_issues['medium']),
            'low_priority': len(priority_issues['low']),
            'categories_analyzed': len(self.results),
            'category_scores': {
                category: data.get('score', 0) 
                for category, data in self.results.items()
            }
        }
    
    def get_grade(self, score: int = None) -> str:
        """Convert score to letter grade"""
        if score is None:
            score = self.calculate_overall_score()
        
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def get_score_color(self, score: int = None) -> str:
        """Get color class based on score"""
        if score is None:
            score = self.calculate_overall_score()
        
        if score >= 80:
            return 'green'
        elif score >= 60:
            return 'yellow'
        else:
            return 'red'
