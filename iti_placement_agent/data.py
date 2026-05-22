"""Sample data used by the demo dashboard.

The values are tuned for the ITI Lucknow + Amausi context so the demo feels
realistic enough for a hackathon video even before you connect live data.
"""

from .models import CandidateProfile, JobOpening


SAMPLE_CANDIDATES = [
    CandidateProfile(
        candidate_id="cand-001",
        name="Aman Kumar",
        trade="Electrician",
        institute="ITI Lucknow",
        location="Amausi, Lucknow",
        skills=["panel wiring", "motor winding", "troubleshooting", "safety compliance", "three phase wiring", "multimeter use"],
        preferred_roles=["maintenance electrician", "industrial technician"],
        expected_salary_inr=18000,
        years_experience=1.5,
    ),
    CandidateProfile(
        candidate_id="cand-002",
        name="Ritika Verma",
        trade="Fitter",
        institute="ITI Lucknow",
        location="Charbagh, Lucknow",
        skills=["machine fitting", "tool handling", "assembly", "quality inspection", "measurement"],
        preferred_roles=["machine operator", "assembly technician"],
        expected_salary_inr=16000,
        years_experience=1.0,
    ),
]


SAMPLE_JOBS = [
    JobOpening(
        job_id="job-101",
        title="Maintenance Electrician",
        company="Amausi Industrial Works",
        location="Amausi, Lucknow",
        required_skills=["panel wiring", "troubleshooting", "motor winding", "preventive maintenance"],
        preferred_trade="Electrician",
        minimum_experience_years=1.0,
        salary_min_inr=16000,
        salary_max_inr=22000,
        contact_email="hr@amausiworks.example",
    ),
    JobOpening(
        job_id="job-102",
        title="Machine Operator",
        company="North Star Manufacturing",
        location="Chinhat, Lucknow",
        required_skills=["machine setup", "quality check", "material handling"],
        preferred_trade="Fitter",
        minimum_experience_years=0.5,
        salary_min_inr=14000,
        salary_max_inr=18000,
        contact_email="jobs@northstar.example",
    ),
    JobOpening(
        job_id="job-103",
        title="Industrial Technician",
        company="Lucknow Assembly Unit",
        location="Transport Nagar, Lucknow",
        required_skills=["three phase wiring", "multimeter use", "safety compliance", "maintenance"],
        preferred_trade="Electrician",
        minimum_experience_years=1.0,
        salary_min_inr=18000,
        salary_max_inr=25000,
        contact_email="careers@lucknowassembly.example",
    ),
]