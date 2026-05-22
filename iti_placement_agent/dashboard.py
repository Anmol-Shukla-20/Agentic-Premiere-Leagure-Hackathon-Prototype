"""Tkinter dashboard for the placement agent demo.

The dashboard is intentionally simple and video-friendly: left side for
selection, right side for ranked matches, outreach text, and placement updates.
"""

from dataclasses import asdict
from typing import Dict, List, Optional, Sequence

from .engine import ITIJobAgent
from .models import CandidateProfile, JobOpening, MatchResult
from .storage import build_output_payload, save_json


def persist_outputs(agent: ITIJobAgent, results: Dict[str, List[MatchResult]], matches_path: Optional[str], placements_path: Optional[str]) -> None:
    """Write current match and placement state to JSON files."""
    save_json(matches_path, build_output_payload(results))
    save_json(placements_path, {"summary": agent.summarize_pipeline(), "outcomes": [asdict(item) for item in agent.placement_log]})


def build_dashboard(agent: ITIJobAgent, candidates: Sequence[CandidateProfile], jobs: Sequence[JobOpening], top_k: int, matches_path: Optional[str], placements_path: Optional[str]) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox, scrolledtext, ttk
    except Exception as exc:  # pragma: no cover - fallback for minimal environments
        print(f"Dashboard unavailable: {exc}")
        return

    root = tk.Tk()
    root.title("ITI Lucknow Student's Placement Dashboard")
    root.geometry("1280x820")
    root.minsize(1180, 760)
    root.configure(bg="#111827")

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure("Dashboard.TFrame", background="#111827")
    style.configure("Card.TFrame", background="#1f2937", relief="flat")
    style.configure("Title.TLabel", background="#111827", foreground="#f9fafb", font=("Segoe UI", 22, "bold"))
    style.configure("Subtitle.TLabel", background="#111827", foreground="#cbd5e1", font=("Segoe UI", 10))
    style.configure("CardTitle.TLabel", background="#1f2937", foreground="#93c5fd", font=("Segoe UI", 10, "bold"))
    style.configure("CardValue.TLabel", background="#1f2937", foreground="#f9fafb", font=("Segoe UI", 20, "bold"))
    style.configure("Section.TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 12, "bold"))
    style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    results: Dict[str, List[MatchResult]] = {candidate.candidate_id: [] for candidate in candidates}
    candidate_by_index = {index: candidate for index, candidate in enumerate(candidates)}
    job_by_index = {index: job for index, job in enumerate(jobs)}

    outer = ttk.Frame(root, style="Dashboard.TFrame", padding=18)
    outer.pack(fill="both", expand=True)

    header = ttk.Frame(outer, style="Dashboard.TFrame")
    header.pack(fill="x")
    ttk.Label(header, text="ITI Lucknow Placement Dashboard", style="Title.TLabel").pack(anchor="w")
    ttk.Label(
        header,
        text="Skill-to-job matching for ITI Lucknow graduates, focused on Amausi and nearby industrial openings.",
        style="Subtitle.TLabel",
    ).pack(anchor="w", pady=(4, 0))

    cards = ttk.Frame(outer, style="Dashboard.TFrame")
    cards.pack(fill="x", pady=(18, 12))
    cards.columnconfigure((0, 1, 2, 3), weight=1)

    card_widgets = {}
    for index, (title, value) in enumerate([
        ("Candidates", str(len(candidates))),
        ("Live Jobs", str(len(jobs))),
        ("Top Matches", "0"),
        ("Placements", "0"),
    ]):
        frame = ttk.Frame(cards, style="Card.TFrame", padding=16)
        frame.grid(row=0, column=index, padx=8, sticky="nsew")
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(anchor="w")
        value_label = ttk.Label(frame, text=value, style="CardValue.TLabel")
        value_label.pack(anchor="w", pady=(8, 0))
        card_widgets[title] = value_label

    content = ttk.Frame(outer, style="Dashboard.TFrame")
    content.pack(fill="both", expand=True)
    content.columnconfigure(0, weight=1)
    content.columnconfigure(1, weight=2)
    content.rowconfigure(0, weight=1)

    left = ttk.Frame(content, style="Card.TFrame", padding=14)
    left.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
    right = ttk.Frame(content, style="Card.TFrame", padding=14)
    right.grid(row=0, column=1, sticky="nsew")

    ttk.Label(left, text="Candidates", style="Section.TLabel").pack(anchor="w")
    candidate_list = tk.Listbox(left, height=10, exportselection=False, bg="#111827", fg="#f9fafb", highlightthickness=0, selectbackground="#2563eb")
    candidate_list.pack(fill="x", pady=(8, 14))
    for candidate in candidates:
        candidate_list.insert("end", f"{candidate.name} · {candidate.trade}")

    ttk.Label(left, text="Jobs", style="Section.TLabel").pack(anchor="w")
    job_list = tk.Listbox(left, height=10, exportselection=False, bg="#111827", fg="#f9fafb", highlightthickness=0, selectbackground="#2563eb")
    job_list.pack(fill="x", pady=(8, 14))
    for job in jobs:
        job_list.insert("end", f"{job.title} · {job.company}")

    actions = ttk.Frame(left, style="Card.TFrame")
    actions.pack(fill="x", pady=(8, 0))

    ttk.Label(right, text="Top Matches", style="Section.TLabel").pack(anchor="w")
    columns = ("rank", "job", "company", "location", "score", "label")
    tree = ttk.Treeview(right, columns=columns, show="headings", height=8)
    for column, heading, width in [
        ("rank", "#", 40),
        ("job", "Job Title", 190),
        ("company", "Company", 180),
        ("location", "Location", 160),
        ("score", "Score", 80),
        ("label", "Fit", 90),
    ]:
        tree.heading(column, text=heading)
        tree.column(column, width=width, anchor="w")
    tree.pack(fill="x", pady=(8, 16))

    ttk.Label(right, text="Placement Outcome", style="Section.TLabel").pack(anchor="w")
    placement_text = tk.StringVar(value="Select a candidate and job to record an outcome.")
    placement_label = ttk.Label(right, textvariable=placement_text, wraplength=640, justify="left")
    placement_label.pack(anchor="w", pady=(8, 12))

    ttk.Label(right, text="Outreach Draft", style="Section.TLabel").pack(anchor="w")
    outreach_box = scrolledtext.ScrolledText(right, height=14, wrap=tk.WORD, bg="#0f172a", fg="#e2e8f0", insertbackground="#e2e8f0")
    outreach_box.pack(fill="both", expand=True, pady=(8, 0))

    selected_candidate_index = tk.IntVar(value=0)
    selected_job_index = tk.IntVar(value=0)

    def refresh_cards() -> None:
        # These counters make the demo feel alive while you click through it.
        card_widgets["Top Matches"].configure(text=str(sum(len(items) for items in results.values())))
        card_widgets["Placements"].configure(text=str(len(agent.placement_log)))

    def refresh_matches() -> None:
        candidate_index = selected_candidate_index.get()
        if candidate_index not in candidate_by_index:
            return
        candidate = candidate_by_index[candidate_index]
        ranked = agent.match_jobs(candidate, jobs, top_k=top_k)
        results[candidate.candidate_id] = ranked

        for row in tree.get_children():
            tree.delete(row)
        for index, item in enumerate(ranked, start=1):
            job = item.job
            tree.insert("", "end", values=(index, job["title"], job["company"], job["location"], item.score, item.fit_label))

        if ranked:
            best = ranked[0]
            best_job = JobOpening(**best.job)
            outreach_box.delete("1.0", tk.END)
            outreach_box.insert(tk.END, best.outreach_message)
            selected_job_index.set(next((index for index, job in job_by_index.items() if job.job_id == best_job.job_id), 0))
            placement_text.set(
                f"Best current match: {candidate.name} -> {best_job.title} at {best_job.company} (score {best.score}, {best.fit_label})."
            )
        refresh_cards()

    def record_selected_outcome(stage: str, status: str) -> None:
        candidate_index = selected_candidate_index.get()
        job_index = selected_job_index.get()
        if candidate_index not in candidate_by_index or job_index not in job_by_index:
            messagebox.showwarning("Selection needed", "Please select both a candidate and a job first.")
            return
        candidate = candidate_by_index[candidate_index]
        job = job_by_index[job_index]
        agent.record_outcome(candidate.candidate_id, job.job_id, stage=stage, status=status, notes="Recorded from dashboard")
        placement_text.set(f"Recorded {status} for {candidate.name} on {job.title}.")
        refresh_cards()
        persist_outputs(agent, results, matches_path, placements_path)

    def on_candidate_select(event: object) -> None:
        selection = candidate_list.curselection()
        if not selection:
            return
        selected_candidate_index.set(selection[0])
        refresh_matches()

    def on_job_select(event: object) -> None:
        selection = job_list.curselection()
        if not selection:
            return
        selected_job_index.set(selection[0])
        candidate_index = selected_candidate_index.get()
        if candidate_index in candidate_by_index and selection[0] in job_by_index:
            candidate = candidate_by_index[candidate_index]
            job = job_by_index[selection[0]]
            score, _ = agent.score_job_match(candidate, job)
            outreach_box.delete("1.0", tk.END)
            outreach_box.insert(tk.END, agent.draft_outreach_message(candidate, job, score))
            placement_text.set(f"Focused on {candidate.name} and {job.title} at {job.company}.")

    candidate_list.bind("<<ListboxSelect>>", on_candidate_select)
    job_list.bind("<<ListboxSelect>>", on_job_select)

    ttk.Button(actions, text="Refresh Matches", style="Accent.TButton", command=refresh_matches).pack(fill="x", pady=(0, 8))
    ttk.Button(actions, text="Mark Applied", style="Accent.TButton", command=lambda: record_selected_outcome("applied", "applied")).pack(fill="x", pady=(0, 8))
    ttk.Button(actions, text="Mark Shortlisted", style="Accent.TButton", command=lambda: record_selected_outcome("interview", "shortlisted")).pack(fill="x", pady=(0, 8))
    ttk.Button(actions, text="Mark Hired", style="Accent.TButton", command=lambda: record_selected_outcome("hired", "hired")).pack(fill="x")

    def export_now() -> None:
        persist_outputs(agent, results, matches_path, placements_path)
        messagebox.showinfo("Export complete", "Dashboard data has been exported to the configured JSON files.")

    bottom_actions = ttk.Frame(outer, style="Dashboard.TFrame")
    bottom_actions.pack(fill="x", pady=(12, 0))
    ttk.Button(bottom_actions, text="Export JSON", command=export_now).pack(side="left")
    ttk.Button(bottom_actions, text="Close", command=root.destroy).pack(side="right")

    candidate_list.selection_set(0)
    job_list.selection_set(0)
    refresh_matches()
    root.mainloop()