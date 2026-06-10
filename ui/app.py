"""
PakStudentAlert — Streamlit UI
Run with: python -m streamlit run ui/app.py
"""

import streamlit as st
import asyncio
import sys, os, json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from agents.planner import PlannerAgent
from agents.crawler import CrawlerAgent
from agents.validator import ValidatorAgent
from agents.relevance import RelevanceAgent, FeedbackAwareRelevanceAgent, compute_aggregate
from tools.feedback_store import FeedbackStore
from data.universities import UNIVERSITIES, DISCIPLINE_UNIVERSITIES

st.set_page_config(page_title="PakStudentAlert", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.alert-card {
    background:#1e2130; border-radius:10px; padding:16px 20px;
    border-left:4px solid #4f8ef7; margin-bottom:10px;
}
.alert-high   { border-left-color:#ff4b4b; }
.alert-medium { border-left-color:#ffa500; }
.alert-low    { border-left-color:#21c55d; }
.eligible   { color:#21c55d; font-weight:600; }
.borderline { color:#ffa500; font-weight:600; }
.below      { color:#ff4b4b; font-weight:600; }
.agent-step         { font-family:monospace; font-size:13px; color:#a0aec0; padding:2px 0; }
.agent-step.done    { color:#21c55d; }
.agent-step.running { color:#4f8ef7; }
.agent-step.fail    { color:#ff4b4b; }
.feedback-bar { background:#1a1d2e; border-radius:8px; padding:8px 12px; margin-top:6px; }
</style>
""", unsafe_allow_html=True)

# ── Feedback store (shared across session) ────────────────────────────────────
if "fb_store" not in st.session_state:
    st.session_state.fb_store = FeedbackStore()
fb_store = st.session_state.fb_store

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Your Profile")
    st.markdown("---")
    name       = st.text_input("Name", value="Ali")
    discipline = st.selectbox("Discipline", list(DISCIPLINE_UNIVERSITIES.keys()))
    all_unis   = list(UNIVERSITIES.keys())
    universities = st.multiselect("Target universities", all_unis,
                                   default=DISCIPLINE_UNIVERSITIES.get(discipline, all_unis)[:4])
    st.markdown("#### 📊 Academic Scores")
    c1, c2 = st.columns(2)
    with c1:
        matric     = st.number_input("Matric %",   0.0, 100.0, 91.0, step=0.5)
        test_score = st.number_input("Test score", 0,   400,   145)
    with c2:
        fsc       = st.number_input("FSc %", 0.0, 100.0, 88.0, step=0.5)
        test_type = st.selectbox("Test", ["NET", "ECAT", "MDCAT", "SAT"])

    test_max  = {"NET":200,"ECAT":400,"MDCAT":200,"SAT":1600}[test_type]
    aggregate = round((matric*0.10)+(fsc*0.40)+((test_score/test_max)*100*0.50), 2)
    st.metric("Your Aggregate", f"{aggregate}%")

    # Show feedback stats
    summary = fb_store.get_summary(discipline)
    if summary.get("total_feedback", 0) > 0:
        st.markdown("---")
        st.markdown(f"#### 🧠 Agent has learned from {summary['total_feedback']} ratings")
        if summary.get("liked_types"):
            st.markdown(f"Prefers: `{'`, `'.join(summary['liked_types'])}`")
        if summary.get("disliked_types"):
            st.markdown(f"Skips: `{'`, `'.join(summary['disliked_types'])}`")

    st.markdown("---")
    run_btn = st.button("🚀 Run Pipeline", type="primary", use_container_width=True)

profile = {
    "name": name, "discipline": discipline,
    "universities": universities or DISCIPLINE_UNIVERSITIES.get(discipline, all_unis)[:4],
    "degree": "BS", "year": "applying",
    "matric_pct": matric, "fsc_pct": fsc,
    "test_score": test_score, "test_type": test_type,
    "aggregate_pct": aggregate,
    "interests": ["admissions","scholarships","merit lists","fee structure"],
    "email": "",
}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🎓 PakStudentAlert")
st.markdown("*Autonomous Pakistani university monitor — learns what matters to you over time*")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📡 Live Pipeline", "🏛️ University Explorer", "❓ Ask Anything", "📊 My Feedback"])

# ── TAB 1: Live Pipeline ──────────────────────────────────────────────────────
with tab1:
    if not run_btn:
        st.info("Set your profile in the sidebar and click **Run Pipeline**.")
        st.markdown("""
**What the agents do:**
1. 🗺️ **Planner** — picks sources based on your discipline
2. 🕷️ **Crawler** — fetches all pages in parallel
3. ✅ **Validator** — resolves conflicts between sources
4. 🎯 **Relevance** — scores items, learns from your past feedback
        """)
    else:
        st.markdown(f"Running for **{name}** | {discipline} | Aggregate: **{aggregate}%**")
        log_box = st.empty()
        logs = []

        def log(msg, status="done"):
            logs.append((msg, status))
            log_box.markdown(
                "\n".join(f'<div class="agent-step {s}">{m}</div>' for m, s in logs),
                unsafe_allow_html=True
            )

        async def run_pipeline():
            log("🗺️  Planner — deciding sources...", "running")
            planner = PlannerAgent()
            targets = await planner.plan(profile)
            log(f"🗺️  Planner — {len(targets)} sources selected", "done")

            log(f"🕷️  Crawler — fetching {len(targets)} pages...", "running")
            crawler = CrawlerAgent()
            orig = crawler.fetch_page
            async def logged_fetch(session, source):
                r = await orig(session, source)
                if r["status"] == "ok" and r["text"].strip():
                    log(f"&nbsp;&nbsp;&nbsp;✓ {source['name']} — {len(r['text'])} chars", "done")
                else:
                    log(f"&nbsp;&nbsp;&nbsp;✗ {source['name']} — {r['status']}", "fail")
                return r
            crawler.fetch_page = logged_fetch
            raw = await crawler.crawl_all(targets)
            total = sum(len(r.get("items",[])) for r in raw)
            log(f"🕷️  Crawler — {total} items extracted", "done")

            log("✅  Validator — resolving conflicts...", "running")
            validator = ValidatorAgent()
            validated = await validator.validate(raw)
            log(f"✅  Validator — {len(validated)} items after dedup", "done")

            # Use feedback-aware agent if enough feedback exists
            summary = fb_store.get_summary(discipline)
            if summary.get("total_feedback", 0) >= 3:
                log(f"🧠  Relevance — applying {summary['total_feedback']} past ratings...", "running")
                rel_agent = FeedbackAwareRelevanceAgent()
                relevant = await rel_agent.filter_with_feedback(validated, profile, summary)
            else:
                log("🎯  Relevance — filtering for your profile...", "running")
                rel_agent = RelevanceAgent()
                relevant = await rel_agent.filter(validated, profile)

            log(f"🎯  Relevance — {len(relevant)} items for you", "done")
            log("✨  Done!", "done")
            return relevant

        try:
            relevant = asyncio.run(run_pipeline())
            st.session_state["last_results"] = relevant
            st.session_state["last_profile"]  = profile.copy()
        except Exception as e:
            st.error(f"Error: {e}")
            relevant = []

        st.markdown("---")
        if not relevant:
            st.warning("No relevant items found. Try adding more universities in the sidebar.")
        else:
            st.markdown(f"### 🔔 {len(relevant)} items found")
            st.caption("Rate each item to help the agent learn your preferences")

            for i, item in enumerate(relevant):
                urgency     = item.get("urgency","low").split(" ")[0].lower()
                elig_status = item.get("eligibility_status","")
                elig_note   = item.get("eligibility_note","")
                conflict    = item.get("conflict_flagged", False)

                u_emoji = {"high":"🔴","medium":"🟡","low":"🟢"}.get(urgency,"📌")
                e_emoji = {"strong":"✅","eligible":"✅","borderline":"⚠️","below":"❌"}.get(elig_status,"")
                e_class = {"strong":"eligible","eligible":"eligible","borderline":"borderline","below":"below"}.get(elig_status,"")

                date_html     = f"&nbsp;&nbsp;📅 {item['date']}" if item.get("date") else ""
                source_html   = f"&nbsp;&nbsp;🏛️ {item.get('_source','')}" if item.get("_source") else ""
                elig_html     = f'<br><span class="{e_class}">{e_emoji} {elig_note}</span>' if elig_note else ""
                conflict_html = f'<br><span style="color:#ffa500">⚠️ {item.get("conflict_note","Conflicting sources")}</span>' if conflict else ""

                st.markdown(f"""
<div class="alert-card alert-{urgency}">
  <b>{u_emoji} {item["title"]}</b>
  <span style="color:#718096;font-size:13px">{date_html}{source_html}</span>
  <br><span style="color:#a0aec0">{item.get("details","")}</span>
  {elig_html}{conflict_html}
</div>""", unsafe_allow_html=True)

                # Feedback buttons
                col_up, col_down, col_skip = st.columns([1, 1, 6])
                with col_up:
                    if st.button("👍", key=f"up_{i}"):
                        fb_store.record(
                            item_title=item["title"],
                            item_source=item.get("_source",""),
                            item_type=item.get("type",""),
                            vote="up",
                            profile_discipline=discipline
                        )
                        st.success("Got it — I'll show more like this!", icon="✅")
                with col_down:
                    if st.button("👎", key=f"dn_{i}"):
                        fb_store.record(
                            item_title=item["title"],
                            item_source=item.get("_source",""),
                            item_type=item.get("type",""),
                            vote="down",
                            profile_discipline=discipline
                        )
                        st.info("Got it — I'll deprioritize these.", icon="📉")

# ── TAB 2: University Explorer ────────────────────────────────────────────────
with tab2:
    st.markdown(f"### 🏛️ University Explorer — your aggregate: **{aggregate}%**")
    st.markdown("---")
    disc_filter = st.selectbox("Filter by discipline", ["All"]+list(DISCIPLINE_UNIVERSITIES.keys()), key="disc_filter")

    for uni_name, uni in UNIVERSITIES.items():
        if disc_filter != "All" and disc_filter not in uni.get("disciplines",[]):
            continue
        with st.expander(f"**{uni_name}** — {uni['full_name']}"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Entry Test:** {uni['entry_test']}")
                st.markdown(f"**Campuses:** {', '.join(uni['campuses'])}")
            with c2:
                st.markdown(f"**Aid:** {'✅' if uni.get('financial_aid') else '❌'}")
                st.markdown(f"**Hostel:** {'✅' if uni.get('hostel') else '❌'}")
            with c3:
                st.markdown(f"**Disciplines:** {', '.join(uni['disciplines'])}")
            for prog_key, prog in uni.get("programs",{}).items():
                low, high = prog["merit_range"]
                fee = prog["fee_per_semester"]
                if   aggregate >= high-2: elig,color = "✅ Strong",      "green"
                elif aggregate >= low:    elig,color = "✅ Eligible",    "green"
                elif aggregate >= low-3:  elig,color = "⚠️ Borderline", "orange"
                else:                     elig,color = "❌ Below cutoff","red"
                st.markdown(f"&nbsp;&nbsp;**{prog['degree']}** — Merit: {low}–{high}% | Fee/sem: Rs. {fee:,} | :{color}[{elig}]")

# ── TAB 3: Ask Anything ───────────────────────────────────────────────────────
with tab3:
    st.markdown("### ❓ Ask anything about Pakistani universities")
    st.markdown("*Gemini + your knowledge base — no scraping needed*")
    st.markdown("---")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if question := st.chat_input("e.g. Am I eligible for FAST CS? What is GIKI's fee?"):
        st.session_state.chat.append({"role":"user","content":question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                model = genai.GenerativeModel("gemini-2.5-flash")
                try:
                    resp = model.generate_content(f"""
You are a Pakistani university admissions advisor.
Student: {name}, {discipline}, aggregate {aggregate}%, targets: {universities}
Matric: {matric}%, FSc: {fsc}%, {test_type}: {test_score}
University knowledge base: {json.dumps(UNIVERSITIES, indent=2)}
Answer concisely (3-5 sentences): {question}
""")
                    answer = resp.text
                except Exception:
                    answer = "Gemini is overloaded right now — try again in a minute."
                st.markdown(answer)
                st.session_state.chat.append({"role":"assistant","content":answer})

# ── TAB 4: Feedback History ───────────────────────────────────────────────────
with tab4:
    st.markdown("### 📊 Your Feedback History")
    st.markdown("*The agent uses this to improve relevance scoring over time*")
    st.markdown("---")

    all_feedback = fb_store.get_all()
    if not all_feedback:
        st.info("No feedback yet. Run the pipeline and rate some results with 👍 or 👎.")
    else:
        liked    = [f for f in all_feedback if f["vote"] == "up"]
        disliked = [f for f in all_feedback if f["vote"] == "down"]

        c1, c2, c3 = st.columns(3)
        c1.metric("Total ratings", len(all_feedback))
        c2.metric("👍 Useful",     len(liked))
        c3.metric("👎 Not useful", len(disliked))

        st.markdown("---")

        if liked:
            st.markdown("#### 👍 Marked as useful")
            for f in liked[-10:]:
                st.markdown(f"- **{f['title']}** _{f.get('source','')}_ `{f.get('type','')}`")

        if disliked:
            st.markdown("#### 👎 Marked as not useful")
            for f in disliked[-10:]:
                st.markdown(f"- **{f['title']}** _{f.get('source','')}_ `{f.get('type','')}`")

        if len(all_feedback) < 3:
            st.caption(f"Rate {3-len(all_feedback)} more item(s) for the agent to start adapting.")
        else:
            st.success("✅ Agent is now learning from your feedback — relevance scoring is personalised!")