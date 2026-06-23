import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backends/md_converter_app")

from models import ConversionJob
from store import JobStore


def test_create_and_get_job():
    store = JobStore()
    job = store.create("upload", "test.md", "output/j1")
    assert job.job_id.startswith("job-")
    assert job.status == "pending"

    found = store.get(job.job_id)
    assert found is not None
    assert found.source_name == "test.md"


def test_update_status():
    store = JobStore()
    job = store.create("path", "/docs", "output/j2")
    store.update_status(job.job_id, "done")
    assert store.get(job.job_id).status == "done"


def test_list_jobs():
    store = JobStore()
    store.create("upload", "a.md", "output/j1")
    store.create("upload", "b.md", "output/j2")
    assert len(store.list()) == 2
