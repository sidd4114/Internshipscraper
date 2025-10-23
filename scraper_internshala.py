# scraper_internshala_async.py

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import config
from utils import generate_cover_message

BASE_URL = "https://internshala.com"
SEARCH_URL = BASE_URL + "/internships/keywords/{}"

HEADERS = {"User-Agent": "Mozilla/5.0"}


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


async def fetch_page(session, url):
    async with session.get(url, headers=HEADERS) as response:
        if response.status != 200:
            print(f"⚠️ Failed to fetch {url} (status {response.status})")
            return None
        return await response.text()


async def parse_internships(html):
    postings = []
    seen_links = set()
    if not html:
        return postings

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", class_="individual_internship")
    for card in cards:
        try:
            title_tag = card.find("a", class_="job-title-href")
            title = title_tag.text.strip() if title_tag else ""
            link = BASE_URL + title_tag['href'] if title_tag else "N/A"

            if link in seen_links or not title:
                continue
            seen_links.add(link)

            company_tag = card.find("p", class_="company-name")
            company = company_tag.text.strip() if company_tag else "Unknown Company"

            loc_icon = card.find("i", class_="ic-16-map-pin")
            location = loc_icon.find_next_sibling("span").text.strip() if loc_icon else "N/A"

            money_icon = card.find("i", class_="ic-16-money")
            stipend = money_icon.find_next_sibling("span").text.strip() if money_icon else "N/A"

            cal_icon = card.find("i", class_="ic-16-calendar")
            duration = cal_icon.find_next_sibling("span").text.strip() if cal_icon else "N/A"

            desc_tag = card.find("div", class_="about_job")
            desc = " ".join(desc_tag.stripped_strings).lower() if desc_tag else ""

            skills = [s.text.strip() for s in card.find_all("div", class_="job_skill")]

            if not is_strictly_relevant(title, desc):
                continue

            cover_msg = generate_cover_message(company, title)

            postings.append({
                "Company": company,
                "Role": title,
                "Platform": "Internshala",
                "Link": link,
                "Stipend": stipend,
                "Duration": duration,
                "CoverMessage": cover_msg,
                "Mode": "Online",
                "Location": location,
                "Skills": skills
            })
        except Exception as e:
            print(f"⚠️ Skipping a card due to error: {e}")
    return postings


async def scrape_internshala(is_offline=False, max_pages=5):
    SEARCH_TERMS = [
        "AI", "Machine Learning", "Artificial Intelligence",
        "Deep Learning", "Data Science", "NLP",
        "Computer Vision", "Data Analyst", "Data Engineer", "PyTorch"
    ]
    all_postings = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for term in SEARCH_TERMS:
            for page in range(1, max_pages + 1):
                url = SEARCH_URL.format(term.replace(" ", "%20")) + f"/page-{page}"
                tasks.append(fetch_page(session, url))

        pages_content = await asyncio.gather(*tasks)

        for html in pages_content:
            postings = await parse_internships(html)
            all_postings.extend(postings)

    print(f"[✅] Finished scraping Internshala: {len(all_postings)} internships collected ✅")
    return all_postings


if __name__ == "__main__":
    import asyncio

    data = asyncio.run(scrape_internshala())
    for i, job in enumerate(data[:20]):
        print(f"{i+1}. {job['Role']} at {job['Company']} ({job['Location']}) - {job['Stipend']}")
        print(f"   Duration: {job['Duration']}")
        print(f"   Link: {job['Link']}")
        print(f"   Skills: {', '.join(job['Skills'])}\n")
