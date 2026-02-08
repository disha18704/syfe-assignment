"""
Manager Agent — Orchestrates the multi-agent workflow.
Decides whether document retrieval is needed, calls the MCP Tool Server,
and delegates synthesis to the Specialist Agent.
"""

import json
import time

import httpx
from openai import OpenAI

from agents.prompts import MANAGER_SYSTEM_PROMPT
from agents.specialist import SpecialistAgent
from config import OPENAI_API_KEY, OPENAI_MODEL, MCP_SERVER_URL, TOP_K_RESULTS
from logger import get_logger
from mcp_server.models import RetrievedSnippet

logger = get_logger("Manager")


class ManagerAgent:
    """
    The Manager Agent is the orchestrator of the multi-agent system.
    It receives user questions, decides on tool usage via an LLM,
    calls the MCP Tool Server for retrieval, and delegates to the Specialist.
    """

    def __init__(self) -> None:
        """Initialize the Manager with OpenAI client, HTTP client, and Specialist."""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.mcp_server_url = MCP_SERVER_URL
        self.http_client = httpx.Client(timeout=30.0)
        self.specialist = SpecialistAgent()
        logger.info(
            "ManagerAgent initialized (model=%s, mcp_server=%s)",
            self.model,
            self.mcp_server_url,
        )

    def discover_tools(self) -> list[dict]:
        """
        Call the MCP Tool Server's discovery endpoint to list available tools.
        This demonstrates MCP tool discovery.

        Returns:
            List of tool specifications from the MCP server.

        Raises:
            ConnectionError: If the MCP server is not reachable.
        """
        url = f"{self.mcp_server_url}/mcp/v1/tools"
        logger.info("Discovering tools from MCP server: GET %s", url)

        try:
            response = self.http_client.get(url)
            response.raise_for_status()
            data = response.json()
            tools = data.get("tools", [])
            logger.info(
                "Discovered %d tool(s): %s",
                len(tools),
                [t["name"] for t in tools],
            )
            return tools
        except httpx.ConnectError:
            logger.error(
                "Cannot connect to MCP server at %s. Is it running?",
                self.mcp_server_url,
            )
            raise ConnectionError(
                f"Cannot connect to MCP server at {self.mcp_server_url}. "
                "Please start the MCP server first with: "
                "uvicorn mcp_server.server:app --port 8000"
            )

    def invoke_tool(self, query: str) -> list[RetrievedSnippet]:
        """
        Invoke the document_retriever tool on the MCP server.

        Args:
            query: The search query to send to the retriever.

        Returns:
            List of RetrievedSnippet objects from the knowledge base.
        """
        url = f"{self.mcp_server_url}/mcp/v1/tools/document_retriever"
        logger.info("Invoking tool: POST %s (query='%s')", url, query[:80])

        start_time = time.time()
        response = self.http_client.post(url, json={"query": query})
        response.raise_for_status()
        latency_ms = (time.time() - start_time) * 1000

        data = response.json()
        snippets = [RetrievedSnippet(**r) for r in data.get("results", [])]

        logger.info(
            "MCP tool call completed in %.1f ms — returned %d snippet(s)",
            latency_ms,
            len(snippets),
        )
        for i, s in enumerate(snippets, 1):
            logger.info(
                "  Snippet %d: [%s / %s] (score=%.4f)",
                i,
                s.source,
                s.section,
                s.relevance_score,
            )

        return snippets

    def _decide_action(self, user_question: str) -> dict:
        """
        Use the LLM to decide whether the user's question requires
        document retrieval or can be answered directly.

        Args:
            user_question: The raw user question.

        Returns:
            Parsed JSON dict with 'action' key ('retrieve' or 'direct_answer').
        """
        logger.info("Asking LLM to decide action for question: '%s'", user_question[:100])

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": MANAGER_SYSTEM_PROMPT},
                {"role": "user", "content": user_question},
            ],
            temperature=0.0,  # Deterministic decision-making
            max_tokens=200,
        )

        raw_response = response.choices[0].message.content or "{}"
        logger.debug("Manager LLM raw response: %s", raw_response)

        # Parse JSON from the LLM response
        try:
            # Strip potential markdown code fences
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1]
                cleaned = cleaned.rsplit("```", 1)[0]
            decision = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            logger.warning(
                "Failed to parse Manager LLM response as JSON: %s", raw_response
            )
            # Default to retrieval if parsing fails
            decision = {"action": "retrieve", "query": user_question}

        logger.info("Manager decision: %s", decision.get("action", "unknown"))
        return decision

    def run(self, user_question: str) -> str:
        """
        Execute the full orchestration workflow for a user question.

        Flow:
        1. LLM decides if retrieval is needed
        2. If yes, call MCP Tool Server for document retrieval
        3. Construct enriched context
        4. Delegate to Specialist Agent for synthesis
        5. Return the final answer

        Args:
            user_question: The user's question.

        Returns:
            The final synthesized answer.
        """
        logger.info("=" * 60)
        logger.info("Processing question: '%s'", user_question)
        logger.info("=" * 60)

        # Step 1: LLM decides the action
        decision = self._decide_action(user_question)

        if decision.get("action") == "direct_answer":
            answer = decision.get("answer", "I'm not sure how to respond to that.")
            logger.info("Manager answered directly (no retrieval needed).")
            return answer

        # Step 2: Retrieve documents from MCP server
        search_query = decision.get("query", user_question)
        logger.info("Manager decided to retrieve documents with query: '%s'", search_query)

        try:
            snippets = self.invoke_tool(search_query)
        except Exception as e:
            logger.error("MCP tool invocation failed: %s", e)
            return f"Error: Failed to retrieve documents from MCP server: {e}"

        if not snippets:
            logger.warning("No snippets retrieved. Specialist will note missing info.")

        # Step 3 & 4: Delegate to Specialist Agent
        logger.info(
            "Delegating to Specialist Agent with %d context snippet(s)...",
            len(snippets),
        )
        answer = self.specialist.run(user_question, snippets)

        logger.info("Final answer generated (%d characters).", len(answer))
        return answer

    def close(self) -> None:
        """Clean up resources."""
        self.http_client.close()
