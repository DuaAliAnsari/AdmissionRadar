"""
PakStudentAlert — Autonomous Pakistani University Monitor
=========================================================
Run this file to start the agent pipeline manually.
In production, Cloud Scheduler hits this daily automatically.

Usage:
    python main.py                        # run full pipeline
    python main.py --query "FAST merit"   # ask a one-off question
"""
from dotenv import load_dotenv
load_dotenv()

import asyncio
import argparse
from agents.planner import PlannerAgent
from agents.crawler import CrawlerAgent
from agents.validator import ValidatorAgent
from agents.relevance import RelevanceAgent
from agents.alert import AlertAgent
from data.student_profile import load_profile
from tools.firebase_client import FirebaseClient


async def run_pipeline(query: str = None):
    print("\n🚀 PakStudentAlert pipeline starting...\n")

    # Load student preferences (which unis, programs, deadlines matter)
    profile = load_profile()

    # 1. Planner — decides what to crawl today
    planner = PlannerAgent()
    crawl_targets = await planner.plan(profile, query)
    print(f"📋 Planner: will check {len(crawl_targets)} sources\n")

    # 2. Crawler — hits each source in parallel
    crawler = CrawlerAgent()
    raw_results = await crawler.crawl_all(crawl_targets)
    print(f"🕷️  Crawler: fetched {len(raw_results)} pages\n")

    # 3. Validator — reconciles conflicts between sources
    validator = ValidatorAgent()
    validated = await validator.validate(raw_results)
    print(f"✅ Validator: {len(validated)} items after deduplication\n")

    # 4. Relevance — filters by student profile
    relevance = RelevanceAgent()
    relevant = await relevance.filter(validated, profile)
    print(f"🎯 Relevance: {len(relevant)} items relevant to your profile\n")

    # 5. Alert — send notification if anything is new
    db = FirebaseClient()
    alert = AlertAgent(db)
    await alert.notify(relevant, profile)

    print("\n✨ Pipeline complete.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default=None)
    args = parser.parse_args()
    asyncio.run(run_pipeline(args.query))
