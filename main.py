"""
PakStudentAlert
===============
Run this to start the agent pipeline manually.

Usage:
    python main.py                        # run full pipeline
    python main.py --query "FAST merit"   # ask a one-off question
"""

import asyncio
import argparse
from dotenv import load_dotenv
load_dotenv()

from agents.planner import PlannerAgent
from agents.crawler import CrawlerAgent
from agents.validator import ValidatorAgent
from agents.relevance import RelevanceAgent
from agents.alert import AlertAgent
from data.student_profile import load_profile


async def run_pipeline(query: str = None):
    print("\n🚀 PakStudentAlert pipeline starting...\n")

    profile = load_profile()

    planner = PlannerAgent()
    crawl_targets = await planner.plan(profile, query)
    print(f"📋 Planner: will check {len(crawl_targets)} sources\n")

    crawler = CrawlerAgent()
    raw_results = await crawler.crawl_all(crawl_targets)
    print(f"🕷️  Crawler: fetched {len(raw_results)} pages\n")

    validator = ValidatorAgent()
    validated = await validator.validate(raw_results)
    print(f"✅ Validator: {len(validated)} items after deduplication\n")

    relevance = RelevanceAgent()
    relevant = await relevance.filter(validated, profile)
    print(f"🎯 Relevance: {len(relevant)} items relevant to your profile\n")

    alert = AlertAgent()
    await alert.notify(relevant, profile)

    print("\n✨ Pipeline complete.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default=None)
    args = parser.parse_args()
    asyncio.run(run_pipeline(args.query))