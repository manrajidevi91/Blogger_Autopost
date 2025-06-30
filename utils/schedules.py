import json
import os
from datetime import datetime
from typing import Any, Dict

from apscheduler.schedulers.base import BaseScheduler

from utils.post_creator import create_post

SCHEDULES_FILE = 'schedules.json'

def load_schedules_data() -> Dict[str, Any]:
    """Return all saved schedules from disk."""
    if not os.path.exists(SCHEDULES_FILE):
        with open(SCHEDULES_FILE, "w") as f:
            json.dump({}, f)
    with open(SCHEDULES_FILE, "r") as f:
        return json.load(f)

def save_schedules_data(data: Dict[str, Any]) -> None:
    """Persist the schedules dictionary to disk."""
    # Ensure directory exists in case SCHEDULES_FILE points to a nested path
    dirname = os.path.dirname(SCHEDULES_FILE)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    with open(SCHEDULES_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_schedule(schedule_id: str) -> Dict[str, Any] | None:
    """Fetch a single schedule entry by its id."""
    schedules = load_schedules_data()
    return schedules.get(schedule_id)


def register_jobs(scheduler: BaseScheduler) -> None:
    """Register all jobs from ``schedules.json`` with the given APScheduler."""
    schedules = load_schedules_data()

    for job_id, job in schedules.items():
        try:
            run_time = datetime.fromisoformat(job["scheduled_time"])
        except (KeyError, ValueError):
            # Skip malformed schedule entries
            continue

        args = [
            job.get("site_name"),
            job.get("content_source"),
            job.get("ai_model"),
            job.get("template"),
            job.get("source_input"),
        ]

        if job.get("repeat"):
            scheduler.add_job(
                create_post,
                "interval",
                days=1,
                start_date=run_time,
                id=job_id,
                args=args,
            )
        else:
            scheduler.add_job(
                create_post,
                "date",
                run_date=run_time,
                id=job_id,
                args=args,
            )
