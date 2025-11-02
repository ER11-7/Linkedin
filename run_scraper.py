import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- Your Personalized Job Search Keywords ---
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

LOCATION_FILTER = "India"
BASE_URL = "https://www.linkedin.com/jobs/search/"

def get_jobs_from_linkedin(query: str):
    """
    Scrapes LinkedIn for a specific job query.
    """
    print(f"\n" + "="*40)
    print(f"--- Scraping for: {query} ---")
    print("="*40)
    job_list = []
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)
    
    search_url = f"{BASE_URL}?keywords={query.replace(' ', '%20')}&location={LOCATION_FILTER}"
    
    try:
        driver.get(search_url)
        time.sleep(5) 

        job_elements = driver.find_elements(By.CLASS_NAME, "base-card")
        
        for job in job_elements[:10]: # Get top 10
            try:
                title = job.find_element(By.CLASS_NAME, "base-search-card__title").text
                company = job.find_element(By.CLASS_NAME, "base-search-card__subtitle").text
                link = job.find_element(By.CLASS_NAME, "base-card__full-link").get_attribute("href")
                
                job_list.append({
                    "title": title,
                    "company": company,
                    "link": link
                })
            except Exception:
                continue
                
    except Exception as e:
        print(f"Error while scraping {query}: {e}")
    finally:
        driver.quit()
        
    return job_list

def run_scraper():
    """
    Main function to run the scraper for all queries and print results.
    """
    print("Starting daily job scrape...")
    all_jobs = []
    unique_links = set()

    for query in SEARCH_QUERIES:
        jobs = get_jobs_from_linkedin(query)
        new_jobs_found = 0
        for job in jobs:
            if job['link'] not in unique_links:
                all_jobs.append(job)
                unique_links.add(job['link'])
                new_jobs_found += 1
                
                # --- Print the job details to the log ---
                print(f"\nTitle:    {job['title']}")
                print(f"Company:  {job['company']}")
                print(f"Link:     {job['link']}")
        
        if new_jobs_found == 0:
            print("...No new jobs found for this query.")
            
    print(f"\n" + "="*40)
    print(f"Scrape Complete. Found {len(all_jobs)} total unique jobs.")
    print("="*40)

if __name__ == "__main__":
    run_scraper()
