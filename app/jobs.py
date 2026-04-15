from __future__ import annotations

import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor


class JobManager:
    def __init__(self, repository, max_workers: int = 4) -> None:
        self.repository = repository
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, fn, payload: dict, created_by: str = "", max_retries: int = 2) -> str:
        job_id = uuid.uuid4().hex
        self.repository.create_job(job_id, payload, created_by=created_by, max_retries=max_retries)
        self.executor.submit(self._run_job, job_id, fn, payload)
        return job_id

    def _run_job(self, job_id: str, fn, payload: dict) -> None:
        job = self.repository.get_job(job_id)
        if job is None:
            return

        self.repository.update_job(job_id, status="running")
        try:
            result = fn(payload)
        except Exception as exc:  # pragma: no cover
            retries = job["retries"] + 1
            error = {"message": str(exc), "traceback": traceback.format_exc(limit=5)}
            if retries <= job["max_retries"]:
                self.repository.update_job(job_id, status="retrying", retries=retries, error=error)
                self.executor.submit(self._run_job, job_id, fn, payload)
                return
            self.repository.update_job(job_id, status="failed", retries=retries, error=error)
            return

        self.repository.update_job(job_id, status="completed", result=result)

    def get(self, job_id: str) -> dict | None:
        return self.repository.get_job(job_id)

    def list_jobs(self, limit: int = 50) -> list[dict]:
        return self.repository.list_jobs(limit=limit)

    def retry(self, job_id: str, fn) -> dict | None:
        job = self.repository.retry_job(job_id)
        if job is None:
            return None
        self.executor.submit(self._run_job, job_id, fn, job["payload"])
        return job
