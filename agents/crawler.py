"""
Crawler Agent
-------------
Fetches each source URL and uses Gemini to extract structured info
from the raw HTML. Runs all sources in parallel using asyncio.
"""

import asyncio
import aiohttp
import google.generativeai as genai
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime


class CrawlerAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    async def fetch_page(self, session: aiohttp.ClientSession, source: dict) -> dict:
        """Fetch a single URL and return raw text."""
        headers = {"User-Agent": "Mozilla/5.0 (compatible; PakStudentBot/1.0)"}
        try:
            async with session.get(source["url"], headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                # Remove noise: scripts, styles, nav
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                return {
                    "source": source,
                    "text": soup.get_text(separator="\n", strip=True)[:4000],
                    "status": "ok"
                }
        except Exception as e:
            return {"source": source, "text": "", "status": f"error: {e}"}

    async def extract_info(self, page: dict) -> dict:
        """Use Gemini to extract structured info from raw page text."""
        if page["status"] != "ok" or not page["text"]:
            return {"source": page["source"]["name"], "items": [], "status": page["status"]}

        prompt = f"""
You are extracting information from a Pakistani university/education website.

Source: {page["source"]["name"]}
Type: {page["source"]["type"]}
Today's date: {datetime.now().strftime("%Y-%m-%d")}

Page content:
{page["text"]}

Extract ALL relevant items (scholarships, deadlines, merit lists, announcements).
Return ONLY a JSON object in this exact format, no explanation:
{{
  "source": "{page["source"]["name"]}",
  "items": [
    {{
      "title": "...",
      "type": "deadline|merit_list|scholarship|announcement",
      "date": "YYYY-MM-DD or null",
      "details": "brief summary in 1-2 sentences",
      "urgency": "high|medium|low"
    }}
  ]
}}

If nothing relevant found, return {{"source": "{page["source"]["name"]}", "items": []}}
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
        except Exception as e:
            return {"source": page["source"]["name"], "items": [], "error": str(e)}

    async def crawl_all(self, sources: list[dict]) -> list[dict]:
        """Crawl all sources in parallel, then extract info in parallel."""
        print(f"  Fetching {len(sources)} pages in parallel...")

        async with aiohttp.ClientSession() as session:
            pages = await asyncio.gather(*[self.fetch_page(session, s) for s in sources])

        print(f"  Extracting structured info with Gemini...")
        results = await asyncio.gather(*[self.extract_info(p) for p in pages])

        return [r for r in results if r.get("items")]
