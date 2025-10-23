import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils import get_fast_headless_chrome, generate_cover_message
import config

def is_relevant_text(text):
    """Check if text contains AI/ML keywords."""
    text_lower = text.lower()
    score = 0
    for kw in config.RELEVANT_KEYWORDS + config.SHORT_KEYWORDS:
        if kw.lower() in text_lower:
            score += 1
    return score > 0

def is_excluded_text(text):
    """Check if text contains exclusion keywords."""
    text_lower = text.lower()
    for kw in config.EXCLUSION_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False

def is_strictly_relevant(title, description):
    """More precise filtering logic for AI/ML relevance."""
    title_lower = title.lower()
    desc_lower = description.lower()

    strong_terms = [
        "ai", "machine learning", "artificial intelligence",
        "deep learning", "data science", "ml", "nlp", "computer vision", "neural network"
    ]
    if not any(term in title_lower for term in strong_terms):
        return False

    bad_terms = [
        "ambassador", "representative", "marketing", "content",
        "writer", "business analyst", "qa", "tester", "sales",
        "recruiter", "hr", "manager", "graphic", "design", "internship mela"
    ]
    if any(bad in title_lower or bad in desc_lower for bad in bad_terms):
        return False

    if is_excluded_text(title) or is_excluded_text(desc_lower):
        return False

    return True

def scrape_unstop(is_offline=False):
    """Scrape Unstop internships with online/offline mode."""
    driver = get_fast_headless_chrome()
    postings = []
    seen_links = set()

    SEARCH_TERMS = [
        "AI", "Machine Learning", "Artificial Intelligence",
        "Deep Learning", "Data Science", "NLP",
        "Computer Vision", "Data Analyst", "Data Engineer", "PyTorch"
    ]

    location_param = "Mumbai" if is_offline else ""

    try:
        print(f"[🔍] Scraping Unstop with {len(SEARCH_TERMS)} search terms...")
        base_url = f"https://unstop.com/internships?oppstatus=open&a=2&quickApply=true&usertype=students&passingOutYear=2027"
        if location_param:
            base_url += f"&location={location_param.replace(' ', '%20')}"

        driver.get(base_url)
        time.sleep(6)

        for term in SEARCH_TERMS:
            print(f"   🔸 Searching for '{term}' internships...")

            try:
                search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Search']")
                search_input.clear()
                search_input.send_keys(term)
                time.sleep(1)
                search_input.send_keys(Keys.ENTER)
                time.sleep(5)
            except Exception:
                print(f"      ⚠️ Search bar not found for term '{term}', skipping...")
                continue

            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            cards = driver.find_elements(By.CSS_SELECTOR, "div.cursor-pointer.single_profile")
            print(f"      ➤ Found {len(cards)} cards for '{term}'")

            for card in cards:
                try:
                    title_el = card.find_element(By.CSS_SELECTOR, "div.opp-title h2")
                    title = title_el.text.strip() if title_el else ""
                    if not title:
                        continue

                    try:
                        company = card.find_element(By.CSS_SELECTOR, "p").text.strip()
                    except:
                        company = "Unknown Company"

                    desc = card.text

                    if not is_strictly_relevant(title, desc):
                        continue

                    card_id = card.get_attribute("id")
                    if card_id and "_" in card_id:
                        numeric_id = card_id.split("_")[1]
                        link = f"https://unstop.com/internships/{numeric_id}"
                    else:
                        continue

                    if link in seen_links:
                        continue
                    seen_links.add(link)

                    try:
                        deadline = card.find_element(By.CSS_SELECTOR, "div.seperate_box span").text.strip()
                    except:
                        deadline = "Not specified"

                    cover_msg = generate_cover_message(company, title)

                    postings.append({
                        "Company": company,
                        "Role": title,
                        "Platform": "Unstop",
                        "Link": link,
                        "DaysLeft": deadline,
                        "CoverMessage": cover_msg,
                        "Mode": "Offline" if is_offline else "Online"
                    })

                    # Show found internship
                    print(f"         🆕 FOUND: {company} - {title} ({link}) [{postings[-1]['Mode']}]")

                except Exception:
                    continue

            print(f"      ✅ Added {len(postings)} total so far\n")

        print(f"[✅] Finished scraping Unstop: {len(postings)} highly relevant internships collected ✅")

    except Exception as e:
        print(f"[❌] Unstop error: {e}")

    finally:
        driver.quit()

    return postings
