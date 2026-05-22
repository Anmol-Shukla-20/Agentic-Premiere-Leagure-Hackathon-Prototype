"""Input and output helpers for demo and benchmark data.

The agent can run with built-in samples, but these helpers make it easy to
swap in live data from a form, spreadsheet export, or scraped job feed later.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

from .models import CandidateProfile, JobOpening, MatchResult


def load_json_records(path: Optional[str], record_type: str) -> List[Dict[str, object]]:
    if not path:
        return []
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"{record_type} file not found: {path}")
    with file_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict):
        payload = payload.get("items", [])
    if not isinstance(payload, list):
        raise ValueError(f"{record_type} file must contain a list or a dict with an items list")
    return payload


def load_candidates(path: Optional[str], sample_candidates: List[CandidateProfile]) -> List[CandidateProfile]:
    if not path:
        return sample_candidates
    return [CandidateProfile(**item) for item in load_json_records(path, "candidates")]


def load_jobs(path: Optional[str], sample_jobs: List[JobOpening]) -> List[JobOpening]:
    if not path:
        return sample_jobs
    return [JobOpening(**item) for item in load_json_records(path, "jobs")]


def save_json(path: Optional[str], payload: object) -> None:
    if not path:
        return
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)


def build_output_payload(results: Dict[str, List[MatchResult]]) -> Dict[str, object]:
    from dataclasses import asdict
    from datetime import datetime

    return {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "results": {
            candidate_id: [asdict(item) for item in matches]
            for candidate_id, matches in results.items()
        },
    }


def load_match_dataset_csv(path: Optional[str]) -> List[Dict[str, object]]:
    """Load the labeled skill/job benchmark CSV used to validate matching quality.

    Each row already contains a candidate side, a job side, and the ground-truth
    `Job_Match` label. That makes it ideal for evaluating how well the rules in
    the engine behave before you connect real live openings.
    """
    if not path:
        return []

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"dataset file not found: {path}")

    def to_int(value: str) -> int:
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return 0

    def to_float(value: str) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    rows: List[Dict[str, object]] = []
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw_row in reader:
            parsed_row = dict(raw_row)
            parsed_row["Age"] = to_int(raw_row.get("Age", "0"))
            parsed_row["Academic_Performance"] = to_float(raw_row.get("Academic_Performance", "0"))
            parsed_row["Certifications_Count"] = to_int(raw_row.get("Certifications_Count", "0"))
            parsed_row["Internship_Experience"] = to_float(raw_row.get("Internship_Experience", "0"))
            parsed_row["Min_Experience_Months"] = to_float(raw_row.get("Min_Experience_Months", "0"))
            parsed_row["Job_Match"] = to_int(raw_row.get("Job_Match", "0"))
            for index in range(1, 6):
                parsed_row[f"Skill_{index}"] = to_int(raw_row.get(f"Skill_{index}", "0"))
                parsed_row[f"Required_Skill_{index}"] = to_int(raw_row.get(f"Required_Skill_{index}", "0"))
            rows.append(parsed_row)
    return rows