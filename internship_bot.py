# internship_bot_async_full.py

import os
import time
import asyncio
from datetime import datetime
import pandas as pd

import config
from utils import (
    load_existing_data, save_data, generate_cover_message,
    send_desktop_alert
)
from scraper_linkedin import scrape_linkedin
from scraper_unstop import scrape_unstop
from scraper_internshala import scrape_internshala  # ✅ async scraper
from reddit_scam_check_async import check_scam_comments  # ✅ async version


async def process_job(job, df_existing):
    """Process a single job: check for duplicates and scan Reddit asynchronously"""
    existing = df_existing[
        (df_existing['Company'] == job['Company']) &
        (df_existing['Role'] == job['Role'])
    ]
    if not existing.empty:
        return None

    job['PostingDate'] = datetime.now().strftime("%Y-%m-%d")
    job['Deadline'] = job.get('DaysLeft', '')
    job['Status'] = "New"
    job['CoverMessage'] = generate_cover_message(job['Company'], job['Role'])

    # Async Reddit scam detection
    flags = await check_scam_comments(job['Company'])
    if flags:
        job['ScamStatus'] = "Scam Suspected"
        job['ScamFlags'] = flags
    else:
        job['ScamStatus'] = "Not Sure"
        job['ScamFlags'] = []

    df_existing = pd.concat([df_existing, pd.DataFrame([job])], ignore_index=True)
    print(f"[🆕] NEW: {job['Company']} - {job['Role']} - Scam: {job['ScamStatus']}")
    return job


async def monitor_internships():
    """Main async monitoring loop with fully async Reddit checks"""
    retry_count = 0
    cycle_count = 0

    while True:
        try:
            cycle_count += 1
            print("\n" + "="*70)
            print(f"[🔄 CYCLE #{cycle_count}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*70)

            start_time = time.time()
            df_existing = load_existing_data()

            # --- Run all scrapers concurrently ---
            tasks = []
            if config.ENABLE_LINKEDIN:
                tasks.append(asyncio.to_thread(scrape_linkedin, config.LOCATION))
            if config.ENABLE_UNSTOP:
                tasks.append(asyncio.to_thread(scrape_unstop))
            if config.ENABLE_INTERNSHALA:
                tasks.append(scrape_internshala(config.LOCATION))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Flatten results & filter valid ones
            new_postings = []
            for r in results:
                if isinstance(r, list):
                    new_postings.extend(r)

            # --- Process all jobs concurrently ---
            processed_jobs = await asyncio.gather(
                *(process_job(job, df_existing) for job in new_postings)
            )
            alerts = [job for job in processed_jobs if job]

            save_data(df_existing)

            # --- Send desktop alerts ---
            for alert in alerts:
                subject = f"🚀 New AI/ML Internship – {alert['Company']}"
                body = f"""Role: {alert['Role']}
Company: {alert['Company']}
Platform: {alert['Platform']}
Link: {alert['Link']}
Deadline: {alert.get('DaysLeft', 'Not specified')}

{alert['CoverMessage']}
"""

                if alert['ScamFlags']:
                    body += "\n⚠️ Scam Alerts Found:\n"
                    for f in alert['ScamFlags']:
                        body += f"- [{f['type'].capitalize()}] {f['reason']} (Subreddit: r/{f['subreddit']})\n  Link: {f['link']}\n"

                send_desktop_alert(
                    f"New Internship: {alert['Company']}",
                    f"{alert['Role']} - Scam: {alert['ScamStatus']}"
                )

            elapsed = time.time() - start_time
            print(f"\n[📈] SUMMARY:")
            print(f"   - New internships: {len(alerts)}")
            print(f"   - Total tracked: {len(df_existing)}")
            print(f"   - Time: {elapsed:.1f}s")
            print(f"[⏰] Next check in {config.POLL_INTERVAL//60} minutes...")

            retry_count = 0
            await asyncio.sleep(config.POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\n[👋] Stopped by user")
            break
        except Exception as e:
            retry_count += 1
            print(f"\n[❌] Error: {e}")
            wait = 60 * retry_count if retry_count < 3 else config.POLL_INTERVAL
            print(f"[⏳] Waiting {wait}s before retry...")
            await asyncio.sleep(wait)


if __name__ == "__main__":
    print("="*70)
    print("🤖 AI/ML INTERNSHIP MONITOR BOT WITH SCAM DETECTION (FULL ASYNC MODE)")
    print("="*70)
    print(f"📍 Location: {config.LOCATION}")
    print(f"⏱️  Interval: {config.POLL_INTERVAL//60} minutes")
    print(f"💾 File: {config.CSV_FILE}")
    print(f"🎯 LinkedIn: {'✓' if config.ENABLE_LINKEDIN else '✗'}")
    print(f"🎯 Unstop: {'✓' if config.ENABLE_UNSTOP else '✗'}")
    print(f"🎯 Internshala: {'✓' if config.ENABLE_INTERNSHALA else '✗'}")
    print("="*70)

    asyncio.run(monitor_internships())
