# AdmissionRadar 🎓

Monitors Pakistani university admission portals daily and tells you what's relevant to you — deadlines, merit lists, scholarships — filtered by your academic scores and preferences.

---

## How it works

A pipeline of 5 agents runs in sequence:

1. **Planner** — looks at your discipline and target universities, decides which sources to check
2. **Crawler** — fetches all sources in parallel using async HTTP
3. **Validator** — when two sources report different information (e.g. conflicting merit cutoffs), uses Gemini to reason about which to trust
4. **Relevance** — scores each item against your profile and academic scores, flags programs as eligible, borderline, or below cutoff
5. **Alert** — shows only new items not seen in previous runs

After you rate results 👍/👎, the Relevance agent adjusts scoring on future runs.

---

## Tech Stack

Python · Google Gemini 2.5 · AsyncIO · aiohttp · BeautifulSoup · Streamlit

---

## Setup

```bash
git clone https://github.com/yourusername/admission-radar
cd admission-radar
pip install -r requirements.txt
```

Create a `.env` file:
```
GEMINI_API_KEY=your_key_here
```

Get a free Gemini API key at https://ai.google.dev

Edit `data/student_profile.py` with your name, discipline, target universities, and academic scores.

```bash
python main.py                         # run pipeline in terminal
python -m streamlit run ui/app.py      # open UI in browser
```

---

## UI

Three tabs:

**📡 Live Pipeline** — run the agents and watch them execute in real time. Results show as cards with eligibility badges and 👍/👎 rating buttons.

**🏛️ University Explorer** — browse 20+ universities. Shows your eligibility for every program based on your aggregate automatically.

**❓ Ask Anything** — chat interface backed by Gemini and the university knowledge base. Ask things like "Am I eligible for FAST CS?" or "What is GIKI's fee per semester?"

---

## Universities Covered

FAST NUCES · NUST · LUMS · COMSATS · IBA Karachi · NED Karachi · Habib University · GIKI · ITU · UET Lahore · Air University · QAU · PU Lahore · Sukkur IBA · SZABIST · DOW University · KEMU · Aga Khan University · MUET · UCP

---

## Project Structure

```
admission-radar/
├── main.py
├── agents/
│   ├── planner.py        ← discipline-aware source selection
│   ├── crawler.py        ← parallel async crawling
│   ├── validator.py      ← conflict resolution via Gemini
│   ├── relevance.py      ← eligibility filtering + feedback learning
│   └── alert.py          ← deduplication and terminal output
├── data/
│   ├── universities.py   ← 20+ unis with merit ranges, fees, programs
│   └── student_profile.py
├── tools/
│   └── feedback_store.py
└── ui/
    └── app.py
```