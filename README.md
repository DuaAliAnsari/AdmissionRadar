# PakStudentAlert 🎓

An autonomous multi-agent system that monitors Pakistani university websites, HEC, and education portals — and proactively alerts students about deadlines, merit lists, and scholarships **without them having to check**.

## Architecture

```
Cloud Scheduler (daily)
        ↓
  Planner Agent      → decides which sources to check
        ↓
  Crawler Agents     → fetches sources in parallel
        ↓
  Validator Agent    → reconciles conflicts between sources
        ↓
  Relevance Agent    → filters by student profile
        ↓
  Alert Agent        → sends WhatsApp/email if anything is new
```

## What makes it agentic (not just RAG)

- **Autonomous execution** — runs daily on Cloud Scheduler without any user prompt
- **Conflict resolution** — when two sources disagree on merit numbers, Gemini reasons about which to trust
- **Proactive alerts** — pushes notifications before the student thinks to check
- **Memory** — Firebase tracks what's been sent so you never get duplicate alerts
- **Parallel execution** — all crawler agents run simultaneously

## Setup

```bash
git clone https://github.com/yourusername/pakstudent-alert
cd pakstudent-alert
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Gemini API key
# Edit data/student_profile.py with your details
python main.py
```

## Get a Gemini API Key

1. Go to https://ai.google.dev
2. Click "Get API key"
3. Free tier is more than enough for this project

## Enable WhatsApp Alerts (optional)

1. Sign up at https://twilio.com (free tier)
2. Join the WhatsApp sandbox
3. Add your Twilio credentials to `.env`

## Deploy to run daily automatically

```bash
# Deploy to Google Cloud Run
gcloud run deploy pakstudent-alert --source .

# Set up Cloud Scheduler to hit it daily at 8am PKT
gcloud scheduler jobs create http pakstudent-daily \
  --schedule="0 8 * * *" \
  --time-zone="Asia/Karachi" \
  --uri="YOUR_CLOUD_RUN_URL"
```

## Tech stack

- **Google Gemini 2.0 Flash** — LLM for extraction, validation, relevance scoring
- **aiohttp** — async parallel web crawling
- **BeautifulSoup** — HTML parsing
- **Firebase Firestore** — alert deduplication storage
- **Twilio** — WhatsApp notifications
- **Google Cloud Run + Scheduler** — serverless deployment + daily trigger

## Built by

[Your name] — built as a portfolio project to demonstrate multi-agent AI systems
