import uuid
from dataclasses import dataclass, field
from enum import Enum
from threading import Event, Lock
from typing import Any, Dict, Optional


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    id: str
    status: JobStatus = JobStatus.QUEUED
    progress: int = 0
    message: str = "Waiting to start"
    method_used: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    work_dir: Optional[str] = None
    input_path: Optional[str] = None
    synthetic_path: Optional[str] = None
    preview: Optional[Dict[str, Any]] = None
    cancel_event: Event = field(default_factory=Event)


class JobStore:
    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._lock = Lock()

    def create(
        self,
        work_dir: str,
        input_path: str,
        preview: Dict[str, Any],
        job_id: Optional[str] = None,
    ) -> Job:
        job_id = job_id or str(uuid.uuid4())
        job = Job(
            id=job_id,
            work_dir=work_dir,
            input_path=input_path,
            preview=preview,
        )
        with self._lock:
            self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def update(
        self,
        job_id: str,
        *,
        status: Optional[JobStatus] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        method_used: Optional[str] = None,
        analysis: Optional[Dict[str, Any]] = None,
        report: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        synthetic_path: Optional[str] = None,
    ) -> Optional[Job]:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            if status is not None:
                job.status = status
            if progress is not None:
                job.progress = progress
            if message is not None:
                job.message = message
            if method_used is not None:
                job.method_used = method_used
            if analysis is not None:
                job.analysis = analysis
            if report is not None:
                job.report = report
            if error is not None:
                job.error = error
            if synthetic_path is not None:
                job.synthetic_path = synthetic_path
            return job


    def cancel(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return False
            job.cancel_event.set()
            return True


job_store = JobStore()
