"""Configuration management."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "qwen")
    LLM_MODEL = os.environ.get("LLM_MODEL", "qwen-turbo")
    RAG_URL = os.environ.get("RAG_URL", "http://localhost:8000")
