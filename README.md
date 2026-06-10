# PakStudentAlert 🎓

Monitors Pakistani university websites, HEC, and education portals daily — and alerts students about deadlines, merit lists, and scholarships without them having to check.

---

## Features

- **Autonomous pipeline** — runs daily without any user prompt
- **Parallel crawling** — fetches 13+ sources simultaneously
- **Conflict resolution** — when two sources disagree, Gemini reasons about which to trust
- **Eligibility filtering** — computes your aggregate and flags programs as eligible, borderline, or below cutoff
- **Feedback learning** — 👍/👎 ratings improve relevance scoring over time
- **Gmail alerts** — notifies you only when something new appears
- **Streamlit UI** — live pipeline view, university explorer, and chat interface

---

## Tech Stack

Python · Google Gemini 2.5 · AsyncIO · aiohttp · BeautifulSoup · Firebase · Streamlit · Google Cloud Run

---

## Setup

```bash
git clone https://github.com/yourusername/pakstudent-alert
cd pakstudent-alert
pip install -r requirements.txt
```

Create a `.env` file:
```
GEMINI_API_KEY=your_key_here
GMAIL_ADDRESS=your@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

Edit `data/student_profile.py` with your details, then:

```bash
python main.py                        # run pipeline in terminal
python -m streamlit run ui/app.py     # run UI
```

Get a free Gemini API key at https://ai.google.dev

---

## Project Structure

```
pakstudent-alert/
├── main.py
├── agents/
│   ├── planner.py       ← discipline-aware source selection
│   ├── crawler.py       ← parallel async crawling
│   ├── validator.py     ← conflict resolution
│   ├── relevance.py     ← eligibility filtering + feedback learning
│   └── alert.py         ← Gmail notifications
├── data/
│   ├── universities.py  ← 20+ unis with merit ranges, fees, programs
│   └── student_profile.py
├── tools/
│   ├── firebase_client.py
│   └── feedback_store.py
└── ui/
    └── app.py           ← Streamlit dashboard
```

---

## Deploy

```bash
gcloud run deploy pakstudent-alert --source .

gcloud scheduler jobs create http pakstudent-daily \
  --schedule="0 8 * * *" \
  --time-zone="Asia/Karachi" \
  --uri="YOUR_CLOUD_RUN_URL"
```