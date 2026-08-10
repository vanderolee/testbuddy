"""
TestBuddy Configuration
"""
import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent
RUNS_DIR = PROJECT_ROOT / "runs"
KB_DIR = PROJECT_ROOT / "knowledge_bank" / "data"
KB_CHROMA_DIR = PROJECT_ROOT / "knowledge_bank" / "chroma_db"

# Hotkeys
TRIGGER_HOTKEY = "n"  # Capture screenshot
QUIT_HOTKEY = "q"        # Exit application

# Capture Settings
CAPTURE_DELAY_MS = 5000                 # Wait after hotkey before capture
TARGET_BROWSER = "Safari"              # "Safari", "Google Chrome", "Firefox", "Microsoft Edge"

# LLM Settings
MODEL = "claude-sonnet-4-6-20250805"   # Claude Sonnet 4.6
MAX_TOKENS = 4096                      # Max response tokens
TEMPERATURE = 0.3                      # Lower = more deterministic

# Token Pricing (USD per million tokens) - Claude Sonnet 4.6
INPUT_TOKEN_PRICE = 3.0
OUTPUT_TOKEN_PRICE = 15.0

# Knowledge Bank Settings (for future implementation)
KB_ENABLED = False                     # Knowledge Bank not yet implemented
KB_TOP_K = 3                           # Number of relevant chunks to retrieve
KB_CHUNK_SIZE = 1000                   # Tokens per chunk for document conversion

# Output Settings
OUTPUT_CLEAR_SCREEN = True             # Clear terminal before each answer
OUTPUT_WIDTH = 80                      # Terminal width for formatting
