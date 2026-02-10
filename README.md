# 🔍 SEO Audit Tool — Mini SaaS

> Full-Stack On-Page SEO Analyzer — Analyze any webpage and get detailed SEO recommendations

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Features (23 Total)

### Core Analysis (8)
| Category | Checks |
|----------|--------|
| **Title Tag** | Length, keywords, uniqueness, power words |
| **Meta Description** | Length, CTA presence, OG tags |
| **URL Structure** | HTTPS, length, special chars, clean URLs |
| **Headings** | H1-H6 hierarchy, multiple H1 detection |
| **Content** | Word count, readability score, keyword density |
| **Images** | Alt text, dimensions, filenames, formats |
| **Links** | Internal/external balance, anchor text |
| **Performance** | Response time, scripts, render-blocking |

### Extended Analysis (8)
| Category | Checks |
|----------|--------|
| **Keyword Density** | Top keywords, target keyword placement, density % |
| **Social Media Preview** | Facebook OG, Twitter Card, LinkedIn preview |
| **Mobile-Friendly** | Viewport, text size, tap targets, responsive design |
| **Schema Markup** | JSON-LD, Microdata, RDFa validation |
| **Broken Link Checker** | HTTP status of all page links (parallel) |
| **SSL/Security** | HTTPS, security headers (HSTS, CSP, X-Frame) |
| **Sitemap & Robots** | sitemap.xml + robots.txt presence & validity |
| **Core Web Vitals** | LCP, CLS, INP estimation from page structure |

### Advanced Features (7)
| Feature | Description |
|---------|-------------|
| **i18n Checker** | Language, charset, hreflang tags, text direction |
| **Readability Score** | Flesch Reading Ease, Kincaid Grade, Gunning Fog |
| **Competitor Comparison** | Side-by-side SEO score comparison |
| **SEO Score History** | SQLite-backed scan history with trend charts |
| **Page Screenshot** | Capture page screenshot via API |
| **SERP Preview** | Editable Google search result simulator |
| **Export Reports** | Download as PDF or JSON |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
git clone https://github.com/Hemnathhemu19/SEO-Audit-Tool---Full-Stack-Project.git
cd SEO-Audit-Tool---Full-Stack-Project
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser.

## 📖 Usage

1. Enter any URL in the input field
2. (Optional) Add a target keyword
3. Click **"Analyze Now"**
4. View your SEO score and detailed breakdown
5. Export report as PDF or JSON
6. Check the **History** page for past scans

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze` | Full SEO analysis |
| `POST` | `/api/compare` | Compare two URLs |
| `POST` | `/api/screenshot` | Capture page screenshot |
| `GET` | `/api/history` | Scan history |
| `GET` | `/api/history/trend?url=` | Score trend for a URL |
| `POST` | `/api/quick-check` | URL validation |
| `GET` | `/api/health` | Health check |

### Example Request

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "keyword": "seo"}'
```

## 📁 Project Structure

```
seo-audit-tool/
├── app.py                          # Flask API server
├── requirements.txt                # Dependencies
├── analyzers/                      # 14 analysis modules
│   ├── title_analyzer.py           # Title tag analysis
│   ├── meta_analyzer.py            # Meta description
│   ├── url_analyzer.py             # URL structure
│   ├── heading_analyzer.py         # Heading hierarchy
│   ├── content_analyzer.py         # Content quality
│   ├── image_analyzer.py           # Image optimization
│   ├── link_analyzer.py            # Link analysis
│   ├── speed_analyzer.py           # Performance
│   ├── keyword_analyzer.py         # Keyword density
│   ├── social_analyzer.py          # Social media preview
│   ├── mobile_analyzer.py          # Mobile friendliness
│   ├── schema_analyzer.py          # Schema markup
│   ├── link_checker.py             # Broken link checker
│   ├── security_analyzer.py        # SSL/security
│   ├── sitemap_analyzer.py         # Sitemap & robots
│   ├── vitals_analyzer.py          # Core Web Vitals
│   ├── i18n_analyzer.py            # Internationalization
│   ├── readability_analyzer.py     # Readability scores
│   └── seo_scorer.py               # Overall scoring
├── utils/
│   ├── crawler.py                  # Web page fetcher
│   └── history_manager.py          # SQLite history
├── static/
│   ├── index.html                  # Frontend dashboard
│   ├── css/style.css               # Styles
│   └── js/
│       ├── app.js                  # Main application
│       ├── charts.js               # Chart.js charts
│       └── pdf-export.js           # PDF export
└── tests/
    └── test_analyzers.py           # Unit tests
```

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
python -m pytest tests/ -v --cov=analyzers
```

## 🛠️ Technologies

- **Backend:** Python, Flask, BeautifulSoup4, SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **Charts:** Chart.js
- **PDF Export:** jsPDF

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

**Made by [Hemnath]** | [Portfolio](https://hemus.in)
