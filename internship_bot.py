# ============================================
# FILE 1: internship_bot.py
# ============================================

import os
import time
import asyncio
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

import config
from utils import (
    load_existing_data, save_data, generate_cover_message,
    send_desktop_alert
)
from scraper_linkedin import scrape_linkedin
from scraper_unstop import scrape_unstop
from scraper_internshala import scrape_internshala
from reddit_scam_check import check_scam_comments


async def process_job(job, df_existing):
    """Process a single job: check for duplicates and scan Reddit asynchronously"""
    # Check for duplicates (compare by Link for more accuracy)
    existing = df_existing[df_existing['Link'] == job['Link']]
    
    if not existing.empty:
        # Job already exists - skip silently
        return None

    # Add metadata
    job['PostingDate'] = datetime.now().strftime("%Y-%m-%d")
    job['Deadline'] = job.get('DaysLeft', '')
    job['Status'] = "New"
    
    # Generate cover message if not already present
    if 'CoverMessage' not in job or not job['CoverMessage']:
        job['CoverMessage'] = generate_cover_message(job['Company'], job['Role'])

    # ✅ Async Reddit scam detection
    print(f"[🔍] {job['Company'][:40]:40}", end=" ", flush=True)
    try:
        flags = await check_scam_comments(job['Company'])
        if flags:
            job['ScamStatus'] = "⚠️ Scam Suspected"
            job['ScamFlags'] = flags
            print(f"🚨 {len(flags)} FLAGS!")
        else:
            job['ScamStatus'] = "✅ Clean"
            job['ScamFlags'] = []
            print("✅")
    except Exception as e:
        job['ScamStatus'] = "❓ Unknown"
        job['ScamFlags'] = []
        print(f"⚠️ Error")

    return job


async def run_scrapers_concurrently():
    """Run all scrapers concurrently using thread pool for sync scrapers"""
    tasks = []
    
    # Create a thread pool for blocking scrapers
    executor = ThreadPoolExecutor(max_workers=3)
    loop = asyncio.get_event_loop()
    
    # LinkedIn (sync - run in thread)
    if config.ENABLE_LINKEDIN:
        tasks.append(
            loop.run_in_executor(executor, scrape_linkedin, config.LOCATION)
        )
    
    # Unstop (sync - run in thread)
    if config.ENABLE_UNSTOP:
        tasks.append(
            loop.run_in_executor(executor, scrape_unstop)
        )
    
    # Internshala (sync - run in thread)
    if config.ENABLE_INTERNSHALA:
        tasks.append(
            loop.run_in_executor(executor, scrape_internshala, config.LOCATION)
        )
    
    # Wait for all scrapers to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Clean up executor
    executor.shutdown(wait=False)
    
    return results


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
            print("[📡] Starting scrapers...")
            results = await run_scrapers_concurrently()

            # Flatten results & filter valid ones
            new_postings = []
            for i, r in enumerate(results):
                if isinstance(r, Exception):
                    print(f"[❌] Scraper {i} failed: {r}")
                elif isinstance(r, list):
                    new_postings.extend(r)
                    print(f"[✅] Scraper {i} returned {len(r)} postings")

            print(f"\n[📊] Total new postings collected: {len(new_postings)}")

            # --- Process all jobs concurrently with Reddit checks ---
            if new_postings:
                print(f"\n[🤖] Processing {len(new_postings)} jobs with Reddit scam detection...")
                print(f"[⏳] Estimated time: ~{len(new_postings) * 3}s\n")
                
                processed_jobs = await asyncio.gather(
                    *(process_job(job, df_existing) for job in new_postings),
                    return_exceptions=True
                )
                
                print()  # Blank line after all checks
                
                # Filter out None and exceptions
                alerts = []
                for job in processed_jobs:
                    if isinstance(job, Exception):
                        print(f"[⚠️] Job processing error: {job}")
                    elif job is not None:
                        alerts.append(job)
                        # Add to dataframe
                        df_existing = pd.concat([df_existing, pd.DataFrame([job])], ignore_index=True)
            else:
                alerts = []

            # Save updated data
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

Scam Status: {alert['ScamStatus']}
"""

                if alert.get('ScamFlags'):
                    body += "\n⚠️ SCAM ALERTS FOUND:\n"
                    for f in alert['ScamFlags'][:3]:  # Show first 3 flags
                        body += f"- [{f['type'].capitalize()}] {f['reason']}\n"
                        body += f"  r/{f['subreddit']}: {f['link']}\n"

                send_desktop_alert(
                    f"New Internship: {alert['Company']}",
                    f"{alert['Role']} - {alert['ScamStatus']}"
                )

            # Summary
            elapsed = time.time() - start_time
            scam_count = sum(1 for a in alerts if 'Suspected' in a.get('ScamStatus', ''))
            
            print(f"\n[📈] CYCLE SUMMARY:")
            print(f"   - New internships found: {len(alerts)}")
            print(f"   - Total tracked: {len(df_existing)}")
            print(f"   - Scam alerts: {scam_count}")
            print(f"   - Time elapsed: {elapsed:.1f}s")
            print(f"[⏰] Next check in {config.POLL_INTERVAL//60} minutes...")

            retry_count = 0
            await asyncio.sleep(config.POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\n[👋] Stopped by user")
            break
        except Exception as e:
            retry_count += 1
            print(f"\n[❌] Critical error: {e}")
            import traceback
            traceback.print_exc()
            
            wait = min(60 * retry_count, config.POLL_INTERVAL)
            print(f"[⏳] Waiting {wait}s before retry (attempt {retry_count})...")
            await asyncio.sleep(wait)


if __name__ == "__main__":
    print("="*70)
    print("🤖 AI/ML INTERNSHIP MONITOR BOT WITH REDDIT SCAM DETECTION")
    print("="*70)
    print(f"📍 Location: {config.LOCATION}")
    print(f"⏱️  Interval: {config.POLL_INTERVAL//60} minutes")
    print(f"💾 File: {config.CSV_FILE}")
    print(f"🎯 LinkedIn: {'✓' if config.ENABLE_LINKEDIN else '✗'}")
    print(f"🎯 Unstop: {'✓' if config.ENABLE_UNSTOP else '✗'}")
    print(f"🎯 Internshala: {'✓' if config.ENABLE_INTERNSHALA else '✗'}")
    print(f"🛡️  Reddit Scam Check: ✓")
    print("="*70)
    print("\n⚡ Starting bot in async mode...\n")

    try:
        asyncio.run(monitor_internships())
    except KeyboardInterrupt:
        print("\n[👋] Bot stopped gracefully")