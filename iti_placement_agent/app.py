"""Application entry point for the ITI Lucknow placement agent.

This file ties everything together: it loads data, filters jobs, and chooses
whether the user wants the dashboard, the demo run, or JSON export mode.
"""

import argparse
import json
import math
from dataclasses import asdict
from typing import Dict, List, Optional, Sequence, Tuple

from .config import DEFAULT_TOP_K
from .dashboard import build_dashboard, persist_outputs
from .data import SAMPLE_CANDIDATES, SAMPLE_JOBS
from .engine import ITIJobAgent
from .models import CandidateProfile, JobOpening, MatchResult
from .storage import build_output_payload, load_candidates, load_jobs, load_match_dataset_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ITI Lucknow skill-to-job matching agent")
    parser.add_argument("--candidates", help="Path to candidates JSON file", default=None)
    parser.add_argument("--jobs", help="Path to live jobs JSON file", default=None)
    parser.add_argument("--dataset-csv", help="Path to the labeled skill/job benchmark CSV", default=None)
    parser.add_argument("--matches-out", help="Write ranked matches to JSON", default=None)
    parser.add_argument("--placements-out", help="Write placement summary to JSON", default=None)
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help="Number of matches to keep per candidate")
    parser.add_argument("--location", default="Lucknow", help="Preferred job location keyword")
    parser.add_argument("--salary-max", type=int, default=0, help="Filter jobs above this salary ceiling")
    parser.add_argument("--mode", choices=["dashboard", "demo", "cli", "evaluate"], default="dashboard", help="Run the dashboard, demo, CLI export, or CSV evaluation")
    return parser.parse_args()


def filter_jobs(jobs: Sequence[JobOpening], location_keyword: str = "", salary_max: int = 0) -> List[JobOpening]:
    """Apply the simplest demo filter: keep jobs that fit the Lucknow context."""
    filtered: List[JobOpening] = []
    location_value = location_keyword.strip().lower()
    for job in jobs:
        job_location = job.location.lower()
        if location_value and location_value not in job_location:
            continue
        if salary_max and job.salary_max_inr and job.salary_max_inr > salary_max:
            continue
        filtered.append(job)
    return filtered


def _row_skill_vector(row: Dict[str, object], prefix: str) -> List[float]:
    return [float(row.get(f"{prefix}{index}", 0) or 0) for index in range(1, 6)]


def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    numerator = sum(l_value * r_value for l_value, r_value in zip(left, right))
    left_magnitude = math.sqrt(sum(value * value for value in left))
    right_magnitude = math.sqrt(sum(value * value for value in right))
    if not left_magnitude or not right_magnitude:
        return 0.0
    return numerator / (left_magnitude * right_magnitude)


def score_dataset_row(row: Dict[str, object]) -> float:
    """Convert one labeled CSV row into a simple benchmark score.

    The CSV is already supervised, so we use it to check whether the matching
    heuristics behave sensibly. This is a practical way to validate the project
    before connecting live openings.
    """
    candidate_skills = _row_skill_vector(row, "Skill_")
    job_skills = _row_skill_vector(row, "Required_Skill_")
    skill_similarity = _cosine_similarity(candidate_skills, job_skills)

    internship = float(row.get("Internship_Experience", 0) or 0)
    min_experience = float(row.get("Min_Experience_Months", 0) or 0)
    experience_fit = min(internship / max(min_experience, 1.0), 1.0)

    academic = float(row.get("Academic_Performance", 0) or 0) / 100.0
    certifications = min(float(row.get("Certifications_Count", 0) or 0) / 5.0, 1.0)

    vocational_program = str(row.get("Vocational_Program", "")).strip().lower()
    job_title = str(row.get("Job_Title", "")).strip().lower()
    title_bonus_pairs = {
        "electrician": ["electrical technician"],
        "welder": ["welding operator"],
        "plumber": ["plumbing assistant"],
        "carpenter": ["woodwork assistant"],
        "mechanic": ["automobile mechanic"],
        "it technician": ["it support technician"],
    }
    title_bonus = 0.15 if any(keyword in job_title for keyword in title_bonus_pairs.get(vocational_program, [])) else 0.0

    score = (
        skill_similarity * 0.60
        + experience_fit * 0.15
        + academic * 0.10
        + certifications * 0.10
        + title_bonus
    )
    return min(score, 1.0)


def evaluate_dataset(rows: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """Produce a simple benchmark report for the labeled CSV dataset."""
    if not rows:
        return {"rows": 0, "message": "No dataset rows found."}

    threshold = 0.55
    true_positive = true_negative = false_positive = false_negative = 0
    sample_rows: List[Dict[str, object]] = []

    for row in rows:
        predicted_score = score_dataset_row(row)
        predicted_label = 1 if predicted_score >= threshold else 0
        actual_label = int(row.get("Job_Match", 0) or 0)

        if predicted_label == 1 and actual_label == 1:
            true_positive += 1
        elif predicted_label == 0 and actual_label == 0:
            true_negative += 1
        elif predicted_label == 1 and actual_label == 0:
            false_positive += 1
        else:
            false_negative += 1

        if len(sample_rows) < 5:
            sample_rows.append(
                {
                    "student_id": row.get("Student_ID"),
                    "job_id": row.get("Job_ID"),
                    "job_title": row.get("Job_Title"),
                    "actual": actual_label,
                    "predicted": predicted_label,
                    "score": round(predicted_score, 3),
                }
            )

    total = true_positive + true_negative + false_positive + false_negative
    accuracy = (true_positive + true_negative) / total if total else 0.0
    precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) else 0.0
    recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) else 0.0

    return {
        "rows": total,
        "threshold": threshold,
        "accuracy": round(accuracy, 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "confusion_matrix": {
            "true_positive": true_positive,
            "true_negative": true_negative,
            "false_positive": false_positive,
            "false_negative": false_negative,
        },
        "sample_predictions": sample_rows,
    }


def run_demo(agent: ITIJobAgent, candidates: Sequence[CandidateProfile], jobs: Sequence[JobOpening], top_k: int) -> None:
    results = agent.batch_match(candidates, jobs, top_k=top_k)
    first_candidate_id = next(iter(results)) if results else ""

    print("Top job matches for ITI Lucknow graduates:\n")
    for candidate in candidates:
        print(f"Candidate: {candidate.name} ({candidate.trade})")
        for idx, item in enumerate(results.get(candidate.candidate_id, []), start=1):
            job = item.job
            print(f"  {idx}. {job['title']} at {job['company']} - score {item.score} ({item.fit_label})")
        print()

    if first_candidate_id and results.get(first_candidate_id):
        best = results[first_candidate_id][0]
        best_job = JobOpening(**best.job)
        candidate = next(item for item in candidates if item.candidate_id == first_candidate_id)
        print("Draft outreach message:\n")
        print(agent.draft_outreach_message(candidate, best_job, best.score))
        print()
        agent.record_outcome(candidate.candidate_id, best_job.job_id, stage="applied", status="applied", notes="Auto-shared to best match")
        agent.record_outcome(candidate.candidate_id, best_job.job_id, stage="interview", status="shortlisted", notes="Recruiter requested screening")

    print("Placement pipeline summary:\n")
    print(json.dumps(agent.summarize_pipeline(), indent=2))

    persist_outputs(agent, results, "matches.json", "placement-summary.json")


def run_dataset_evaluation(dataset_rows: Sequence[Dict[str, object]]) -> None:
    report = evaluate_dataset(dataset_rows)
    print("CSV benchmark report:\n")
    print(json.dumps(report, indent=2))


def main() -> None:
    args = parse_args()
    agent = ITIJobAgent()

    candidates = load_candidates(args.candidates, SAMPLE_CANDIDATES)
    jobs = load_jobs(args.jobs, SAMPLE_JOBS)
    jobs = filter_jobs(jobs, location_keyword=args.location, salary_max=args.salary_max)
    dataset_rows = load_match_dataset_csv(args.dataset_csv)

    if args.mode == "evaluate":
        run_dataset_evaluation(dataset_rows)
        return

    if args.mode == "dashboard":
        build_dashboard(
            agent,
            candidates,
            jobs,
            top_k=args.top_k,
            matches_path=args.matches_out or "matches.json",
            placements_path=args.placements_out or "placement-summary.json",
        )
        return

    if args.mode == "demo":
        run_demo(agent, candidates, jobs, top_k=args.top_k)
        return

    results = agent.batch_match(candidates, jobs, top_k=args.top_k)
    output_payload = build_output_payload(results)
    persist_outputs(agent, results, args.matches_out, args.placements_out)
    print(json.dumps(output_payload, indent=2))


if __name__ == "__main__":
    main()