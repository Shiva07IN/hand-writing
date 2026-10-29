"""
MUJ Assignment Agent - Configuration Manager
Loads and validates all settings from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)


# ── Gemini AI Settings ─────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# ── Ink & Style Settings ──────────────────────────────────
INK_COLOR = (
    int(os.getenv("INK_COLOR_R", "15")),
    int(os.getenv("INK_COLOR_G", "25")),
    int(os.getenv("INK_COLOR_B", "105")),
)
FONT_SIZE = int(os.getenv("FONT_SIZE", "38"))
PAGE_STYLE = os.getenv("PAGE_STYLE", "lined")  # blank | lined | ruled

# ── Student Info ──────────────────────────────────────────
STUDENT_NAME = os.getenv("STUDENT_NAME", "Student")
STUDENT_REG_NO = os.getenv("STUDENT_REG_NO", "XXXXXXXXX")
STUDENT_SECTION = os.getenv("STUDENT_SECTION", "")
STUDENT_COURSE = os.getenv("STUDENT_COURSE", "")

# ── Paths ─────────────────────────────────────────────────
FONTS_DIR = BASE_DIR / "fonts"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure directories exist
for d in [FONTS_DIR, INPUT_DIR, OUTPUT_DIR, ASSETS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Page Dimensions (A4 at ~150 DPI) ─────────────────────
PAGE_WIDTH = 1240
PAGE_HEIGHT = 1754
MARGIN_LEFT = 130
MARGIN_TOP = 160
MARGIN_RIGHT = 100
MARGIN_BOTTOM = 120
LINE_SPACING = 16  # Extra spacing between text lines
