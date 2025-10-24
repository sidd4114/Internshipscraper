# reddit_scam_check.py


import re
import asyncio
import asyncpraw
from typing import List, Dict

# ONLY use subreddits that actually exist and are accessible
WORKING_SUBREDDITS = [
    "Scams",
    "IndiaCareers",
    "LegalAdviceIndia",
    "Advice",
    "jobs"
]

# Scam detection keywords
SCAM_KEYWORDS = [
    "scam", "fraud", "fake", "cheat", "ripoff", "not paid",
    "suspicious", "fake internship", "don't join", "avoid",
    "warning", "beware", "unpaid", "never pay", "red flag"
]


def contains_scam_keyword(text: str, company_name: str) -> str:
    """Check if any scam keyword appears near the company name."""
    if not text:
        return None

    text = text.lower()
    company_name_lower = company_name.lower()
    lines = re.split(r'[.\n]', text)

    for line in lines:
        if company_name_lower in line:
            for kw in SCAM_KEYWORDS:
                if kw in line:
                    return kw
    return None


async def search_single_subreddit(reddit, subreddit_name: str, company_name: str, limit: int = 15) -> List[Dict]:
    """Search a single subreddit for scam mentions."""
    flags = []

    try:
        subreddit = await reddit.subreddit(subreddit_name)
        search_gen = subreddit.search(company_name, limit=limit)

        async for submission in search_gen:
            # Check post title + selftext
            post_text = f"{submission.title} {submission.selftext}"
            kw_found = contains_scam_keyword(post_text, company_name)

            if kw_found:
                flags.append({
                    "type": "post",
                    "subreddit": subreddit_name,
                    "post_title": submission.title[:100],
                    "text": submission.selftext[:200],
                    "reason": f"Keyword '{kw_found}' found",
                    "link": f"https://reddit.com{submission.permalink}"
                })

            # Check top 3 comments only
            try:
                await submission.comments.replace_more(limit=0)
                for comment in submission.comments.list()[:3]:
                    kw_found = contains_scam_keyword(comment.body, company_name)
                    if kw_found:
                        flags.append({
                            "type": "comment",
                            "subreddit": subreddit_name,
                            "post_title": submission.title[:100],
                            "text": comment.body[:200],
                            "reason": f"Keyword '{kw_found}' found",
                            "link": f"https://reddit.com{comment.permalink}"
                        })
            except:
                pass

    except Exception as e:
        if "404" not in str(e) and "403" not in str(e):
            pass  # Silent failure

    return flags


async def check_scam_comments(company_name: str, subreddits: List[str] = None, limit: int = 15) -> List[Dict]:
    """
    Asynchronously scan multiple subreddits for scam reports.
    Searches ALL subreddits concurrently for speed.
    """
    if subreddits is None:
        subreddits = WORKING_SUBREDDITS

    # Create Reddit client
    reddit = asyncpraw.Reddit(
        client_id="OMPlBPoltQK0v5O1NuhpOA",
        client_secret="7rsKEI2U0lqvitOsTa5I8UTfdmSrNQ",
        user_agent="InternshipScraperBot by /u/LongjumpingDay729",
        timeout=15
    )

    try:
        # 🚀 Search ALL subreddits concurrently
        tasks = [
            search_single_subreddit(reddit, sub, company_name, limit)
            for sub in subreddits
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten results
        all_flags = []
        for result in results:
            if isinstance(result, list):
                all_flags.extend(result)

    finally:
        await reddit.close()

    return all_flags


# --- Quick Test ---
if __name__ == "__main__":
    async def main():
        test_companies = ["Propgrowthx Pvt. Ltd.", "Google"]

        for company in test_companies:
            print(f"\n{'='*60}")
            print(f"Testing: {company}")
            print('='*60)

            flags = await check_scam_comments(company, limit=10)

            if flags:
                print(f"\n🚨 Found {len(flags)} flags:")
                for i, f in enumerate(flags[:3], 1):
                    print(f"\n{i}. [{f['type'].upper()}] r/{f['subreddit']}")
                    print(f"   {f['reason']}")
                    print(f"   {f['link']}")
            else:
                print(f"✅ No scam flags found")

            await asyncio.sleep(1)

    asyncio.run(main())