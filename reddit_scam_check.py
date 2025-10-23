import re
import asyncio
import asyncpraw

# Initialize Async Reddit API
reddit = asyncpraw.Reddit(
    client_id="OMPlBPoltQK0v5O1NuhpOA",
    client_secret="7rsKEI2U0lqvitOsTa5I8UTfdmSrNQ",
    user_agent="InternshipScraperBot by /u/LongjumpingDay729"
)

# Prioritized subreddits
HIGH_PRIORITY = ["Scams", "AntiScam", "IndiaCareers"]
MEDIUM_PRIORITY = ["Fraud", "BadCompanies", "LegalAdviceIndia"]
LOW_PRIORITY = ["Advice", "jobs"]
SUBREDDITS = HIGH_PRIORITY + MEDIUM_PRIORITY + LOW_PRIORITY

# Keywords that indicate a potential scam
SCAM_KEYWORDS = [
    "scam", "fraud", "fake", "cheat", "ripoff",
    "not paid", "suspicious", "fake internship"
]


def contains_scam_keyword(text, company_name):
    """Check if any scam keyword appears near the company name."""
    text = text.lower()
    company_name_lower = company_name.lower()
    lines = re.split(r'[.\n]', text)
    for line in lines:
        if company_name_lower in line:
            for kw in SCAM_KEYWORDS:
                if kw in line:
                    return kw
    return None


async def check_scam_comments(company_name, subreddits=SUBREDDITS, limit=50):
    """Asynchronously scan multiple subreddits for scam reports."""
    flagged_items = []

    for subreddit in subreddits:
        try:
            print(f"[🔍] Searching subreddit: r/{subreddit} for '{company_name}'...")
            async for submission in reddit.subreddit(subreddit).search(company_name, limit=limit):
                # Check post title + selftext
                post_text = f"{submission.title} {submission.selftext}"
                kw_found = contains_scam_keyword(post_text, company_name)
                if kw_found:
                    flagged_items.append({
                        "type": "post",
                        "subreddit": subreddit,
                        "post_title": submission.title,
                        "text": submission.selftext,
                        "reason": f"Contains keyword: {kw_found} near company name",
                        "link": f"https://reddit.com{submission.permalink}"
                    })

                # Check comments
                await submission.comments.replace_more(limit=0)
                for comment in submission.comments.list():
                    kw_found = contains_scam_keyword(comment.body, company_name)
                    if kw_found:
                        flagged_items.append({
                            "type": "comment",
                            "subreddit": subreddit,
                            "post_title": submission.title,
                            "text": comment.body,
                            "reason": f"Contains keyword: {kw_found} near company name",
                            "link": f"https://reddit.com{comment.permalink}"
                        })

        except Exception as e:
            print(f"[⚠️] Error searching subreddit '{subreddit}': {e}")
            continue

    print(f"[✅] Finished scanning Reddit for '{company_name}'. Found {len(flagged_items)} potential flags.\n")
    return flagged_items


# --- Example usage ---
if __name__ == "__main__":
    async def main():
        company = "Propgrowthx Pvt. Ltd."
        flags = await check_scam_comments(company)

        if flags:
            print(f"🚨 Scam flags found for {company} ({len(flags)} items):\n")
            for f in flags:
                print(f"Type: {f['type'].capitalize()}")
                print(f"Subreddit: {f['subreddit']}")
                print(f"Reason: {f['reason']}")
                print(f"Post Title: {f['post_title']}")
                print(f"Content: {f['text']}")
                print(f"Link: {f['link']}\n")
        else:
            print(f"No scam flags found for {company}.")

    asyncio.run(main())
