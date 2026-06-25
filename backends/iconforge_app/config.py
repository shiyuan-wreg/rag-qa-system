"""IconForge configuration constants."""
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent


class Config:
    DEFAULT_COLOR = "#171817"        # = rgb(23,24,23)
    DEFAULT_THRESHOLD = 120          # dewhite: 三通道均 > 此值视为白/背景
    DEFAULT_PADDING = 0.06           # 紧贴 viewBox 外扩比例
    RASTER_THRESHOLD = 128           # 位图二值化:像素 < 此值算墨(前景)
    MAX_UPLOAD_BYTES = 5 * 1024 * 1024
