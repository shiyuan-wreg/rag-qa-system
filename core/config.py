"""Configuration management."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "qwen")
    LLM_MODEL = os.environ.get("LLM_MODEL", "qwen-turbo")
    # 通用 LLM 接入(OpenAI 兼容,如 DeepSeek)。base_url 为空时各 SDK 用各自默认值。
    LLM_BASE_URL = os.environ.get("LLM_BASE_URL")
    # 聊天用 key。优先 LLM_API_KEY,回退旧的 DASHSCOPE_API_KEY(向后兼容)。
    LLM_API_KEY = os.environ.get("LLM_API_KEY") or os.environ.get("DASHSCOPE_API_KEY", "")
    DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY")
    # RAG 向量检索用的 Jina embedding key
    JINA_API_KEY = os.environ.get("JINA_API_KEY", "")
    RAG_URL = os.environ.get("RAG_URL", "http://rag:8001")
    FC_URL = os.environ.get("FC_URL", "http://fc:8002")
