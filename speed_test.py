#!/usr/bin/env python3
"""
Speed test: Compare sequential vs concurrent Reddit API calls
"""

import asyncio
import time
from reddit_scam_check import check_scam_comments, search_single_subreddit, WORKING_SUBREDDITS
import asyncpraw


# Test companies
TEST_COMPANIES = [
    "Google",
    "Microsoft", 
    "Amazon",
    "Propgrowthx Pvt. Ltd.",
    "TCS"
]


async def test_sequential_checks():
    """Old way: Check each company one at a time"""
    print("\n" + "="*60)
    print("🐌 SEQUENTIAL MODE (Old Way)")
    print("="*60)
    
    start = time.time()
    
    for company in TEST_COMPANIES:
        print(f"Checking {company}...", end=" ")
        flags = await check_scam_comments(company, limit=10)
        print(f"✓ ({len(flags)} flags)")
    
    elapsed = time.time() - start
    print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
    return elapsed


async def test_concurrent_checks():
    """New way: Check all companies at the same time"""
    print("\n" + "="*60)
    print("⚡ CONCURRENT MODE (New Way)")
    print("="*60)
    
    start = time.time()
    
    # Run ALL companies concurrently
    tasks = [
        check_scam_comments(company, limit=10) 
        for company in TEST_COMPANIES
    ]
    
    results = await asyncio.gather(*tasks)
    
    for i, (company, flags) in enumerate(zip(TEST_COMPANIES, results)):
        print(f"✓ {company}: {len(flags)} flags")
    
    elapsed = time.time() - start
    print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
    return elapsed


async def test_subreddit_parallelization():
    """Show how subreddits are checked in parallel for ONE company"""
    print("\n" + "="*60)
    print("🔬 SUBREDDIT PARALLELIZATION TEST")
    print("="*60)
    
    company = "Propgrowthx Pvt. Ltd."
    
    # Sequential (old way)
    print(f"\n1️⃣  Sequential: Checking {len(WORKING_SUBREDDITS)} subreddits one-by-one...")
    reddit = asyncpraw.Reddit(
        client_id="OMPlBPoltQK0v5O1NuhpOA",
        client_secret="7rsKEI2U0lqvitOsTa5I8UTfdmSrNQ",
        user_agent="InternshipScraperBot by /u/LongjumpingDay729",
        timeout=15
    )
    
    start = time.time()
    total_flags = 0
    
    for sub in WORKING_SUBREDDITS:
        flags = await search_single_subreddit(reddit, sub, company, limit=10)
        total_flags += len(flags)
        print(f"   r/{sub}: {len(flags)} flags")
    
    seq_time = time.time() - start
    await reddit.close()
    print(f"   ⏱️  Time: {seq_time:.1f}s")
    
    # Concurrent (new way)
    print(f"\n2️⃣  Concurrent: Checking all {len(WORKING_SUBREDDITS)} subreddits at once...")
    
    start = time.time()
    flags = await check_scam_comments(company, limit=10)
    conc_time = time.time() - start
    
    print(f"   ✓ Found {len(flags)} total flags")
    print(f"   ⏱️  Time: {conc_time:.1f}s")
    
    speedup = seq_time / conc_time if conc_time > 0 else 0
    print(f"\n   🚀 Speedup: {speedup:.1f}x faster!")


async def main():
    print("\n" + "="*60)
    print("⚡ ASYNC PERFORMANCE TEST")
    print("="*60)
    print(f"Testing with {len(TEST_COMPANIES)} companies")
    print(f"Checking {len(WORKING_SUBREDDITS)} subreddits each")
    print("="*60)
    
    # Test 1: Subreddit parallelization
    await test_subreddit_parallelization()
    
    await asyncio.sleep(2)
    
    # Test 2: Sequential vs Concurrent company checks
    seq_time = await test_sequential_checks()
    
    await asyncio.sleep(2)
    
    conc_time = await test_concurrent_checks()
    
    # Summary
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    print(f"Sequential mode:  {seq_time:.1f}s")
    print(f"Concurrent mode:  {conc_time:.1f}s")
    
    speedup = seq_time / conc_time if conc_time > 0 else 0
    print(f"\n🚀 Overall speedup: {speedup:.1f}x faster!")
    print(f"⏱️  Time saved: {seq_time - conc_time:.1f} seconds")
    print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted")