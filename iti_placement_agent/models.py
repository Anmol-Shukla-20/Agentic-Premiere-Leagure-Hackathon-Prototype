"""Data structures used by the placement agent.

These dataclasses keep the data shape explicit, which helps the dashboard,
matching engine, and JSON input/output stay aligned.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CandidateProfile:
    candidate_id: str
    name: str
    trade: str
    institute: str
    location: str
    skills: List[str]
    preferred_roles: List[str] = field(default_factory=list)
    expected_salary_inr: int = 0
    years_experience: float = 0.0


@dataclass
class JobOpening:
    job_id: str
    title: str
    company: str
    location: str
    required_skills: List[str]
    preferred_trade: str = ""
    minimum_experience_years: float = 0.0
    salary_min_inr: int = 0
    salary_max_inr: int = 0
    contact_email: str = ""
    source: str = "live-board"


@dataclass
class PlacementOutcome:
    candidate_id: str
    job_id: str
    stage: str
    status: str
    updated_at: str
    notes: str = ""


@dataclass
class MatchResult:
    candidate_id: str
    job_id: str
    score: float
    fit_label: str
    diagnostics: Dict[str, float]
    outreach_message: str
    candidate: Dict[str, object]
    job: Dict[str, object]