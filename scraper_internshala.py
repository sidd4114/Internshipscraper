
# ============================================
# FILE 2: scraper_internshala.py
# ============================================

import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import config
from utils import get_fast_headless_chrome, generate_cover_message

BASE_URL = "https://internshala.com"


def is_excluded_text(text):
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in config.EXCLUSION_KEYWORDS)


def is_strictly_relevant(title, description):
    combined_text = f"{title} {description}".lower()

    strong_terms = [
        "ai", "artificial intelligence", "machine learning",
        "ml", "deep learning", "data science", "nlp",
        "computer vision", "neural network", "chatgpt", "generative ai"
    ]
    bad_terms = [
        "ambassador", "marketing", "sales", "hr", "manager",
        "internship mela", "content", "writer", "tester"
    ]

    if any(bad in combined_text for bad in bad_terms):
        return False
    if is_excluded_text(combined_text):
        return False

    return any(term in combined_text for term in strong_terms)


def scrape_internshala(location="Mumbai", max_pages=2):
    """
    Scrape Internshala using Selenium to bypass DDoS protection.
    Synchronous function - will be run in a thread by the main bot.
    """
    driver = get_fast_headless_chrome()
    all_postings = []
    seen_links = set()
    
    # Focused search terms to reduce requests
    SEARCH_TERMS = ["Machine Learning", "Data Science"]
    
    try:
        print(f"[🔍] Scraping Internshala with Selenium...")
        
        for term in SEARCH_TERMS:
            for page in range(1, max_pages + 1):
                try:
                    url = f"{BASE_URL}/internships/keywords/{term.replace(' ', '%20')}/page-{page}"
                    driver.get(url)
                    
                    # Wait for content to load
                    time.sleep(3)
                    
                    # Parse the page
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    cards = soup.find_all("div", class_="individual_internship")
                    
                    if not cards:
                        print(f"   No results for '{term}' page {page}")
                        break
                    
                    for card in cards:
                        try:
                            title_tag = card.find("a", class_="job-title-href")
                            if not title_tag:
                                continue
                                
                            title = title_tag.text.strip()
                            link = BASE_URL + title_tag.get('href', '')
                            
                            if link in seen_links or not title:
                                continue
                            seen_links.add(link)
                            
                            company_tag = card.find("p", class_="company-name")
                            company = company_tag.text.strip() if company_tag else "Unknown"
                            
                            # Get location
                            loc_icon = card.find("i", class_="ic-16-map-pin")
                            location_text = "Remote"
                            if loc_icon:
                                loc_span = loc_icon.find_next_sibling("span")
                                if loc_span:
                                    location_text = loc_span.text.strip()
                            
                            # Get stipend
                            money_icon = card.find("i", class_="ic-16-money")
                            stipend = "Not disclosed"
                            if money_icon:
                                stipend_span = money_icon.find_next_sibling("span")
                                if stipend_span:
                                    stipend = stipend_span.text.strip()
                            
                            # Get duration
                            cal_icon = card.find("i", class_="ic-16-calendar")
                            duration = "Not specified"
                            if cal_icon:
                                duration_span = cal_icon.find_next_sibling("span")
                                if duration_span:
                                    duration = duration_span.text.strip()
                            
                            # Get description
                            desc_tag = card.find("div", class_="about_job")
                            desc = " ".join(desc_tag.stripped_strings).lower() if desc_tag else ""
                            
                            # Get skills
                            skills = [s.text.strip() for s in card.find_all("div", class_="job_skill")]
                            
                            # Filter relevance
                            if not is_strictly_relevant(title, desc):
                                continue
                            
                            all_postings.append({
                                "Company": company,
                                "Role": title,
                                "Platform": "Internshala",
                                "Link": link,
                                "Stipend": stipend,
                                "Duration": duration,
                                "CoverMessage": generate_cover_message(company, title),
                                "Mode": "Online",
                                "Location": location_text,
                                "Skills": skills
                            })
                            
                        except Exception:
                            continue  # Skip problematic cards
                    
                    print(f"   ✓ '{term}' page {page}: {len(all_postings)} total")
                    time.sleep(2)  # Polite delay between pages
                    
                except Exception as e:
                    print(f"   ⚠️ Error on '{term}' page {page}: {e}")
                    break
        
        print(f"[✅] Internshala: {len(all_postings)} internships collected")
        
    except Exception as e:
        print(f"[❌] Internshala error: {e}")
        
    finally:
        driver.quit()
    
    return all_postings


if __name__ == "__main__":
    data = scrape_internshala()
    print(f"\nTotal: {len(data)} internships\n")
    for i, job in enumerate(data[:10], 1):
        print(f"{i}. {job['Role']} at {job['Company']}")
        print(f"   {job['Stipend']} | {job['Duration']} | {job['Location']}")
        print(f"   {job['Link']}\n")
