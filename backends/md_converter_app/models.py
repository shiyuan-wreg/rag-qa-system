"""Data models for DocHub."""

from dataclasses import dataclass


@dataclass
class ConversionJob:
    job_id: str
    source_type: str  # "upload" or "path"
    source_name: str
    status: str  # pending / running / done / error
    created_at: str
    output_dir: str
    error_message: str = ""
