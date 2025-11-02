from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote_plus
from typing import List, Dict
import time

# Search queries as requested
SEARCH_QUERIES = [
    '"Energy Analyst" AND (Python OR "Power BI")',
    '"Green Hydrogen" AND (Analyst OR Research)',
    '"Renewable Energy" AND (Research OR Analyst)',
    '"Energy Data Analyst"',
    '"GIS Analyst" AND ("Energy" OR "Renewables")',
    '"Nuclear Energy Analyst" OR "Nuclear Policy"',
    '"Energy Policy Analyst"',
    '"Techno-Economic Analysis" "Renewable Energy"'
]

app = FastAPI(title="LinkedIn Job Scraper (India)")

def build_linkedin_search_url(query: str) -> str:
    """
    Build a LinkedIn job search URL scoped to India.
    """
    base = "https://www.linkedin.com/jobs/search/"
    # Encode the query
    encoded = quote_plus(query)
    # location set to India, basic params to show first page results
    return f"{base}?keywords={encoded}&location=India&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"

def init_chrome_driver() -> webdriver.Chrome:
    """
    Initialize a headless Chrome WebDriver using webdriver-manager.
    """
    options = Options()
    # Headless mode
    options.add_argument("--headless")
    # Recommended options for running in headless/container environments
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,1024")
    # Optional: avoid detection (not guaranteed)
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_linkedin_jobs(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Scrape top job results for a given query from LinkedIn (India).
    Returns a list of dicts: {"title": ..., "company": ..., "url": ...}
    """
    url = build_linkedin_search_url(query)
    driver = None
    results: List[Dict[str, str]] = []
    try:
        driver = init_chrome_driver()
        driver.get(url)

        # Wait for job titles to appear (LinkedIn DOM may vary; we wait for a known class)
        wait = WebDriverWait(driver, 10)
        # Wait for at least one title element to be present
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "base-search-card__title")))

        # Collect elements
        title_elements = driver.find_elements(By.CLASS_NAME, "base-search-card__title")
        company_elements = driver.find_elements(By.CLASS_NAME, "base-search-card__subtitle")
        link_elements = driver.find_elements(By.CLASS_NAME, "base-card__full-link")

        # Some pages may have different counts; iterate up to min length
        count = min(len(title_elements), len(company_elements), len(link_elements), max_results)

        for i in range(count):
            try:
                title = title_elements[i].text.strip()
                company = company_elements[i].text.strip()
                job_url = link_elements[i].get_attribute("href")
                if not job_url:
                    # fallback: maybe link is within an <a> inside the title element
                    anchor = title_elements[i].find_element(By.XPATH, ".//ancestor::a[1]")
                    job_url = anchor.get_attribute("href") if anchor is not None else ""
                results.append({"title": title, "company": company, "url": job_url})
            except Exception:
                # Skip any problematic entry but continue
                continue

    except Exception:
        # If the DOM classes are different or page blocked, return whatever collected so far (possibly empty)
        pass
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return results

@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse(
        """
        <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>LinkedIn Job Scraper</title>
            </head>
            <body style="font-family:Arial,Helvetica,sans-serif; padding:1rem;">
                <h1>LinkedIn Job Scraper (India)</h1>
                <p>Use <a href="/jobs">/jobs</a> to run the scraper and view job cards.</p>
            </body>
        </html>
        """
    )

@app.get("/jobs", response_class=HTMLResponse)
def get_jobs():
    all_jobs: List[Dict[str, str]] = []
    seen_urls = set()

    # Loop through search queries and collect results
    for query in SEARCH_QUERIES:
        # Scrape top 10 results for this query
        scraped = scrape_linkedin_jobs(query, max_results=10)
        for job in scraped:
            url = job.get("url") or ""
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_jobs.append(job)
        # be polite/avoid too-rapid queries
        time.sleep(1)

    # Build mobile-friendly HTML with simple responsive cards
    html_parts = [
        "<!doctype html>",
        "<html>",
        "<head>",
        "  <meta name='viewport' content='width=device-width, initial-scale=1'/>",
        "  <title>LinkedIn Jobs (India)</title>",
        "  <style>",
        "    body{font-family:Arial,Helvetica,sans-serif; margin:0; padding:1rem; background:#f5f7fa}",
        "    .container{max-width:900px;margin:0 auto}",
        "    .header{display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem}",
        "    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem}",
        "    .card{background:#fff;padding:1rem;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1)}",
        "    .title{font-size:1rem;font-weight:700;margin:0 0 0.5rem 0}",
        "    .company{color:#555;margin:0 0 0.75rem 0}",
        "    .link{display:inline-block;padding:0.4rem 0.6rem;background:#0a66c2;color:#fff;border-radius:6px;text-decoration:none;font-size:0.9rem}",
        "    @media (max-width:420px){ .title{font-size:0.95rem} }",
        "  </style>",
        "</head>",
        "<body>",
        "  <div class='container'>",
        "    <div class='header'>",
        "      <h2>LinkedIn Jobs (India) — Unique Results</h2>",
        f"      <div>{len(all_jobs)} jobs</div>",
        "    </div>",
        "    <div class='grid'>"
    ]

    if not all_jobs:
        html_parts.append("<div class='card'><p>No jobs found or LinkedIn blocked the request. Try again later.</p></div>")
    else:
        for job in all_jobs:
            title = job.get("title", "No title")
            company = job.get("company", "No company")
            url = job.get("url", "#")
            card_html = (
                "<div class='card'>"
                f"<div class='title'>{title}</div>"
                f"<div class='company'>{company}</div>"
                f"<a class='link' href='{url}' target='_blank' rel='noopener noreferrer'>View on LinkedIn</a>"
                "</div>"
            )
            html_parts.append(card_html)

    html_parts.extend([
        "    </div>",
        "    <footer style='margin-top:1rem;color:#666;font-size:0.9rem'>",
        "      <p>Scraped with Selenium (webdriver-manager). Results de-duplicated by job URL.</p>",
        "    </footer>",
        "  </div>",
        "</body>",
        "</html>"
    ])

    return HTMLResponse("\n".join(html_parts))


if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)
