"""Browser UI for the ITI Lucknow placement agent.

This is the screen you can record for the demo video: login/signup first,
then a dashboard that lists aggregated jobs from multiple sources and shows
matching plus outreach details.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List

import streamlit as st

from iti_placement_agent.data import SAMPLE_CANDIDATES
from iti_placement_agent.engine import ITIJobAgent
from iti_placement_agent.job_sources import JOB_SOURCES, build_source_jobs
from iti_placement_agent.models import CandidateProfile, JobOpening


def load_job_feed() -> List[JobOpening]:
    """Build the dashboard feed from multiple named sources."""
    return build_source_jobs()


def setup_page() -> None:
    st.set_page_config(page_title="ITI Placement Agent", page_icon="🎯", layout="wide")
    st.markdown(
        """
        <style>
        :root {
            --bg: #eef3fb;
            --panel: #ffffff;
            --ink: #0f172a;
            --muted: #64748b;
            --brand: #2563eb;
            --brand-soft: #dbeafe;
            --brand-2: #0f766e;
            --line: #dbe3ef;
            --accent: #ea580c;
            --accent-soft: #fff7ed;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.16), transparent 28%),
                radial-gradient(circle at top right, rgba(234, 88, 12, 0.10), transparent 24%),
                radial-gradient(circle at bottom right, rgba(15, 118, 110, 0.08), transparent 28%),
                var(--bg);
            color: var(--ink);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #091120 0%, #111827 100%);
            color: white;
        }

        [data-testid="stSidebar"] * {
            color: #e5e7eb;
        }

        .app-shell {
            border: 1px solid var(--line);
            border-radius: 24px;
            background: rgba(255,255,255,0.84);
            backdrop-filter: blur(12px);
            padding: 1rem 1.15rem;
            box-shadow: 0 18px 44px rgba(15, 23, 42, 0.10);
        }

        .hero-title {
            font-size: 2.35rem;
            font-weight: 850;
            letter-spacing: -0.04em;
            margin-bottom: 0.2rem;
        }

        .hero-subtitle {
            color: var(--muted);
            font-size: 1.0rem;
            max-width: 900px;
        }

        .metric-card {
            background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 1rem 1rem 0.9rem 1rem;
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.06);
            min-height: 100px;
        }

        .source-pill {
            display: inline-block;
            padding: 0.22rem 0.55rem;
            border-radius: 999px;
            background: var(--brand-soft);
            color: var(--brand);
            font-size: 0.77rem;
            font-weight: 700;
            margin-right: 0.35rem;
            margin-bottom: 0.25rem;
        }

        .source-pill.alt {
            background: var(--accent-soft);
            color: #c2410c;
        }

        .section-title {
            font-size: 1.08rem;
            font-weight: 780;
            margin: 0.1rem 0 0.55rem 0;
        }

        .small-muted {
            color: var(--muted);
            font-size: 0.86rem;
        }

        .job-card {
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 0.95rem 1rem;
            background: #fff;
            margin-bottom: 0.72rem;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.045);
        }

        .job-title {
            font-size: 1.02rem;
            font-weight: 750;
        }

        .hero-banner {
            border-radius: 22px;
            padding: 1.1rem 1.25rem;
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 52%, #0f766e 100%);
            color: white;
            box-shadow: 0 16px 30px rgba(15, 23, 42, 0.18);
            margin-bottom: 1rem;
        }

        .hero-banner .hero-title,
        .hero-banner .hero-subtitle {
            color: white;
            margin: 0;
        }

        .badge-row {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin-top: 0.6rem;
        }

        .badge-soft {
            display: inline-block;
            padding: 0.30rem 0.62rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.20);
            color: white;
            font-size: 0.8rem;
            font-weight: 650;
        }

        .profile-box {
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            background: linear-gradient(180deg, #fff 0%, #fbfdff 100%);
            box-shadow: 0 8px 16px rgba(15, 23, 42, 0.05);
        }

        .divider-soft {
            height: 1px;
            background: linear-gradient(90deg, transparent, #dbe3ef, transparent);
            margin: 0.9rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_auth_state() -> None:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = ""
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    if "profile_saved" not in st.session_state:
        st.session_state.profile_saved = False
    if "profile_data" not in st.session_state:
        st.session_state.profile_data = {
            "name": SAMPLE_CANDIDATES[0].name,
            "trade": SAMPLE_CANDIDATES[0].trade,
            "institute": SAMPLE_CANDIDATES[0].institute,
            "location": SAMPLE_CANDIDATES[0].location,
            "skills": ", ".join(SAMPLE_CANDIDATES[0].skills),
            "preferred_roles": ", ".join(SAMPLE_CANDIDATES[0].preferred_roles),
            "expected_salary_inr": SAMPLE_CANDIDATES[0].expected_salary_inr,
            "years_experience": SAMPLE_CANDIDATES[0].years_experience,
        }
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "auto_apply": False,
            "email_alerts": True,
            "share_profile": True,
            "preferred_source_focus": "All Sources",
        }


def build_candidate_from_profile() -> CandidateProfile:
    profile = st.session_state.profile_data
    skills = [skill.strip() for skill in profile["skills"].split(",") if skill.strip()]
    preferred_roles = [role.strip() for role in profile["preferred_roles"].split(",") if role.strip()]
    return CandidateProfile(
        candidate_id=st.session_state.current_user or "cand-profile",
        name=profile["name"].strip() or SAMPLE_CANDIDATES[0].name,
        trade=profile["trade"].strip() or SAMPLE_CANDIDATES[0].trade,
        institute=profile["institute"].strip() or SAMPLE_CANDIDATES[0].institute,
        location=profile["location"].strip() or SAMPLE_CANDIDATES[0].location,
        skills=skills or SAMPLE_CANDIDATES[0].skills,
        preferred_roles=preferred_roles or SAMPLE_CANDIDATES[0].preferred_roles,
        expected_salary_inr=int(profile["expected_salary_inr"] or SAMPLE_CANDIDATES[0].expected_salary_inr),
        years_experience=float(profile["years_experience"] or SAMPLE_CANDIDATES[0].years_experience),
    )


def profile_completion(candidate: CandidateProfile) -> int:
    filled = sum(
        1
        for value in [
            candidate.name,
            candidate.trade,
            candidate.institute,
            candidate.location,
            candidate.skills,
            candidate.preferred_roles,
            candidate.expected_salary_inr,
            candidate.years_experience,
        ]
        if value
    )
    return int((filled / 8) * 100)


def show_auth_screen() -> None:
    """Simple login/signup gate for the demo video.

    This is intentionally lightweight: for a hackathon demo we only need a
    believable auth flow, not a full backend identity system.
    """
    col_left, col_right = st.columns([1.1, 0.9], gap="large")

    with col_left:
        st.markdown(
            """
            <div class="hero-banner">
                <div class="hero-title">ITI Lucknow Placement Agent</div>
                <div class="hero-subtitle">A browser-based assistant for matching ITI graduates with live jobs from company portals, Unstop, CourseJoiner, and government platforms.</div>
                <div class="badge-row">
                    <span class="badge-soft">Login first</span>
                    <span class="badge-soft">Save profile</span>
                    <span class="badge-soft">Match similar jobs</span>
                    <span class="badge-soft">Track placements</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info("Use the login/signup panel on the right. After sign-in, the dashboard opens with your profile and similar jobs.")

    with col_right:
        with st.container(border=True):
            st.markdown("### Login / Sign up")
            with st.form("auth_form", clear_on_submit=False):
                mode = st.radio("Choose mode", ["Login", "Sign up"], horizontal=True, key="auth_mode_selector")
                st.session_state.auth_mode = mode.lower()
                username = st.text_input("Email or username", placeholder="student@iti.ac.in", key="auth_username")
                password = st.text_input("Password", type="password", placeholder="••••••••", key="auth_password")
                confirm_password = None
                if mode == "Sign up":
                    confirm_password = st.text_input("Confirm password", type="password", placeholder="••••••••", key="auth_confirm_password")
                submitted = st.form_submit_button("Continue", use_container_width=True)

            if submitted:
                if not username.strip() or not password.strip():
                    st.warning("Please enter both username and password.")
                elif mode == "Sign up" and confirm_password != password:
                    st.warning("Passwords do not match.")
                else:
                    st.session_state.current_user = username.strip()
                    st.session_state.authenticated = True
                    st.rerun()

        with st.container(border=True):
            st.markdown("#### What you get after login")
            st.write("• A clean dashboard with strong visual hierarchy")
            st.write("• Sidebar profile and settings")
            st.write("• Saved preferences used to recommend similar jobs")
            st.write("• Source-wise job feed from portals and government platforms")


def render_sidebar(job_feed: List[JobOpening]) -> None:
    """Show the left navigation and source summary."""
    st.sidebar.markdown("## ITI Portal")
    st.sidebar.caption(f"Welcome, {st.session_state.current_user or 'User'}")
    st.sidebar.divider()

    st.sidebar.markdown("### Profile")
    candidate = build_candidate_from_profile()
    st.sidebar.write(candidate.name)
    st.sidebar.caption(candidate.trade)
    st.sidebar.caption(candidate.location)
    st.sidebar.progress(profile_completion(candidate) / 100)
    st.sidebar.caption(f"Profile completeness: {profile_completion(candidate)}%")

    with st.sidebar.expander("Profile settings", expanded=True):
        st.session_state.profile_data["name"] = st.text_input("Full name", value=st.session_state.profile_data["name"])
        st.session_state.profile_data["trade"] = st.selectbox(
            "Trade",
            ["Electrician", "Fitter", "Welder", "Plumber", "Carpenter", "Mechanic", "IT Technician"],
            index=["Electrician", "Fitter", "Welder", "Plumber", "Carpenter", "Mechanic", "IT Technician"].index(st.session_state.profile_data["trade"])
            if st.session_state.profile_data["trade"] in ["Electrician", "Fitter", "Welder", "Plumber", "Carpenter", "Mechanic", "IT Technician"]
            else 0,
        )
        st.session_state.profile_data["institute"] = st.text_input("Institute", value=st.session_state.profile_data["institute"])
        st.session_state.profile_data["location"] = st.text_input("Location", value=st.session_state.profile_data["location"])
        st.session_state.profile_data["skills"] = st.text_area("Skills", value=st.session_state.profile_data["skills"], height=100)
        st.session_state.profile_data["preferred_roles"] = st.text_area("Preferred roles", value=st.session_state.profile_data["preferred_roles"], height=70)
        st.session_state.profile_data["expected_salary_inr"] = st.number_input("Expected salary (INR)", min_value=0, step=500, value=int(st.session_state.profile_data["expected_salary_inr"]))
        st.session_state.profile_data["years_experience"] = st.number_input("Years of experience", min_value=0.0, step=0.5, value=float(st.session_state.profile_data["years_experience"]))

        if st.button("Save profile", use_container_width=True):
            st.session_state.profile_saved = True
            st.success("Profile saved. The matcher will now use these details.")

    with st.sidebar.expander("Settings", expanded=False):
        st.session_state.settings["auto_apply"] = st.checkbox("Auto apply to best matches", value=st.session_state.settings["auto_apply"])
        st.session_state.settings["email_alerts"] = st.checkbox("Email alerts", value=st.session_state.settings["email_alerts"])
        st.session_state.settings["share_profile"] = st.checkbox("Share profile with recruiters", value=st.session_state.settings["share_profile"])
        st.session_state.settings["preferred_source_focus"] = st.selectbox(
            "Focus source",
            ["All Sources"] + [source.name for source in JOB_SOURCES],
            index=( ["All Sources"] + [source.name for source in JOB_SOURCES] ).index(st.session_state.settings["preferred_source_focus"])
            if st.session_state.settings["preferred_source_focus"] in (["All Sources"] + [source.name for source in JOB_SOURCES])
            else 0,
        )

    st.sidebar.divider()
    st.sidebar.markdown("### Sources")
    for source in JOB_SOURCES:
        st.sidebar.markdown(f"**{source.name}**  ")
        st.sidebar.caption(source.description)

    st.sidebar.divider()
    st.sidebar.markdown("### Navigation")
    st.sidebar.write("Dashboard")
    st.sidebar.write("Profile")
    st.sidebar.write("Settings")
    st.sidebar.write("Application Management")
    st.sidebar.write("Government Internships")
    st.sidebar.write("Live Jobs")
    st.sidebar.write("Logout")

    st.sidebar.divider()
    st.sidebar.metric("Live jobs", len(job_feed))
    st.sidebar.metric("Sources", len(JOB_SOURCES))

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_user = ""
        st.rerun()


def render_dashboard(agent: ITIJobAgent, candidate: CandidateProfile, job_feed: List[JobOpening]) -> None:
    """Render the main dashboard after login."""
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">Dashboard</div>
            <div class="hero-subtitle">Live jobs collected from multiple job sources and matched to ITI Lucknow skills.</div>
            <div class="badge-row">
                <span class="badge-soft">Profile-driven</span>
                <span class="badge-soft">Source tagged</span>
                <span class="badge-soft">Similar jobs</span>
                <span class="badge-soft">Placement flow</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    top_left, top_mid, top_right, top_four = st.columns(4)

    ranked = agent.match_jobs(candidate, job_feed, top_k=5)
    source_count = len({job.source for job in job_feed})
    completion = profile_completion(candidate)
    top_left.markdown(f'<div class="metric-card"><div class="small-muted">Profile used</div><h2>{candidate.name}</h2><div class="small-muted">{candidate.trade} · {candidate.location}</div></div>', unsafe_allow_html=True)
    top_mid.markdown(f'<div class="metric-card"><div class="small-muted">Jobs available</div><h2>{len(job_feed)}</h2><div class="small-muted">Across {source_count} sources</div></div>', unsafe_allow_html=True)
    top_right.markdown(f'<div class="metric-card"><div class="small-muted">Top matches ready</div><h2>{len(ranked)}</h2><div class="small-muted">Auto-ranked by fit score</div></div>', unsafe_allow_html=True)
    top_four.markdown(f'<div class="metric-card"><div class="small-muted">Profile completion</div><h2>{completion}%</h2><div class="small-muted">Saved details improve matching</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    profile_col, jobs_col, insight_col = st.columns([0.8, 1.25, 0.95], gap="large")

    with profile_col:
        st.markdown('<div class="section-title">User profile</div>', unsafe_allow_html=True)
        st.markdown(
            f'''
            <div class="profile-box">
                <div class="job-title">{candidate.name}</div>
                <div class="small-muted">{candidate.institute}</div>
                <div class="divider-soft"></div>
                <div><strong>Trade:</strong> {candidate.trade}</div>
                <div><strong>Location:</strong> {candidate.location}</div>
                <div><strong>Experience:</strong> {candidate.years_experience} years</div>
                <div><strong>Salary:</strong> INR {candidate.expected_salary_inr}</div>
                <div class="divider-soft"></div>
                <div class="small-muted"><strong>Skills:</strong> {', '.join(candidate.skills[:6])}</div>
                <div class="small-muted" style="margin-top:0.35rem;"><strong>Preferred roles:</strong> {', '.join(candidate.preferred_roles) if candidate.preferred_roles else 'Not set'}</div>
            </div>
            '''
            ,
            unsafe_allow_html=True,
        )

        st.markdown('<div style="height:0.7rem"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Quick actions</div>', unsafe_allow_html=True)
        st.button("Save profile to session", use_container_width=True)
        st.button("Open settings", use_container_width=True)

    with jobs_col:
        st.markdown('<div class="section-title">Similar jobs and live feed</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-muted">Jobs are shown from multiple sources. Similar jobs for the saved profile appear first.</div>', unsafe_allow_html=True)

        source_focus = st.session_state.settings.get("preferred_source_focus", "All Sources")
        filtered_jobs = [job for job in job_feed if source_focus == "All Sources" or job.source == source_focus]
        if source_focus != "All Sources":
            st.caption(f"Filtered to source: {source_focus}")

        ranked_feed = []
        for job in filtered_jobs:
            score, diagnostics = agent.score_job_match(candidate, job)
            ranked_feed.append((score, diagnostics, job))
        ranked_feed.sort(key=lambda item: item[0], reverse=True)

        if not ranked_feed:
            st.info("No jobs match the current source filter.")

        for score, diagnostics, job in ranked_feed:
            source_label = f'<span class="source-pill">{job.source}</span>'
            if score >= 0.8:
                source_label += ' <span class="source-pill alt">best fit</span>'
            st.markdown(
                f'''
                <div class="job-card">
                    <div class="job-title">{job.title}</div>
                    <div class="small-muted">{job.company} · {job.location}</div>
                    <div style="margin-top:0.45rem; margin-bottom:0.35rem;">{source_label}</div>
                    <div class="small-muted">Skills: {', '.join(job.required_skills)}</div>
                    <div class="small-muted">Score for {candidate.name}: {score}</div>
                </div>
                '''
                ,
                unsafe_allow_html=True,
            )

    with insight_col:
        st.markdown('<div class="section-title">Best matches</div>', unsafe_allow_html=True)
        st.dataframe(
            [
                {
                    "Rank": index + 1,
                    "Job Title": item.job["title"],
                    "Company": item.job["company"],
                    "Source": item.job["source"],
                    "Fit": item.fit_label,
                    "Score": item.score,
                }
                for index, item in enumerate(ranked)
            ],
            use_container_width=True,
            hide_index=True,
        )

        if ranked:
            best_match = ranked[0]
            best_job = JobOpening(**best_match.job)
            st.markdown('<div class="section-title">Outreach draft</div>', unsafe_allow_html=True)
            st.code(agent.draft_outreach_message(candidate, best_job, best_match.score), language="text")

            st.markdown('<div class="section-title">Placement flow</div>', unsafe_allow_html=True)
            st.write("1. Save profile details")
            st.write("2. Match candidate to similar jobs")
            st.write("3. Draft outreach to recruiter")
            st.write("4. Track placement status")
            st.write("5. Export results for the final report")

        st.markdown('<div style="height:0.4rem"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Saved settings</div>', unsafe_allow_html=True)
        st.write(f"Auto apply: {'On' if st.session_state.settings['auto_apply'] else 'Off'}")
        st.write(f"Email alerts: {'On' if st.session_state.settings['email_alerts'] else 'Off'}")
        st.write(f"Share profile: {'On' if st.session_state.settings['share_profile'] else 'Off'}")

        st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
        st.info("Edit the profile in the sidebar, then use the dashboard to see similar jobs reorder automatically.")


def main() -> None:
    setup_page()
    ensure_auth_state()

    job_feed = load_job_feed()
    agent = ITIJobAgent()
    candidate = build_candidate_from_profile()

    if not st.session_state.authenticated:
        show_auth_screen()
        return

    render_sidebar(job_feed)
    candidate = build_candidate_from_profile()
    render_dashboard(agent, candidate, job_feed)


if __name__ == "__main__":
    main()