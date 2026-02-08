"""
Centralized configuration loader.
Loads settings from .env file and exposes them as module-level constants.
"""

import os
import sys

from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

# --- OpenAI Configuration ---
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- MCP Server Configuration ---
MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "localhost")
MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8000"))
MCP_SERVER_URL: str = f"http://{MCP_SERVER_HOST}:{MCP_SERVER_PORT}"

# --- Retrieval Configuration ---
TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "3"))

# --- Logging Configuration ---
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

# --- Knowledge Base Path ---
KNOWLEDGE_BASE_DIR: str = os.getenv(
    "KNOWLEDGE_BASE_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base"),
)


def validate_config() -> None:
    """Validate that required configuration values are set."""
    if not OPENAI_API_KEY:
        print(
            "ERROR: OPENAI_API_KEY is not set. "
            "Please create a .env file with your API key. "
            "See .env.example for reference."
        )
        sys.exit(1)
