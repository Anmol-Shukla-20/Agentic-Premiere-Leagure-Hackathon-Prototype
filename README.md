# ITI Lucknow Placement Agent

## 1. Team Name and Members

Team name: Lucknow_Developers_Giants

Members / GitHub handles:
- Anmol Shukla/ https://github.com/Anmol-Shukla-20

## 2. Project Title and Short Description

ITI Lucknow Placement Agent is a browser-based job-matching system for ITI graduates. It helps students save their profile, match their skills to similar jobs, and see relevant openings from multiple sources in a clean dashboard. The app also drafts outreach messages and tracks placement progress so the process feels closer to a real placement assistant.

## 3. Problem Statement Addressed

PS-04 - Skill-to-job matching agent for ITI Lucknow graduates.

ITI Lucknow produces thousands of skilled tradespeople annually who often struggle to find formal employment. This project builds an agent that maps their skills to live job openings, communicates on their behalf, and tracks placement outcomes. The solution is designed around the Lucknow context, especially ITI Lucknow and the Amausi industrial area.

## 4. Tech Stack and Tools Used

Tech stack:
- Python 3.11
- Streamlit for the browser UI
- Standard library modules for scoring, JSON handling, CSV handling, and data modeling

Tools and AI assistance:
- GitHub Copilot for code assistance
- Streamlit for rapid UI development

Data sources and inputs:
- Built-in demo jobs and candidate samples
- `Skill_Job_Matching_Dataset.csv` for benchmark evaluation
- Source-tagged job feeds for company portals, Unstop, CourseJoiner, and government-style job portals

## 5. Setup and Run Instructions

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the browser UI

```bash
streamlit run streamlit_app.py
```

### Run the text demo mode

```bash
python iti_job_agent.py --mode demo
```

### Evaluate the labeled CSV dataset

```bash
python iti_job_agent.py --mode evaluate --dataset-csv "Skill_Job_Matching_Dataset.csv"
```

### Open the dashboard in the browser

After running Streamlit, open the local URL shown in the terminal, usually:

```bash
http://localhost:8501
```

## 6. Known Limitations and Incomplete Features

- The login/signup flow is demo-only and does not use a real authentication backend.
- Job feeds are currently source-tagged demo entries, not live API connectors or scrapers.
- User profile data is saved in the current Streamlit session and is not yet stored in a database.
- The CSV evaluation mode is an offline benchmark, not a live model-training pipeline.
- Recruiter outreach is drafted text only; email/WhatsApp sending is not integrated yet.

## Project Flow

1. The user opens the browser UI and signs up or logs in.
2. The dashboard loads a profile-first view with a sidebar for profile and settings.
3. The app scores jobs from multiple sources and shows similar jobs first.
4. The user can save profile details so matching becomes more personalized.
5. The app generates an outreach draft and tracks placement updates such as applied, shortlisted, or hired.
6. The CSV dataset can be used to benchmark the matching logic and validate that the scoring behaves sensibly.

## Folder Structure

- `iti_job_agent.py` - thin launcher kept at the repo root for easy execution
- `streamlit_app.py` - browser UI with login/signup and dashboard
- `Skill_Job_Matching_Dataset.csv` - labeled benchmark dataset
- `requirements.txt` - dependency list for the UI
- `iti_placement_agent/config.py` - shared constants and skill synonym rules
- `iti_placement_agent/models.py` - dataclasses for candidates, jobs, matches, and outcomes
- `iti_placement_agent/data.py` - sample ITI Lucknow candidates and live-style job openings
- `iti_placement_agent/storage.py` - JSON and CSV input/output helpers
- `iti_placement_agent/engine.py` - scoring, matching, outreach, and outcome tracking
- `iti_placement_agent/dashboard.py` - dashboard helpers for the legacy UI path
- `iti_placement_agent/app.py` - command-line entry point and run modes
- `iti_placement_agent/job_sources.py` - source-tagged demo jobs from portals and company feeds

## Demo Notes

For a good video demo, show these steps:

1. Open the login/signup page.
2. Sign in to enter the dashboard.
3. Show the left sidebar profile section and save a user profile.
4. Show how the similar jobs reorder when the profile details change.
5. Highlight the source labels for company portals, Unstop, CourseJoiner, and government sources.
6. Open the outreach draft and explain how the agent communicates on behalf of the candidate.
