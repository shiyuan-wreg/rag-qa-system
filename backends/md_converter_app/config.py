"""Configuration for DocHub."""

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

APP_DIR = Path(__file__).resolve().parent


class Config:
    DOCHUB_PASSWORD = os.environ.get("DOCHUB_PASSWORD", "test-password")
    DOCHUB_ALLOW_PATH_CONVERT = os.environ.get("DOCHUB_ALLOW_PATH_CONVERT", "false").lower() == "true"
    UPLOAD_DIR = APP_DIR / "uploads"
    OUTPUT_DIR = APP_DIR / "output"
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024
    SECRET_KEY = os.environ.get("DOCHUB_SECRET_KEY", secrets.token_hex(32))
