"""Configuration management."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "qwen")
    LLM_MODEL = os.environ.get("LLM_MODEL", "qwen-turbo")
    DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY")
    RAG_URL = os.environ.get("RAG_URL", "http://localhost:8000")
    FC_URL  = os.environ.get("FC_URL", "http://localhost:8001")
