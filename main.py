"""
CLI entry point for the Multi-Agent Document Analysis System.
Runs an interactive loop where users can ask questions that are processed
through the Manager → MCP Tool Server → Specialist agent pipeline.
"""

import argparse
import logging
import sys

from config import validate_config, MCP_SERVER_URL
from logger import get_logger

logger = get_logger("CLI")

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║       Multi-Agent Document Analysis System                  ║
║       ─────────────────────────────────────                 ║
║       Manager Agent  →  MCP Tool Server  →  Specialist      ║
╚══════════════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
Commands:
  Type a question and press Enter to get an answer.
  Type 'quit' or 'exit' to stop.
  Type 'help' to see this message.
"""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Document Analysis System — CLI"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging output.",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point: validate config, connect to MCP server, run Q&A loop."""
    args = parse_args()

    # Override log level if --verbose flag is set
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        for handler in logging.getLogger().handlers:
            handler.setLevel(logging.DEBUG)

    # Validate configuration before doing anything else
    validate_config()

    print(BANNER)
    logger.info("Starting Multi-Agent Document Analysis System")
    logger.info("MCP Server URL: %s", MCP_SERVER_URL)

    # Import here to avoid triggering OpenAI client init before config validation
    from agents.manager import ManagerAgent

    manager = ManagerAgent()

    # Step 1: Discover tools from MCP server (verifies connectivity)
    print("Connecting to MCP Tool Server...")
    try:
        tools = manager.discover_tools()
        print(f"Connected! Discovered {len(tools)} tool(s): "
              f"{', '.join(t['name'] for t in tools)}")
    except ConnectionError as e:
        print(f"\nERROR: {e}")
        print("Please start the MCP server in a separate terminal:")
        print("  uvicorn mcp_server.server:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    print(HELP_TEXT)

    # Step 2: Interactive question loop
    try:
        while True:
            try:
                question = input("> Ask a question (or 'quit' to exit): ").strip()
            except EOFError:
                break

            if not question:
                continue
            if question.lower() in ("quit", "exit", "q"):
                break
            if question.lower() == "help":
                print(HELP_TEXT)
                continue

            print("\nProcessing...\n")

            try:
                answer = manager.run(question)

                print("─" * 60)
                print("ANSWER:")
                print("─" * 60)
                print(answer)
                print("─" * 60)
                print()

            except Exception as e:
                logger.exception("Error processing question")
                print(f"\nError: {e}\n")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")

    finally:
        manager.close()
        print("Goodbye!")
        logger.info("System shut down.")


if __name__ == "__main__":
    main()
