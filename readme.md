```markdown
# LinkedIn Job Scraper (FastAPI + Selenium)

This is a simple FastAPI application that scrapes LinkedIn job listings (scoped to India) for a fixed set of search queries using Selenium and webdriver-manager.

Features:
- Uses Selenium with webdriver-manager to automatically install/manage ChromeDriver.
- Runs Chrome in headless mode.
- Scrapes the top 10 results for each query from LinkedIn and returns a single HTML page with unique job cards.
- FastAPI endpoints:
  - GET / : Welcome page
  - GET /jobs : Runs the scraper for all queries and returns mobile-friendly job cards

Search queries (inside main.py):
- "Energy Analyst" AND (Python OR "Power BI")
- "Green Hydrogen" AND (Analyst OR Research)
- "Renewable Energy" AND (Research OR Analyst)
- "Energy Data Analyst"
- "GIS Analyst" AND ("Energy" OR "Renewables")
- "Nuclear Energy Analyst" OR "Nuclear Policy"
- "Energy Policy Analyst"
- "Techno-Economic Analysis" "Renewable Energy"

Requirements:
- Python 3.8+
- Google Chrome installed on the machine where the app runs.

Install:
1. Create and activate a virtual environment.
2. pip install -r requirements.txt

Run:
python main.py

Then open http://localhost:8000/jobs

Notes and caveats:
- LinkedIn has bot detection and rate limiting. This simple scraper may be blocked or require authentication for full results.
- The HTML structure of LinkedIn may change; the scraper uses class names such as `base-search-card__title`, `base-search-card__subtitle`, and `base-card__full-link` as requested. If scraping returns no results, review and update selectors or add authentication/cookies.
```
