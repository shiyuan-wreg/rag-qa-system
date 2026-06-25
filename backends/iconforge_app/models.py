"""Pydantic 响应模型。"""
from pydantic import BaseModel


class CleanStats(BaseModel):
    pathsKept: int
    pathsDropped: int
    bbox: list[float]
    bytesIn: int
    bytesOut: int


class CleanResponse(BaseModel):
    svg: str
    stats: CleanStats
    warnings: list[str] = []
