import asyncio, aiohttp, json, re, os, time
from datetime import datetime
from bs4 import BeautifulSoup
from google import genai

def _strip_fences(text):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else text

class CrawlerAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    async def fetch_page(self, session, source):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.google.com/",
        }
        try:
            async with session.get(source["url"], headers=headers, timeout=aiohttp.ClientTimeout(total=20), ssl=False) as resp:
                if resp.status != 200:
                    print(f"  ✗ {source['name']} — HTTP {resp.status}")
                    return {"source": source, "text": "", "status": f"http_{resp.status}"}
                html = await resp.text(errors="ignore")
                soup = BeautifulSoup(html, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    tag.decompose()
                main = soup.find("main") or soup.find(id="main") or soup.find(class_="content") or soup
                text = main.get_text(separator="\n", strip=True)[:5000]
                print(f"  ✓ {source['name']} — {len(text)} chars")
                return {"source": source, "text": text, "status": "ok"}
        except Exception as e:
            print(f"  ✗ {source['name']} — {e}")
            return {"source": source, "text": "", "status": f"error: {e}"}

    async def extract_all_info(self, pages):
        ok_pages = [p for p in pages if p["status"] == "ok" and p["text"].strip()]
        if not ok_pages:
            print("  ⚠️  No pages fetched successfully.")
            return []

        pages_text = ""
        for i, p in enumerate(ok_pages):
            pages_text += f"\n\n--- SOURCE {i+1}: {p['source']['name']} ({p['source']['type']}) ---\n"
            pages_text += f"URL: {p['source']['url']}\nContent:\n{p['text']}"

        today = datetime.now().strftime("%Y-%m-%d")
        prompt = f"""
You are extracting actionable information from Pakistani university/education websites.
Today's date: {today}

{pages_text}

Extract ONLY concrete, actionable items with specific facts: dates, deadlines, merit lists, 
scholarship openings, fee amounts, test dates. 

SKIP: generic text like "apply now", "we welcome students", "join our university", anything 
with no specific date or number attached.

SKIP any item whose date is more than 6 months in the past (before {today[:7]}).

Return ONLY a JSON array, one element per source:
[
  {{
    "source": "<source name>",
    "items": [
      {{
        "title": "short specific title",
        "type": "deadline|merit_list|scholarship|fee|test|announcement",
        "date": "YYYY-MM-DD or null",
        "details": "1 sentence with the specific fact — include the actual date/number",
        "urgency": "high (within 2 weeks)|medium (within 2 months)|low (further out)"
      }}
    ]
  }}
]

If a source has only generic marketing text, return "items": [] for it.
No explanation. JSON only.
"""
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(model="gemini-2.0-flash-001", contents=prompt)
                break
            except Exception as e:
                if "503" in str(e) and attempt < 2:
                    print(f"  ⏳ Gemini overloaded, retrying in 30s... (attempt {attempt+1}/3)")
                    time.sleep(30)
                else:
                    raise

        try:
            results = json.loads(_strip_fences(response.text))
            total = sum(len(r.get("items", [])) for r in results)
            print(f"  → Gemini extracted {total} item(s) across {len(ok_pages)} sources")
            return results
        except Exception as e:
            print(f"  → Gemini parse error: {e}\n  Raw: {response.text[:200]}")
            return []

    async def crawl_all(self, sources):
        print(f"  Fetching {len(sources)} pages in parallel...")
        async with aiohttp.ClientSession() as session:
            pages = await asyncio.gather(*[self.fetch_page(session, s) for s in sources])
        ok = sum(1 for p in pages if p["status"] == "ok" and p["text"].strip())
        print(f"  {ok}/{len(sources)} pages fetched successfully")
        if ok == 0:
            return []
        print(f"  Extracting structured info with Gemini (batched)...")
        results = await self.extract_all_info(pages)
        return [r for r in results if r.get("items")]