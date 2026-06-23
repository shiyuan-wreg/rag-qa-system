"""In-memory job store for DocHub."""

from datetime import datetime, timezone

from models import ConversionJob


class JobStore:
    def __init__(self):
        self._jobs: dict[str, ConversionJob] = {}
        self._counter = 0

    def create(self, source_type: str, source_name: str, output_dir: str) -> ConversionJob:
        self._counter += 1
        job_id = f"job-{self._counter:04d}"
        job = ConversionJob(
            job_id=job_id,
            source_type=source_type,
            source_name=source_name,
            status="pending",
            created_at=datetime.now(timezone.utc).isoformat(),
            output_dir=output_dir,
        )
        self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> ConversionJob | None:
        return self._jobs.get(job_id)

    def update_status(self, job_id: str, status: str, error_message: str = "") -> None:
        job = self._jobs.get(job_id)
        if job:
            job.status = status
            job.error_message = error_message

    def list(self) -> list[ConversionJob]:
        return sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)
