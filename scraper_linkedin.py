import time
from selenium.webdriver.common.by import By
from utils import get_fast_headless_chrome, is_relevant

def scrape_linkedin(location="Mumbai"):
    """
    LinkedIn internship scraper
    Currently DISABLED for performance
    """
    print("[⚠] LinkedIn scraping is disabled")
    return []
    
    # Uncomment below to enable LinkedIn scraping
    """
    driver = get_fast_headless_chrome()
    postings = []
    
    try:
        driver.get("https://www.linkedin.com")
        time.sleep(5)
        
        keywords = "Data%20Science%20OR%20Machine%20Learning%20OR%20AI"
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location=India&f_TPR=r2592000&f_JT=I&sortBy=DD"
        driver.get(search_url)
        time.sleep(10)
        
        jobs = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")
        
        for job in jobs:
            try:
                title = job.find_element(By.CSS_SELECTOR, "h3").text.strip()
                company = job.find_element(By.CSS_SELECTOR, "h4").text.strip()
                link = job.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                if is_relevant(title):
                    postings.append({
                        "Company": company,
                        "Role": title,
                        "Platform": "LinkedIn",
                        "Link": link
                    })
            except:
                continue
                
    except Exception as e:
        print(f"[✖] LinkedIn error: {e}")
    finally:
        driver.quit()
    
    print(f"[✔] LinkedIn: {len(postings)} internships")
    return postings
    """
