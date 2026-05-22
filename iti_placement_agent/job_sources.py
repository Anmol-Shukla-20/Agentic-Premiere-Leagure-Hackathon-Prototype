"""Job-source helpers for the browser UI.

The goal is not to hard-code one employer feed. Instead, we keep the sources
named and structured so the dashboard can show where each opening came from and
later swap in live ingestion from portals like company career pages, Unstop,
CourseJoiner, and government job boards.
"""

from dataclasses import dataclass
from typing import List

from .models import JobOpening


@dataclass(frozen=True)
class JobSource:
    name: str
    description: str
    url: str
    source_type: str


JOB_SOURCES: List[JobSource] = [
    JobSource(
        name="Company Career Portals",
        description="Direct hiring pages from partner employers and local industries.",
        url="https://company.example/careers",
        source_type="career-portal",
    ),
    JobSource(
        name="Unstop",
        description="Student and fresher opportunities that often fit ITI profiles.",
        url="https://unstop.com",
        source_type="aggregator",
    ),
    JobSource(
        name="CourseJoiner",
        description="Training-linked openings and apprenticeship-style roles.",
        url="https://coursejoiner.com/",
        source_type="aggregator",
    ),
    JobSource(
        name="Government Job Portals",
        description="Government apprenticeships, skill missions, and public recruitment feeds.",
        url="https://gov.example/jobs",
        source_type="govt-portal",
    ),
]


def build_source_jobs() -> List[JobOpening]:
    """Create a source-tagged job feed for the dashboard.

    These are demo entries that make the UI feel like an aggregated live board.
    In the next step, these can be replaced with real scraping/API adapters.
    """
    return [
        JobOpening(
            job_id="portal-101",
            title="ITI Maintenance Electrician",
            company="Amausi Industrial Plant",
            location="Lucknow",
            required_skills=["panel wiring", "troubleshooting", "three phase wiring", "safety compliance"],
            preferred_trade="Electrician",
            minimum_experience_years=1.0,
            salary_min_inr=16000,
            salary_max_inr=23000,
            contact_email="hr@amausi-industrial.example",
            source="Company Career Portal",
        ),
        JobOpening(
            job_id="unstop-201",
            title="Apprentice Technician",
            company="North India Manufacturing",
            location="Lucknow",
            required_skills=["maintenance", "quality check", "machine setup"],
            preferred_trade="Fitter",
            minimum_experience_years=0.0,
            salary_min_inr=12000,
            salary_max_inr=18000,
            contact_email="jobs@north-india-manufacturing.example",
            source="Unstop",
        ),
        JobOpening(
            job_id="course-301",
            title="Industrial Technician Trainee",
            company="SkillBridge Academy Partner",
            location="Lucknow",
            required_skills=["multimeter use", "motor winding", "maintenance"],
            preferred_trade="Electrician",
            minimum_experience_years=0.5,
            salary_min_inr=14000,
            salary_max_inr=20000,
            contact_email="careers@skillbridge.example",
            source="CourseJoiner",
        ),
        JobOpening(
            job_id="govt-401",
            title="Government Apprenticeship - Electrician",
            company="State Skill Mission",
            location="Lucknow",
            required_skills=["safety compliance", "panel wiring", "three phase wiring"],
            preferred_trade="Electrician",
            minimum_experience_years=0.0,
            salary_min_inr=10000,
            salary_max_inr=15000,
            contact_email="apprenticeship@state-skill.example",
            source="Government Job Portal",
        ),
    ]