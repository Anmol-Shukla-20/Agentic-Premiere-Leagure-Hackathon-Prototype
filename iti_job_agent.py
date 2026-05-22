"""ITI Lucknow job-matching agent prototype.

This single-file MVP demonstrates how to:
- model ITI graduate profiles
- score and rank live job openings by skill overlap
- draft an outreach message on behalf of a candidate
- track placement outcomes for follow-up

The script is intentionally dependency-free so it can be pushed as a fast hackathon
starter and expanded later into an API or web app.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Tuple
import json
import math
import re


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


class ITIJobAgent:
    """Core matching and outreach logic for ITI graduates."""

    def __init__(self) -> None:
        self.placement_log: List[PlacementOutcome] = []

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    @staticmethod
    def _tokenize(items: List[str]) -> List[str]:
        tokens: List[str] = []
        for item in items:
            normalized = ITIJobAgent._normalize(item)
            if normalized:
                tokens.append(normalized)
        return tokens

    def score_job_match(self, candidate: CandidateProfile, job: JobOpening) -> Tuple[float, Dict[str, float]]:
        candidate_skills = set(self._tokenize(candidate.skills))
        job_skills = set(self._tokenize(job.required_skills))
        skill_overlap = candidate_skills.intersection(job_skills)

        overlap_score = len(skill_overlap) / max(len(job_skills), 1)
        trade_bonus = 1.0 if self._normalize(candidate.trade) and self._normalize(candidate.trade) in self._normalize(job.preferred_trade) else 0.0
        role_bonus = 0.2 if any(self._normalize(role) in self._normalize(job.title) for role in candidate.preferred_roles) else 0.0
        experience_bonus = 0.0
        if candidate.years_experience >= job.minimum_experience_years:
            experience_bonus = min((candidate.years_experience - job.minimum_experience_years) * 0.05, 0.2)

        salary_bonus = 0.0
        if job.salary_max_inr and candidate.expected_salary_inr:
            if candidate.expected_salary_inr <= job.salary_max_inr:
                salary_bonus = 0.1
            elif candidate.expected_salary_inr <= int(job.salary_max_inr * 1.15):
                salary_bonus = 0.05

        final_score = (overlap_score * 0.6) + (trade_bonus * 0.15) + role_bonus + experience_bonus + salary_bonus
        final_score = min(final_score, 1.0)

        diagnostics = {
            "skill_overlap": overlap_score,
            "trade_bonus": trade_bonus,
            "role_bonus": role_bonus,
            "experience_bonus": experience_bonus,
            "salary_bonus": salary_bonus,
            "matched_skills": len(skill_overlap),
            "job_skill_count": len(job_skills),
        }
        return final_score, diagnostics

    def match_jobs(self, candidate: CandidateProfile, jobs: List[JobOpening], top_k: int = 5) -> List[Dict[str, object]]:
        ranked: List[Dict[str, object]] = []
        for job in jobs:
            score, diagnostics = self.score_job_match(candidate, job)
            ranked.append(
                {
                    "job": asdict(job),
                    "score": round(score, 3),
                    "diagnostics": diagnostics,
                    "fit_label": self._label_score(score),
                }
            )
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:top_k]

    @staticmethod
    def _label_score(score: float) -> str:
        if score >= 0.8:
            return "strong"
        if score >= 0.55:
            return "good"
        if score >= 0.3:
            return "possible"
        return "weak"

    def draft_outreach_message(self, candidate: CandidateProfile, job: JobOpening, score: float) -> str:
        greeting_name = job.company or "team"
        return (
            f"Subject: Candidate recommendation for {job.title} from ITI Lucknow\n\n"
            f"Hello {greeting_name},\n\n"
            f"I am reaching out on behalf of {candidate.name}, an ITI Lucknow graduate from the {candidate.trade} trade "
            f"based in {candidate.location}. We found a strong match for your opening '{job.title}' at {job.company}.\n\n"
            f"Match score: {round(score * 100)}%\n"
            f"Relevant skills: {', '.join(candidate.skills[:6])}\n"
            f"Preferred role alignment: {', '.join(candidate.preferred_roles) if candidate.preferred_roles else 'general trade role'}\n\n"
            f"If you are open to a quick screening call, we can share the candidate profile and availability.\n\n"
            f"Regards,\nITI Lucknow Placement Agent"
        )

    def record_outcome(self, candidate_id: str, job_id: str, stage: str, status: str, notes: str = "") -> PlacementOutcome:
        outcome = PlacementOutcome(
            candidate_id=candidate_id,
            job_id=job_id,
            stage=stage,
            status=status,
            updated_at=datetime.utcnow().isoformat(timespec="seconds") + "Z",
            notes=notes,
        )
        self.placement_log.append(outcome)
        return outcome

    def summarize_pipeline(self) -> Dict[str, int]:
        summary = {"total": len(self.placement_log), "applied": 0, "shortlisted": 0, "interview": 0, "hired": 0, "rejected": 0}
        for item in self.placement_log:
            status = item.status.lower()
            if status in summary:
                summary[status] += 1
        return summary


SAMPLE_CANDIDATE = CandidateProfile(
    candidate_id="cand-001",
    name="Aman Kumar",
    trade="Electrician",
    institute="ITI Lucknow",
    location="Amausi, Lucknow",
    skills=["panel wiring", "motor winding", "troubleshooting", "safety compliance", "three phase wiring", "multimeter use"],
    preferred_roles=["maintenance electrician", "industrial technician"],
    expected_salary_inr=18000,
    years_experience=1.5,
)

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


def run_demo() -> None:
    agent = ITIJobAgent()
    matches = agent.match_jobs(SAMPLE_CANDIDATE, SAMPLE_JOBS, top_k=3)

    print("Top job matches for ITI Lucknow candidate:\n")
    for idx, item in enumerate(matches, start=1):
        job = item["job"]
        score = item["score"]
        print(f"{idx}. {job['title']} at {job['company']} - score {score} ({item['fit_label']})")

    best = matches[0]
    best_job = JobOpening(**best["job"])
    outreach = agent.draft_outreach_message(SAMPLE_CANDIDATE, best_job, float(best["score"]))
    print("\nDraft outreach message:\n")
    print(outreach)

    agent.record_outcome(SAMPLE_CANDIDATE.candidate_id, best_job.job_id, stage="applied", status="applied", notes="Auto-submitted to best match")
    agent.record_outcome(SAMPLE_CANDIDATE.candidate_id, best_job.job_id, stage="interview", status="shortlisted", notes="HR requested phone screening")

    print("\nPlacement pipeline summary:\n")
    print(json.dumps(agent.summarize_pipeline(), indent=2))


if __name__ == "__main__":
    run_demo()
