"""
Compass AI - Streamlit Web Application
Personalized Learning Roadmap & Skill-Gap Optimization Engine
UN SDG 4 Alignment: Quality Education & Lifelong Learning
"""
import os
import sys

import streamlit as st

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.adaptation import adapt_roadmap_progress
from core.agent import CompassAgent
from core.priority import calculate_priorities
from core.profile import UserProfile
from core.roadmap import generate_roadmap
from core.skill_gap import calculate_skill_gap
from llm.client import extract_profile_from_text
from llm.explain import generate_recommendation_explanation
from rag.ranking import filter_and_rank_resources
from rag.retriever import FAISSRetriever

# Page Configuration
st.set_page_config(
    page_title="Compass AI | Personalized Learning Path",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling (Glassmorphism & Navigation Metaphor Aesthetics)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .tagline {
        color: #38BDF8;
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: -0.3rem;
    }

    .sdg-badge {
        background: linear-gradient(90deg, #C5192D 0%, #E5243B 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 0.8rem;
    }

    .wizard-card {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
    }

    .metric-card {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.25rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }

    .status-existing {
        color: #10B981;
        font-weight: 700;
    }
    .status-needs-imp {
        color: #F59E0B;
        font-weight: 700;
    }
    .status-missing {
        color: #EF4444;
        font-weight: 700;
    }

    .resource-card {
        background: #1E293B;
        border-left: 5px solid #38BDF8;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    }

    .priority-card {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid #38BDF8;
        padding: 1.1rem 1.3rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }

    .verdict-success {
        background-color: #065F46;
        color: #A7F3D0;
        padding: 0.85rem 1.2rem;
        border-radius: 8px;
        font-weight: 700;
    }
    .verdict-warning {
        background-color: #92400E;
        color: #FDE68A;
        padding: 0.85rem 1.2rem;
        border-radius: 8px;
        font-weight: 700;
    }
    .verdict-error {
        background-color: #991B1B;
        color: #FECACA;
        padding: 0.85rem 1.2rem;
        border-radius: 8px;
        font-weight: 700;
    }

    .step-pill {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 12px;
        background: #334155;
        color: #94A3B8;
    }
    .step-pill-active {
        background: #0284C7;
        color: white;
    }

    .breakdown-box {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.8rem 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #CBD5E1;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Vector Retriever
if "retriever" not in st.session_state:
    with st.spinner("Initializing Vector Retriever & Knowledge Base..."):
        retriever = FAISSRetriever()
        retriever.build_index()
        st.session_state.retriever = retriever

# Initialize Session State for Multi-step Wizard & Milestone Progress
if "intake_step" not in st.session_state:
    st.session_state.intake_step = 1

if "milestone_status" not in st.session_state:
    st.session_state.milestone_status = {}

if "draft_profile" not in st.session_state:
    st.session_state.draft_profile = {
        "name": "Student",
        "current_status": "Student",
        "education": "B.Tech / B.E.",
        "degree_branch": "AI & Data Science",
        "graduation_year": 2025,
        "goal": "Data Engineer",
        "goal_type": "Internship",
        "target_industry": "",
        "target_companies": "",
        "deadline_weeks": 12,
        "goal_importance": 8,
        "skills": {"Python": "intermediate", "SQL": "beginner"},
        "hours_per_day": 2.0,
        "days_per_week": 5,
        "budget": "Free only",
        "device": "Laptop",
        "internet_reliability": "Reliable",
        "language": ["English"],
        "learning_format": "Mixed / Any",
        "theory_practical_pref": "Balanced",
        "session_duration": "1 hour",
        "weakest_areas": ""
    }

# Application Header
st.markdown("""
<div class="main-header">
    <div class="sdg-badge">🇺🇳 UN SDG 4: Quality Education & Lifelong Learning</div>
    <h1 style="margin: 0; font-size: 2.2rem; font-weight: 700;">🧭 Compass AI</h1>
    <div class="tagline">"Too much information. Too many paths. One clear direction."</div>
    <p style="margin-top: 0.6rem; font-style: italic; opacity: 0.9; font-size: 0.95rem;">
        "The learner chooses the destination. Compass AI finds the optimal path."
    </p>
</div>
""", unsafe_allow_html=True)

# Available Core Skills
ALL_SKILLS = [
    "Python", "SQL", "Advanced SQL", "Statistics & Probability",
    "Data Visualization", "Data Modeling", "ETL", "Data Warehousing",
    "Cloud Fundamentals", "Spark & Big Data", "Machine Learning",
    "Deep Learning", "MLOps", "Portfolio Projects"
]

# Sidebar Navigation & Preset Profiles
st.sidebar.markdown("### ⚡ Demo Preset Profiles")

if st.sidebar.button("🎓 Demo 1: B.Tech Student (Data Engineer)", use_container_width=True):
    st.session_state.profile = UserProfile(
        name="Aarav Sharma",
        education="B.Tech / B.E.",
        degree_branch="AI & Data Science",
        graduation_year=2025,
        current_status="Student",
        goal="Data Engineer",
        goal_type="Internship",
        deadline_weeks=12,
        goal_importance=9,
        skills={"Python": "intermediate", "SQL": "beginner"},
        hours_per_day=2.0,
        days_per_week=5,
        hours_per_week=10,
        budget="free",
        language=["English"],
        learning_format="video"
    )
    st.rerun()

if st.sidebar.button("💼 Demo 2: Career Switcher (Data Analyst)", use_container_width=True):
    st.session_state.profile = UserProfile(
        name="Priya Patel",
        education="B.Sc / BCA",
        degree_branch="Computer Applications",
        graduation_year=2023,
        current_status="Working Professional",
        goal="Data Analyst",
        goal_type="Full-time Job",
        deadline_weeks=8,
        goal_importance=10,
        skills={"Statistics & Probability": "beginner", "SQL": "beginner"},
        hours_per_day=3.0,
        days_per_week=5,
        hours_per_week=15,
        budget="free",
        language=["English", "Hindi"],
        learning_format="practice"
    )
    st.rerun()

if st.sidebar.button("🚀 Demo 3: Advanced Learner (ML Engineer)", use_container_width=True):
    st.session_state.profile = UserProfile(
        name="Rohan Verma",
        education="M.Tech / M.E.",
        degree_branch="Computer Science",
        graduation_year=2024,
        current_status="Graduate",
        goal="ML Engineer",
        goal_type="Full-time Job",
        deadline_weeks=16,
        goal_importance=10,
        skills={"Python": "advanced", "SQL": "intermediate", "Statistics & Probability": "intermediate", "Machine Learning": "intermediate"},
        hours_per_day=4.0,
        days_per_week=5,
        hours_per_week=20,
        budget="paid",
        language=["English"],
        learning_format="projects"
    )
    st.rerun()

st.sidebar.markdown("---")
if "profile" in st.session_state and st.sidebar.button("🔄 Reset Profile / Retake Intake", use_container_width=True):
    del st.session_state.profile
    st.session_state.intake_step = 1
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 💬 Express Intake (Natural Language)")
nl_input = st.sidebar.text_area(
    "Describe your background & goal:",
    value="I am a student. I know basic SQL and intermediate Python. I want a Data Engineering internship in 3 months. I can study 10 hours per week and prefer free English resources.",
    height=120
)
if st.sidebar.button("✨ Parse & Generate Compass", type="primary", use_container_width=True):
    try:
        profile_nl, _ = extract_profile_from_text(nl_input)
        st.session_state.profile = profile_nl
        st.rerun()
    except (ValueError, KeyError, RuntimeError) as e:
        st.sidebar.error(f"Extraction error: {e}")

# RENDER ONBOARDING WIZARD WHEN NO ACTIVE PROFILE
if "profile" not in st.session_state:
    st.markdown("### 📋 Set Your Compass Direction (7-Step Intake Wizard)")
    step = st.session_state.intake_step
    draft = st.session_state.draft_profile

    # Step Progress Indicator
    st.progress(step / 7.0)
    steps_titles = [
        "1. About You", "2. Destination", "3. Current Position",
        "4. Constraints", "5. Preferences", "6. Context", "7. Generate Compass"
    ]
    p_html = "".join(
        f"<span class='step-pill {'step-pill-active' if i+1 == step else ''}'>{title}</span>"
        for i, title in enumerate(steps_titles)
    )
    st.markdown(p_html, unsafe_allow_html=True)

    with st.container():
        # STEP 1: ABOUT YOU
        if step == 1:
            st.subheader("Step 1: About You")
            col1, col2 = st.columns(2)
            with col1:
                draft["name"] = st.text_input("Full Name", value=draft.get("name", "Student"))
                draft["education"] = st.selectbox(
                    "Highest Education",
                    ["B.Tech / B.E.", "B.Sc / BCA", "M.Tech / M.E.", "M.Sc / MCA", "Non-Tech / Other"],
                    index=0
                )
            with col2:
                draft["degree_branch"] = st.text_input("Degree Branch / Specialization", value=draft.get("degree_branch", "AI & DS"))
                draft["current_status"] = st.selectbox("Current Status", ["Student", "Graduate", "Working Professional"], index=0)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Continue to Destination ➡️", key="step1_next", type="primary"):
                st.session_state.intake_step = 2
                st.rerun()

        # STEP 2: DESTINATION
        elif step == 2:
            st.subheader("Step 2: Your Destination & Career Target")
            c1, c2 = st.columns(2)
            with c1:
                draft["goal"] = st.selectbox(
                    "Target Career Goal",
                    ["Data Engineer", "Data Analyst", "ML Engineer"],
                    index=0
                )
                draft["goal_type"] = st.selectbox("Goal Type", ["Internship", "Full-time Job", "Skill Mastery", "Career Switch"], index=0)
            with c2:
                draft["deadline_weeks"] = st.number_input("Target Timeframe (Weeks)", min_value=2, max_value=52, value=draft.get("deadline_weeks", 12))
                draft["goal_priority"] = st.select_slider("Goal Urgency", options=["Low", "Medium", "High"], value="High")

            col_b, col_n = st.columns([1, 4])
            with col_b:
                if st.button("⬅️ Back", key="step2_back"):
                    st.session_state.intake_step = 1
                    st.rerun()
            with col_n:
                if st.button("Continue to Current Position ➡️", key="step2_next", type="primary"):
                    st.session_state.intake_step = 3
                    st.rerun()

        # STEP 3: CURRENT POSITION
        elif step == 3:
            st.subheader("Step 3: Current Position & Existing Skills")
            st.markdown("Select your current proficiency level for skills you possess:")
            
            curr_skills = draft.get("skills", {})
            updated_skills = {}
            
            col_s1, col_s2 = st.columns(2)
            for idx, skill in enumerate(ALL_SKILLS):
                target_col = col_s1 if idx % 2 == 0 else col_s2
                with target_col:
                    existing_lvl = curr_skills.get(skill, "none")
                    sel_lvl = st.selectbox(
                        f"Proficiency in **{skill}**",
                        ["none", "beginner", "intermediate", "advanced"],
                        index=["none", "beginner", "intermediate", "advanced"].index(existing_lvl),
                        key=f"skill_{skill}"
                    )
                    if sel_lvl != "none":
                        updated_skills[skill] = sel_lvl

            draft["skills"] = updated_skills

            col_b, col_n = st.columns([1, 4])
            with col_b:
                if st.button("⬅️ Back", key="step3_back"):
                    st.session_state.intake_step = 2
                    st.rerun()
            with col_n:
                if st.button("Continue to Constraints ➡️", key="step3_next", type="primary"):
                    st.session_state.intake_step = 4
                    st.rerun()

        # STEP 4: CONSTRAINTS
        elif step == 4:
            st.subheader("Step 4: Time Commitment & Resource Constraints")
            c1, c2 = st.columns(2)
            with c1:
                draft["hours_per_day"] = st.slider("Available Hours / Day", min_value=0.5, max_value=8.0, value=float(draft.get("hours_per_day", 2.0)), step=0.5)
                draft["days_per_week"] = st.slider("Study Days / Week", min_value=1, max_value=7, value=int(draft.get("days_per_week", 5)))
                calc_h = int(draft["hours_per_day"] * draft["days_per_week"])
                st.info(f"⏱️ Calculated Weekly Speed: **{calc_h} Hours/Week**")
            with c2:
                draft["budget"] = st.selectbox("Budget Constraint", ["Free only", "Paid Resources Allowed", "Limited Budget"], index=0)
                draft["device"] = st.selectbox("Primary Device", ["Laptop", "Desktop", "Mobile"], index=0)

            col_b, col_n = st.columns([1, 4])
            with col_b:
                if st.button("⬅️ Back", key="step4_back"):
                    st.session_state.intake_step = 3
                    st.rerun()
            with col_n:
                if st.button("Continue to Preferences ➡️", key="step4_next", type="primary"):
                    st.session_state.intake_step = 5
                    st.rerun()

        # STEP 5: PREFERENCES
        elif step == 5:
            st.subheader("Step 5: Learning Preferences")
            c1, c2 = st.columns(2)
            with c1:
                draft["language"] = st.multiselect("Preferred Languages", ["English", "Hindi", "Both"], default=["English"])
                draft["learning_format"] = st.selectbox("Preferred Format", ["Mixed / Any", "Video", "Reading", "Practice", "Projects"], index=0)
            with c2:
                draft["theory_practical_pref"] = st.select_slider("Theory vs Practical Preference", options=["More Theory", "Balanced", "More Practical"], value="Balanced")
                draft["session_duration"] = st.selectbox("Target Session Duration", ["30 min", "1 hour", "2 hours", "Flexible"], index=1)

            col_b, col_n = st.columns([1, 4])
            with col_b:
                if st.button("⬅️ Back", key="step5_back"):
                    st.session_state.intake_step = 4
                    st.rerun()
            with col_n:
                if st.button("Continue to Additional Context ➡️", key="step5_next", type="primary"):
                    st.session_state.intake_step = 6
                    st.rerun()

        # STEP 6: ADDITIONAL CONTEXT
        elif step == 6:
            st.subheader("Step 6: Additional Context & Focus Areas")
            draft["weakest_areas"] = st.text_input("Weakest Areas / Concerns (comma separated)", value=draft.get("weakest_areas", ""))
            draft["topics_already_studied"] = st.text_input("Topics / Courses Already Studied (comma separated)", value=draft.get("topics_already_studied", ""))
            draft["topics_to_prioritize"] = st.text_input("Topics You Want to Prioritize (comma separated)", value=draft.get("topics_to_prioritize", ""))
            draft["topics_to_postpone"] = st.text_input("Topics You Want to Postpone (comma separated)", value=draft.get("topics_to_postpone", ""))

            col_b, col_n = st.columns([1, 4])
            with col_b:
                if st.button("⬅️ Back", key="step6_back"):
                    st.session_state.intake_step = 5
                    st.rerun()
            with col_n:
                if st.button("Review & Generate Compass ➡️", key="step6_next", type="primary"):
                    st.session_state.intake_step = 7
                    st.rerun()

        # STEP 7: REVIEW & GENERATE
        elif step == 7:
            st.subheader("Step 7: Review & Generate Your Personalized Compass")
            total_weekly_h = int(draft.get("hours_per_day", 2.0) * draft.get("days_per_week", 5))

            st.markdown(f"""
            - **Target Goal:** `{draft.get('goal')}` ({draft.get('deadline_weeks')} Weeks Timeframe)
            - **Weekly Capacity:** `{total_weekly_h} Hours/Week` ({draft.get('hours_per_day')}h/day × {draft.get('days_per_week')} days)
            - **Current Skills:** `{', '.join(f'{k}:{v}' for k,v in draft.get('skills', {}).items()) if draft.get('skills') else 'None selected'}`
            - **Budget:** `{draft.get('budget')}` | **Language:** `{', '.join(draft.get('language', ['English']))}`
            """)

            col_b, col_g = st.columns([1, 4])
            with col_b:
                if st.button("⬅️ Back", key="step7_back"):
                    st.session_state.intake_step = 6
                    st.rerun()
            with col_g:
                if st.button("🚀 Generate My Personalized Compass", key="step7_generate", type="primary"):
                    if not draft.get("skills"):
                        st.error("Please select at least one current skill in Step 3.")
                    else:
                        budget_clean = "free" if "free" in draft.get("budget", "").lower() else ("paid" if "paid" in draft.get("budget", "").lower() else "any")
                        profile = UserProfile(
                            name=draft.get("name"),
                            education=draft.get("education"),
                            education_level=draft.get("education"),
                            degree_branch=draft.get("degree_branch"),
                            graduation_year=draft.get("graduation_year"),
                            current_status=draft.get("current_status"),
                            goal=draft.get("goal"),
                            goal_type=draft.get("goal_type"),
                            target_role=draft.get("target_role"),
                            target_industry=draft.get("target_industry"),
                            target_companies=[c.strip() for c in str(draft.get("target_companies", "")).split(",") if c.strip()],
                            deadline_weeks=int(draft.get("deadline_weeks", 12)),
                            goal_importance=8,
                            goal_priority=draft.get("goal_priority", "High"),
                            skills=draft.get("skills", {}),
                            skill_confidence=draft.get("skill_confidence", {}),
                            existing_projects=[p.strip() for p in str(draft.get("existing_projects", "")).split(",") if p.strip()],
                            certifications=[c.strip() for c in str(draft.get("certifications", "")).split(",") if c.strip()],
                            completed_courses=[c.strip() for c in str(draft.get("completed_courses", "")).split(",") if c.strip()],
                            hours_per_day=float(draft.get("hours_per_day", 2.0)),
                            days_per_week=int(draft.get("days_per_week", 5)),
                            hours_per_week=total_weekly_h,
                            budget=budget_clean,
                            device=draft.get("device"),
                            internet_quality=draft.get("internet_quality"),
                            internet_reliability=draft.get("internet_quality"),
                            language=draft.get("language", ["English"]) if draft.get("language") else ["English"],
                            learning_format=draft.get("learning_format"),
                            theory_practical_pref=draft.get("theory_practical_pref"),
                            session_duration=draft.get("session_duration"),
                            weakest_areas=[w.strip() for w in str(draft.get("weakest_areas", "")).split(",") if w.strip()],
                            topics_studied=[t.strip() for t in str(draft.get("topics_already_studied", "")).split(",") if t.strip()],
                            topics_prioritize=[t.strip() for t in str(draft.get("topics_to_prioritize", "")).split(",") if t.strip()],
                            topics_postpone=[t.strip() for t in str(draft.get("topics_to_postpone", "")).split(",") if t.strip()]
                        )
                        st.session_state.profile = profile
                        st.rerun()

# RENDER MAIN DASHBOARD WITH INFORMATION ARCHITECTURE WHEN PROFILE IS ACTIVE
else:
    profile = st.session_state.profile

    gap_report = calculate_skill_gap(profile)
    priority_report = calculate_priorities(profile, gap_report=gap_report)
    roadmap_report = generate_roadmap(profile, priority_report=priority_report)

    hours_by_skill = {item.skill.lower(): item.estimated_hours for item in roadmap_report.items + roadmap_report.overflow_items}
    pct_ready = int((len(gap_report.existing_skills) / max(1, gap_report.total_required_skills)) * 100)

    # INFORMATION ARCHITECTURE: 7 TOP-LEVEL TABS
    tab_home, tab_gap, tab_prio, tab_roadmap, tab_resources, tab_ask, tab_progress = st.tabs([
        "🧭 Compass Home",
        "📍 Skill Gap",
        "🎯 Your Direction",
        "🗺️ Roadmap",
        "📚 Resources",
        "🤔 Ask Compass",
        "📈 Progress Tracker"
    ])

    # =========================================================================
    # TAB 1: COMPASS HOME
    # =========================================================================
    with tab_home:
        st.markdown("### 🧭 YOUR COMPASS: Executive Route Overview")

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Destination Goal", profile.goal)
        with c2:
            st.metric("Target Timeframe", f"{profile.deadline_weeks} Weeks")
        with c3:
            st.metric("Weekly Commitment", f"{profile.hours_per_week} Hours/Week")
        with c4:
            st.metric("Current Readiness", f"{pct_ready}% Ready")
        with c5:
            st.metric("Focus Skills", f"{len(priority_report.now)} NOW | {len(priority_report.next_skills)} NEXT")

        st.markdown("---")

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.markdown("#### 🎯 Immediate Core Focus")
            if priority_report.now:
                top_now = priority_report.now[0]
                st.success(f"🔥 **Highest Priority Skill:** `{top_now.skill}` (Score: `{top_now.priority_score}`)")
                st.markdown(f"**Why Actionable Now?** {top_now.reasoning}")
                if getattr(top_now, "structured_reasons", None):
                    st.markdown("**Key Drivers:**")
                    for r in top_now.structured_reasons:
                        st.markdown(f"- {r}")
            else:
                st.info("No high-urgency NOW skills remaining. You are on track!")

        with col_h2:
            st.markdown("#### 👤 Profile Summary")
            st.markdown(f"""
            - **Learner Name:** `{profile.name or 'Student'}` ({profile.current_status})
            - **Education Background:** `{profile.education or 'Degree'}` ({profile.degree_branch or 'General'})
            - **Preferred Budget:** `{profile.budget.capitalize()}` | **Languages:** `{', '.join(profile.language)}`
            - **Preferred Format:** `{profile.learning_format.capitalize()}` | **Session Length:** `{profile.session_duration}`
            """)

        st.markdown("---")

        # 1. WHY COMPASS SECTION
        st.markdown("#### 💡 WHY COMPASS?")
        st.markdown("""
        Generic learning platforms often present learners with too many options without clear direction. Compass AI takes a structured, 6-step approach:
        1. **Understand your destination**: Define target goal & role expectations.
        2. **Understand your current position**: Map existing skills & confidence levels.
        3. **Identify the gap**: Pinpoint specific missing skill steps required.
        4. **Prioritize what matters**: Sequence prerequisites and core skills deterministically.
        5. **Build a capacity-aware route**: Fit learning workload into real-world available weekly hours.
        6. **Recommend targeted resources**: Filter and rank top learning materials matching budget & language.
        """)

        # 2. LEARNING EFFICIENCY METRICS & SUSTAINABLE LEARNING CARD
        avail_h = roadmap_report.total_available_capacity_hours
        alloc_h = roadmap_report.total_estimated_hours
        rem_h = max(0, avail_h - alloc_h)

        st.markdown("#### 📊 LEARNING EFFICIENCY & CAPACITY ALLOCATION")
        m_eff1, m_eff2, m_eff3, m_eff4 = st.columns(4)
        with m_eff1:
            st.metric("Available Capacity", f"{avail_h} Hours")
        with m_eff2:
            st.metric("Estimated Core Path", f"{alloc_h} Hours")
        with m_eff3:
            st.metric("Unallocated Buffer", f"{rem_h} Hours")
        with m_eff4:
            st.metric("Prioritized Skills", f"{len(priority_report.now)} NOW | {len(priority_report.next_skills)} NEXT")

        st.markdown("""
        <div style="background:#1E293B; border-left: 5px solid #10B981; padding: 1.2rem; border-radius: 8px; margin-top: 1rem;">
            <h4 style="margin:0; color:#A7F3D0;">🌱 SUSTAINABLE LEARNING & SDG 4 ALIGNMENT</h4>
            <p style="margin:0.4rem 0 0.8rem 0; font-size:0.9rem; color:#CBD5E1;">
                Compass AI promotes efficient and personalized learning through targeted skill development and capacity-aware planning, 
                helping learners focus study time on relevant resources and avoid unnecessary learning effort.
            </p>
            <ul style="margin:0; padding-left:1.2rem; font-size:0.85rem; color:#A7F3D0;">
                <li>✓ Personalized learning path matching your exact skill level</li>
                <li>✓ Redundant resource avoidance for previously studied topics</li>
                <li>✓ Capacity-aware planning fitting real-world available hours</li>
                <li>✓ Goal-focused curated resource filtering</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # 3. RESPONSIBLE AI & ARCHITECTURE EXPLAINERS
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1, st.expander("🛡️ Responsible AI & System Limitations"):
            st.markdown("""
            - **Self-Reported Skill Levels**: Initial skill levels are self-reported unless supported by listed courses or projects.
            - **Curated Dataset Boundaries**: Resource recommendations are drawn from our curated catalog of verified learning resources.
            - **Educational Guidance**: Recommendations provide algorithmic data-driven decision support; the system is not an authoritative career decision-maker.
            - **Offline Fallback Safety**: In environments without an active API key, an offline hash vectorizer ensures stable prototype operation.
            """)

        with col_exp2, st.expander("⚙️ How Compass Works (System Architecture & AI Split)"):
            st.markdown("""
                **Pipeline Data Flow:**
                `USER PROFILE ➔ SKILL GAP ENGINE ➔ PRIORITY ENGINE ➔ ROADMAP ENGINE ➔ EMBEDDINGS ➔ FAISS INDEX ➔ RAG RETRIEVAL ➔ RESOURCE RANKING ➔ COMPASS RECOMMENDATION`

                **Deterministic Components:**
                - Skill gap calculation & gap distance mapping
                - Priority scoring formula & prerequisite protection
                - Capacity workload & deadline constraint scheduling
                - Hard resource constraint filtering (Budget, Language)

                **AI Components:**
                - Gemini text embeddings (with offline hash vectorizer fallback)
                - FAISS vector similarity search
                - Contextual recommendation explanations
                - Conversational decision support evaluator
                """)

    # =========================================================================
    # TAB 2: SKILL GAP
    # =========================================================================
    with tab_gap:
        st.markdown(f"### 📍 CURRENT POSITION: Skill Gap Analysis for **{gap_report.goal}**")

        col_e, col_n, col_m = st.columns(3)
        with col_e:
            st.markdown(f"#### ✅ Ready Skills ({len(gap_report.existing_skills)})")
            for s in gap_report.existing_skills:
                st.markdown(
                    f"- **{s.skill}**: `{s.user_level.capitalize()}` $\\rightarrow$ `{s.required_level.capitalize()}` "
                    f"(Gap: {s.gap_score}) `<span class='status-existing'>✓ Ready</span>`",
                    unsafe_allow_html=True
                )
        with col_n:
            st.markdown(f"#### ⚠️ Needs Improvement ({len(gap_report.needs_improvement_skills)})")
            for s in gap_report.needs_improvement_skills:
                st.markdown(
                    f"- **{s.skill}**: `{s.user_level.capitalize()}` $\\rightarrow$ `{s.required_level.capitalize()}` "
                    f"(Gap: {s.gap_score}) `<span class='status-needs-imp'>⚠️ Needs Improvement</span>`",
                    unsafe_allow_html=True
                )
        with col_m:
            st.markdown(f"#### ✕ Missing Skills ({len(gap_report.missing_skills)})")
            for s in gap_report.missing_skills:
                st.markdown(
                    f"- **{s.skill}**: `None` $\\rightarrow$ `{s.required_level.capitalize()}` "
                    f"(Gap: {s.gap_score}) `<span class='status-missing'>✕ Missing</span>`",
                    unsafe_allow_html=True
                )

        st.markdown("---")
        st.markdown("#### 🔬 Detailed Knowledge & Exposure Breakdown")
        for item in gap_report.existing_skills + gap_report.needs_improvement_skills + gap_report.missing_skills:
            with st.expander(f"Skill Assessment: **{item.skill}** ({item.status})"):
                st.markdown(f"- **Required Level:** `{item.required_level.capitalize()}` (Importance: `{item.importance}/10`) ")
                st.markdown(f"- **User Current Level:** `{item.user_level.capitalize()}` (Confidence: `{item.confidence}`) ")
                st.markdown(f"- **Numerical Gap:** `{item.gap_score}` step(s)")
                st.markdown(f"- **Reason:** {item.reason}")
                if item.exposure_evidence:
                    st.markdown(f"- **Prior Exposure Evidence:** `{', '.join(item.exposure_evidence)}`")

    # =========================================================================
    # TAB 3: YOUR DIRECTION (PRIORITY ENGINE)
    # =========================================================================
    with tab_prio:
        st.markdown("### 🎯 YOUR DIRECTION: Deterministic Priority Skill Matrix")

        t_now, t_next, t_later, t_skip = st.tabs([
            f"🔥 NOW ({len(priority_report.now)})",
            f"🔜 NEXT ({len(priority_report.next_skills)})",
            f"⏳ LATER ({len(priority_report.later)})",
            f"⏩ SKIP ({len(priority_report.skip)})"
        ])

        def render_priority_items(items, border_color, category_title):
            if not items:
                st.info(f"No skills currently in {category_title} category.")
                return
            for s in items:
                est_h = hours_by_skill.get(s.skill.lower(), 15)
                prereq_str = ", ".join(s.prerequisites) if s.prerequisites else "None"
                reasons_html = "".join(f"<li style='margin-bottom:2px;'>{r}</li>" for r in getattr(s, "structured_reasons", []))
                reasons_block = f"<ul style='margin:0.3rem 0; padding-left:1.2rem; font-size:0.88rem; color:#CBD5E1;'>{reasons_html}</ul>" if reasons_html else ""

                st.markdown(f"""
                <div class="priority-card" style="border-left-color:{border_color};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#F8FAFC;">{category_title} {s.skill}</h4>
                        <span style="background:rgba(255,255,255,0.1); color:#38BDF8; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.85rem;">Priority Score: {s.priority_score}</span>
                    </div>
                    <p style="margin:0.4rem 0 0.2rem 0; font-size:0.92rem; color:#CBD5E1;"><strong>Why this priority?</strong> {s.reasoning}</p>
                    {reasons_block}
                    <p style="margin:0.3rem 0 0 0; font-size:0.85rem; color:#94A3B8;">⏱️ <strong>Estimated Effort:</strong> {est_h} Hours | 🔗 <strong>Prerequisites:</strong> {prereq_str}</p>
                </div>
                """, unsafe_allow_html=True)

                # "WHY THIS?" PANEL WITH TECHNICAL BREAKDOWN
                with st.expander(f"💡 Why is '{s.skill}' assigned priority score {s.priority_score}? (Click for score breakdown)"):
                    st.markdown(f"**Grounded Explanation:** {s.reasoning}")
                    if s.score_breakdown:
                        b = s.score_breakdown
                        st.markdown("##### 🔬 Technical Score Breakdown:")
                        bk1, bk2, bk3, bk4 = st.columns(4)
                        with bk1:
                            st.metric("Base Raw Score", f"{b.base_score}")
                            st.metric("Goal Weight", f"{b.goal_contribution}")
                        with bk2:
                            st.metric("Gap Step Distance", f"{b.gap_contribution}")
                            st.metric("Prerequisite Factor", f"{b.prerequisite_contribution}")
                        with bk3:
                            st.metric("Weak Area Boost", f"+{b.weak_area_adjustment}" if b.weak_area_adjustment > 0 else "0.0")
                            st.metric("User Priority Boost", f"+{b.user_priority_adjustment}" if b.user_priority_adjustment > 0 else "0.0")
                        with bk4:
                            st.metric("Postpone Penalty", f"{b.postpone_adjustment}" if b.postpone_adjustment != 0 else "0.0")
                            st.metric("Final Priority Score", f"{b.final_score}")

        with t_now:
            render_priority_items(priority_report.now, "#10B981", "🔥")
        with t_next:
            render_priority_items(priority_report.next_skills, "#F59E0B", "🔜")
        with t_later:
            render_priority_items(priority_report.later, "#64748B", "⏳")
        with t_skip:
            if priority_report.skip:
                for s in priority_report.skip:
                    st.markdown(f"""
                    <div class="priority-card" style="border-left-color:#10B981;">
                        <h4 style="margin:0; color:#F8FAFC;">⏩ {s.skill} (Skill Mastered)</h4>
                        <p style="margin:0.3rem 0 0 0; font-size:0.9rem; color:#CBD5E1;">{s.reasoning}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No skills in SKIP category.")

    # =========================================================================
    # TAB 4: ROADMAP
    # =========================================================================
    with tab_roadmap:
        st.markdown(f"### 🗺️ YOUR ROUTE: Weekly Study Schedule ({roadmap_report.total_weeks_allocated} Weeks Allocated)")

        # CAPACITY WARNING CALLOUT BANNER
        if roadmap_report.capacity_tradeoff_explanation:
            if roadmap_report.overflow_items:
                st.warning(f"⚖️ **Capacity Tradeoff Notice**: {roadmap_report.capacity_tradeoff_explanation}")
            else:
                st.info(f"💡 **Capacity Notice**: {roadmap_report.capacity_tradeoff_explanation}")

        for item in roadmap_report.items:
            p_badge = "🔴 HIGH PRIORITY" if item.priority_category == "NOW" else ("🟡 MEDIUM PRIORITY" if item.priority_category == "NEXT" else "🔵 ELECTIVE")
            prereq_str = ", ".join(item.prerequisites) if item.prerequisites else "None"

            with st.expander(f"📍 **WEEK {item.week_start}–{item.week_end}: {item.skill}** — {p_badge}", expanded=True):
                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    st.markdown(f"⏱️ **Estimated Effort:** `{item.estimated_hours} Hours` (at {profile.hours_per_week}h/week)")
                    st.markdown(f"⏱️ **Recommended Session Duration:** `{item.recommended_session_length}`")
                    st.markdown(f"🔗 **Prerequisites:** `{prereq_str}`")
                with r_col2:
                    st.markdown(f"🎯 **Milestone Target:** {item.milestone}")
                    st.markdown(f"💡 **Why Scheduled Here:** {item.why_now}")

                # Milestone Progress Radio
                curr_m_status = st.session_state.milestone_status.get(item.skill, "Not started")
                status_sel = st.radio(
                    f"Milestone Progress for {item.skill}:",
                    ["Not started", "In progress", "Completed"],
                    index=["Not started", "In progress", "Completed"].index(curr_m_status),
                    horizontal=True,
                    key=f"m_status_tab4_{item.skill}"
                )
                if status_sel != curr_m_status:
                    st.session_state.milestone_status[item.skill] = status_sel
                    st.rerun()

    # =========================================================================
    # TAB 5: RESOURCES (RAG RANKING)
    # =========================================================================
    with tab_resources:
        st.markdown("### 📚 RESOURCES: Curated RAG Recommendations")

        # Interactive RAG Filters Header
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            filter_lang = st.selectbox("Language Filter", ["All", "English", "Hindi"], index=0, key="res_lang_sel")
        with f_col2:
            filter_cost = st.selectbox("Cost Filter", ["All", "Free", "Paid"], index=0, key="res_cost_sel")
        with f_col3:
            filter_format = st.selectbox("Format Filter", ["All", "Video", "Course", "Book", "Documentation", "Interactive"], index=0, key="res_fmt_sel")
        with f_col4:
            filter_diff = st.selectbox("Difficulty Filter", ["All", "Beginner", "Intermediate", "Advanced"], index=0, key="res_diff_sel")

        filter_profile = profile.model_copy()
        if filter_lang != "All":
            filter_profile.language = [filter_lang]
        if filter_cost != "All":
            filter_profile.budget = filter_cost.lower()
        if filter_format != "All":
            filter_profile.learning_format = filter_format.lower()

        for item in roadmap_report.items:
            st.markdown(f"#### Recommended Learning Resources for **{item.skill}**")
            ranked_resources = filter_and_rank_resources(
                skill_name=item.skill,
                required_level="intermediate" if filter_diff == "All" else filter_diff.lower(),
                profile=filter_profile,
                retriever=st.session_state.retriever,
                top_k=3
            )

            if not ranked_resources:
                st.info(f"No resources matched active filters for {item.skill}. Try broadening your search filters above.")

            for rank_idx, res in enumerate(ranked_resources):
                doc = res.resource
                rec_label = "⭐ RECOMMENDED FOR YOU" if rank_idx == 0 else "ALTERNATIVE RESOURCE"
                rec_badge_color = "#0284C7" if rank_idx == 0 else "#334155"

                exp, exp_provider = generate_recommendation_explanation(
                    skill_name=item.skill,
                    priority_category=item.priority_category,
                    roadmap_weeks=f"Week {item.week_start}-{item.week_end}",
                    resource=doc,
                    profile=filter_profile
                )

                st.markdown(f"""
                <div class="resource-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#38BDF8;"><a href="{doc.url}" target="_blank" style="color:#38BDF8; text-decoration:none;">🔗 {doc.title}</a></h4>
                        <span style="background:{rec_badge_color}; color:white; padding:2px 10px; border-radius:10px; font-size:0.78rem; font-weight:700;">{rec_label}</span>
                    </div>
                    <p style="margin: 0.4rem 0; font-size:0.88rem; color:#CBD5E1;">
                        <strong>Provider:</strong> {doc.provider} | <strong>Format:</strong> {doc.format.capitalize()} | 
                        <strong>Cost:</strong> {doc.cost.capitalize()} | <strong>Language:</strong> {doc.language} | 
                        <strong>Duration:</strong> {doc.duration}
                    </p>
                    <div style="background:rgba(15, 23, 42, 0.6); padding:0.8rem; border-radius:6px; margin-top:0.4rem;">
                        <p style="font-size:0.88rem; margin:0; color:#E2E8F0;">💡 <strong>Why Recommended:</strong> {res.fit_explanation}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"View technical matching details ({exp_provider})"):
                    st.markdown(f"- **Final Composite Score:** `{res.final_score}`")
                    st.markdown(f"- **Vector Similarity:** `{res.vector_similarity}`")
                    st.markdown(f"- **Skill & Level Match Score:** `{res.skill_match_score}`")
                    st.markdown(f"- **Budget Fit Score:** `{res.budget_fit_score}`")
                    st.markdown(f"- **Language Fit Score:** `{res.language_fit_score}`")
                    st.markdown(f"- **Matched User Preferences:** `{', '.join(res.matched_preferences)}`")
                    st.markdown(f"- **LLM Recommendation Context ({exp_provider}):**\n{exp}")

    # =========================================================================
    # TAB 6: ASK COMPASS (DECISION SUPPORT)
    # =========================================================================
    with tab_ask:
        st.markdown("### 🤔 ASK COMPASS: Conversational Decision Support")
        st.markdown("Ask any skill or sequence question to evaluate alignment with your current goal, capacity, and prerequisites:")

        # Quick Example Query Buttons
        st.markdown("**Quick Example Questions:**")
        q_cols = st.columns(3)
        with q_cols[0]:
            if st.button("Should I learn Kafka now?", use_container_width=True):
                st.session_state.selected_query = "Should I learn Kafka now?"
        with q_cols[1]:
            if st.button("Can I skip SQL?", use_container_width=True):
                st.session_state.selected_query = "Can I skip SQL?"
        with q_cols[2]:
            if st.button("Should I learn Spark before Databricks?", use_container_width=True):
                st.session_state.selected_query = "Should I learn Spark before Databricks?"

        query_x = st.text_input(
            "Type your query:",
            value=st.session_state.get("selected_query", ""),
            key="ask_compass_input"
        )

        if query_x:
            agent = CompassAgent(profile, retriever=st.session_state.retriever)
            agent_log = agent.run(query_x)

            prio_data = agent_log.tool_outputs.get("evaluate_skill_priority", {})
            badge_class = (
                "verdict-success" if prio_data.get("priority_tier") == "NOW" 
                else ("verdict-warning" if prio_data.get("priority_tier") in ["NEXT", "LATER"] else "verdict-error")
            )

            st.markdown(f"""
            <div class="{badge_class}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.1rem;">{agent_log.final_verdict}</span>
                    <span style="background:rgba(255,255,255,0.2); padding:2px 10px; border-radius:12px; font-weight:700;">Priority Tier: {agent_log.priority_tier}</span>
                </div>
            </div>
            <p style="font-size:0.8rem; color:#94A3B8; margin-top:4px;">{agent_log.provider_source}</p>
            """, unsafe_allow_html=True)

            st.markdown(f"🎯 **Target Skill Evaluated:** `{prio_data.get('query_skill')}` | 📊 **Relevance Score:** `{prio_data.get('relevance_score')}/10`")
            st.markdown(f"⏱️ **Timing Guidance:** `{prio_data.get('recommendation_timing')}`")
            st.markdown(f"💡 **Tradeoff & Opportunity Cost:** {prio_data.get('tradeoff_analysis')}")

            if agent_log.answer_text:
                st.markdown(f"🗣️ **Agent Response:**\n{agent_log.answer_text}")

            with st.expander("🛠️ View Agent Execution Trace & Tools Invoked"):
                st.markdown("**Tools Executed by Compass Agent:**")
                for t in agent_log.tools_invoked:
                    st.markdown(f"- ✓ `{t}`")
                st.json(agent_log.tool_outputs)

    # =========================================================================
    # TAB 7: PROGRESS TRACKER & RE-ROUTE
    # =========================================================================
    with tab_progress:
        st.markdown("### 📈 PROGRESS TRACKER: Milestone Tracking & Capacity Re-Routing")

        total_roadmap_items = len(roadmap_report.items)
        completed_skills = [
            item.skill for item in roadmap_report.items 
            if st.session_state.milestone_status.get(item.skill) == "Completed"
        ]
        completed_count = len(completed_skills)
        in_progress_count = sum(
            1 for item in roadmap_report.items 
            if st.session_state.milestone_status.get(item.skill) == "In progress"
        )
        roadmap_completion_pct = int((completed_count / max(1, total_roadmap_items)) * 100)

        # Milestone Progress Overview Metrics
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        with p_col1:
            st.metric("Milestone Completion", f"{roadmap_completion_pct}%")
        with p_col2:
            st.metric("Completed Milestones", f"{completed_count} / {total_roadmap_items}")
        with p_col3:
            st.metric("In Progress Milestones", f"{in_progress_count}")
        with p_col4:
            active_item = next((i.skill for i in roadmap_report.items if st.session_state.milestone_status.get(i.skill) != "Completed"), "All Completed")
            st.metric("Current Active Milestone", active_item)

        st.progress(roadmap_completion_pct / 100.0)

        st.markdown("---")
        st.markdown("#### 🔄 Re-Route / Available Capacity Adjustment")
        st.markdown("If your weekly available study hours or schedule change, adapt your roadmap dynamically below:")

        c_reroute1, c_reroute2 = st.columns(2)
        with c_reroute1:
            new_weekly_hours = st.number_input(
                "Update Available Weekly Study Hours",
                min_value=1,
                max_value=100,
                value=int(profile.hours_per_week),
                key="progress_reroute_hours"
            )
            current_week_num = st.number_input(
                "Current Week Number",
                min_value=1,
                max_value=24,
                value=1,
                key="progress_reroute_week"
            )
        with c_reroute2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Adapt Roadmap (Re-Route)", type="primary", key="progress_adapt_btn"):
                adapt_rep = adapt_roadmap_progress(
                    profile=profile,
                    completed_skills=completed_skills,
                    current_week=current_week_num,
                    new_hours_per_week=new_weekly_hours
                )
                st.session_state.profile = adapt_rep.updated_profile
                st.session_state.adaptation_report = adapt_rep
                st.rerun()

        if "adaptation_report" in st.session_state and st.session_state.adaptation_report:
            ad_rep = st.session_state.adaptation_report
            st.info(f"⚡ **ROADMAP ADAPTED ({ad_rep.status})**: {ad_rep.adaptation_summary}")
