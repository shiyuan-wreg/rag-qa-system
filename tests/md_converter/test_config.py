from backends.md_converter_app.config import Config
from backends.md_converter_app.models import ConversionJob


def test_config_has_required_fields():
    assert hasattr(Config, "DOCHUB_PASSWORD")
    assert hasattr(Config, "DOCHUB_ALLOW_PATH_CONVERT")
    assert hasattr(Config, "UPLOAD_DIR")
    assert hasattr(Config, "OUTPUT_DIR")


def test_job_model_has_required_fields():
    job = ConversionJob(
        job_id="j1",
        source_type="upload",
        source_name="test.md",
        status="pending",
        created_at="2026-06-23T00:00:00",
        output_dir="output/j1",
    )
    assert job.job_id == "j1"
    assert job.source_type == "upload"
    assert job.status == "pending"
