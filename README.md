# 🔍 SEO Audit Tool

> AI-powered On-Page SEO Analyzer - Analyze any webpage and get detailed SEO recommendations

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Features

- **Comprehensive SEO Analysis** - Analyze 8+ SEO factors
- **Real-time Scoring** - Get instant SEO scores (0-100)
- **Visual Dashboard** - Beautiful dark-themed interface
- **Priority Issues** - Issues categorized by priority
- **Actionable Recommendations** - Step-by-step improvement suggestions
- **Export Reports** - Download PDF or JSON reports
- **Keyword Analysis** - Optional keyword density checking

## 📊 What It Analyzes

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

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/seo-audit-tool.git
   cd seo-audit-tool
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## 📖 Usage

1. Enter any webpage URL in the input field
2. (Optional) Add a target keyword for density analysis
3. Click **"Analyze Now"**
4. View your SEO score and detailed breakdown
5. Export report as PDF or JSON

## 🔌 API Documentation

### Analyze URL

**Endpoint:** `POST /api/analyze`

**Request:**
```json
{
  "url": "https://example.com/blog-post",
  "keyword": "optional target keyword"
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com/blog-post",
  "overall_score": 75,
  "grade": "C",
  "analysis": {
    "title": { "score": 85, "issues": [...] },
    "meta_description": { "score": 80, "issues": [...] },
    ...
  },
  "priority_issues": {
    "high": [...],
    "medium": [...],
    "low": [...]
  },
  "recommendations": [...]
}
```

### Health Check

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "SEO Audit Tool",
  "version": "1.0.0"
}
```

## 📁 Project Structure

```
seo-audit-tool/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── README.md               # Documentation
│
├── analyzers/              # SEO analysis modules
│   ├── __init__.py
│   ├── title_analyzer.py
│   ├── meta_analyzer.py
│   ├── url_analyzer.py
│   ├── heading_analyzer.py
│   ├── content_analyzer.py
│   ├── image_analyzer.py
│   ├── link_analyzer.py
│   ├── speed_analyzer.py
│   └── seo_scorer.py
│
├── utils/                  # Utility modules
│   ├── __init__.py
│   └── crawler.py
│
├── static/                 # Frontend files
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js
│       ├── charts.js
│       └── pdf-export.js
│
└── tests/                  # Test files
    └── test_analyzers.py
```

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=analyzers
```

## 🎨 Screenshots

### Dashboard
- Modern dark theme design
- Real-time score animation
- Category breakdown cards
- Interactive charts

### Analysis Report
- Priority-sorted issues
- Actionable recommendations
- Export to PDF/JSON

## 🛠️ Technologies Used

- **Backend:** Python, Flask, BeautifulSoup4
- **Frontend:** HTML5, CSS3, JavaScript
- **Charts:** Chart.js
- **PDF Export:** jsPDF
- **Readability:** textstat

## 📈 Roadmap

- [ ] Lighthouse integration for Core Web Vitals
- [ ] Competitor comparison feature
- [ ] Scheduled monitoring
- [ ] Email reports
- [ ] AI-powered content suggestions

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Ahrefs, Moz, and Screaming Frog
- Built with ❤️ for better SEO

---

**Made by [Your Name]** | [Portfolio](https://yourportfolio.com) | [LinkedIn](https://linkedin.com/in/yourprofile)
