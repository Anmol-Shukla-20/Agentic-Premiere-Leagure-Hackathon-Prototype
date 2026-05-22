"""Matching engine for the ITI Lucknow placement agent.

This is the core of the demo: it scores jobs against candidate skills, adds
location and salary awareness, and creates a ready-to-send outreach message.
"""

from dataclasses import asdict
from datetime import datetime
from difflib import SequenceMatcher
import re
from typing import Dict, List, Sequence, Tuple

from .config import DEFAULT_LOCATION_KEYWORDS, DEFAULT_OUTCOME_STAGES, SKILL_SYNONYMS
from .models import CandidateProfile, JobOpening, MatchResult, PlacementOutcome


class ITIJobAgent:
    """Core matching, outreach, and placement tracking logic."""

    def __init__(self) -> None:
        self.placement_log: List[PlacementOutcome] = []

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    def _normalize_skill(self, text: str) -> str:
        normalized = self._normalize(text)
        return SKILL_SYNONYMS.get(normalized, normalized)

    def _tokenize_skills(self, items: Sequence[str]) -> List[str]:
        return [self._normalize_skill(item) for item in items if self._normalize(item)]

    def _location_match_score(self, candidate_location: str, job_location: str) -> float:
        candidate_value = self._normalize(candidate_location)
        job_value = self._normalize(job_location)
        if not candidate_value or not job_value:
            return 0.0
        if candidate_value == job_value:
            return 1.0
        if any(keyword in job_value for keyword in DEFAULT_LOCATION_KEYWORDS):
            if any(keyword in candidate_value for keyword in DEFAULT_LOCATION_KEYWORDS):
                return 1.0
            return 0.7
        if candidate_value.split(",")[-1].strip() == job_value.split(",")[-1].strip():
            return 0.5
        return 0.0

    def _salary_fit_score(self, expected_salary: int, job: JobOpening) -> float:
        if expected_salary <= 0 or job.salary_max_inr <= 0:
            return 0.0
        if expected_salary <= job.salary_max_inr:
            return 1.0
        gap_ratio = (expected_salary - job.salary_max_inr) / max(job.salary_max_inr, 1)
        if gap_ratio <= 0.15:
            return 0.5
        return 0.0

    def _trade_alignment(self, candidate_trade: str, job_trade: str, job_title: str) -> float:
        candidate_value = self._normalize_skill(candidate_trade)
        trade_value = self._normalize_skill(job_trade)
        title_value = self._normalize(job_title)
        if candidate_value and trade_value and candidate_value == trade_value:
            return 1.0
        if candidate_value and trade_value and (candidate_value in trade_value or trade_value in candidate_value):
            return 0.8
        if candidate_value and candidate_value in title_value:
            return 0.5
        return 0.0

    def score_job_match(self, candidate: CandidateProfile, job: JobOpening) -> Tuple[float, Dict[str, float]]:
        candidate_skills = set(self._tokenize_skills(candidate.skills))
        job_skills = set(self._tokenize_skills(job.required_skills))
        matched_skills = candidate_skills.intersection(job_skills)

        overlap_score = len(matched_skills) / max(len(job_skills), 1)
        trade_score = self._trade_alignment(candidate.trade, job.preferred_trade, job.title)
        role_score = 0.0
        if candidate.preferred_roles:
            job_title = self._normalize(job.title)
            role_score = max(
                (SequenceMatcher(None, self._normalize(role), job_title).ratio() for role in candidate.preferred_roles),
                default=0.0,
            )
        experience_score = 1.0 if candidate.years_experience >= job.minimum_experience_years else 0.0
        location_score = self._location_match_score(candidate.location, job.location)
        salary_score = self._salary_fit_score(candidate.expected_salary_inr, job)

        score = (
            overlap_score * 0.55
            + trade_score * 0.10
            + role_score * 0.10
            + experience_score * 0.10
            + location_score * 0.10
            + salary_score * 0.05
        )

        diagnostics = {
            "skill_overlap": round(overlap_score, 3),
            "trade_alignment": round(trade_score, 3),
            "role_alignment": round(role_score, 3),
            "experience_fit": round(experience_score, 3),
            "location_fit": round(location_score, 3),
            "salary_fit": round(salary_score, 3),
            "matched_skill_count": float(len(matched_skills)),
            "job_skill_count": float(len(job_skills)),
        }
        return round(min(score, 1.0), 3), diagnostics

    @staticmethod
    def _label_score(score: float) -> str:
        if score >= 0.8:
            return "strong"
        if score >= 0.6:
            return "good"
        if score >= 0.35:
            return "possible"
        return "weak"

    def draft_outreach_message(self, candidate: CandidateProfile, job: JobOpening, score: float) -> str:
        recipient = job.company or "Hiring Team"
        shared_skills = ", ".join(candidate.skills[:6])
        return (
            f"Subject: ITI Lucknow candidate recommendation for {job.title}\n\n"
            f"Hello {recipient},\n\n"
            f"We are sharing {candidate.name}, an ITI Lucknow graduate from the {candidate.trade} trade, "
            f"based in {candidate.location}. The candidate is a strong fit for '{job.title}' at {job.company}.\n\n"
            f"Match score: {round(score * 100)}%\n"
            f"Relevant skills: {shared_skills}\n"
            f"Target role: {', '.join(candidate.preferred_roles) if candidate.preferred_roles else candidate.trade}\n"
            f"Experience: {candidate.years_experience} years\n"
            f"Expected salary: INR {candidate.expected_salary_inr}\n\n"
            f"If you are open to a short screening call, we can share the profile and availability immediately.\n\n"
            f"Regards,\nITI Lucknow Placement Agent"
        )

    def match_jobs(self, candidate: CandidateProfile, jobs: Sequence[JobOpening], top_k: int = 5) -> List[MatchResult]:
        ranked: List[MatchResult] = []
        for job in jobs:
            score, diagnostics = self.score_job_match(candidate, job)
            ranked.append(
                MatchResult(
                    candidate_id=candidate.candidate_id,
                    job_id=job.job_id,
                    score=score,
                    fit_label=self._label_score(score),
                    diagnostics=diagnostics,
                    outreach_message=self.draft_outreach_message(candidate, job, score),
                    candidate=asdict(candidate),
                    job=asdict(job),
                )
            )
        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:top_k]

    def batch_match(self, candidates: Sequence[CandidateProfile], jobs: Sequence[JobOpening], top_k: int = 3) -> Dict[str, List[MatchResult]]:
        return {candidate.candidate_id: self.match_jobs(candidate, jobs, top_k=top_k) for candidate in candidates}

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
        summary = {"total": len(self.placement_log), **{stage: 0 for stage in DEFAULT_OUTCOME_STAGES}}
        for item in self.placement_log:
            status = item.status.lower()
            if status in summary:
                summary[status] += 1
        return summary