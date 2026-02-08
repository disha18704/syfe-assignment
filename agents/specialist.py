"""
Specialist Agent — Synthesizes a grounded, cited answer from retrieved context.
"""

from openai import OpenAI

from agents.prompts import SPECIALIST_SYSTEM_PROMPT
from config import OPENAI_API_KEY, OPENAI_MODEL
from logger import get_logger
from mcp_server.models import RetrievedSnippet

logger = get_logger("Specialist")


class SpecialistAgent:
    """
    The Specialist Agent receives a user question and retrieved context snippets,
    then uses an LLM to synthesize a well-cited, grounded answer.
    """

    def __init__(self) -> None:
        """Initialize the Specialist with an OpenAI client."""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        logger.info("SpecialistAgent initialized (model=%s)", self.model)

    def _format_context(self, snippets: list[RetrievedSnippet]) -> str:
        """
        Format retrieved snippets into a structured context block for the LLM.

        Args:
            snippets: List of retrieved document snippets with metadata.

        Returns:
            Formatted context string.
        """
        if not snippets:
            return "No context snippets were retrieved."

        context_parts: list[str] = []
        for i, snippet in enumerate(snippets, 1):
            context_parts.append(
                f"--- Snippet {i} ---\n"
                f"Source: {snippet.source}\n"
                f"Section: {snippet.section}\n"
                f"Relevance Score: {snippet.relevance_score}\n"
                f"Content:\n{snippet.text}\n"
            )
        return "\n".join(context_parts)

    def run(
        self, question: str, context_snippets: list[RetrievedSnippet]
    ) -> str:
        """
        Generate a synthesized answer based on the question and context.

        Args:
            question: The original user question.
            context_snippets: Retrieved document snippets with source metadata.

        Returns:
            The Specialist's synthesized answer with citations.
        """
        formatted_context = self._format_context(context_snippets)

        user_message = (
            f"## User Question\n{question}\n\n"
            f"## Retrieved Context\n{formatted_context}\n\n"
            "Please synthesize a comprehensive answer based on the context above. "
            "Remember to cite all sources inline."
        )

        logger.debug("Specialist prompt:\n%s", user_message)
        logger.info("Calling LLM for synthesis (model=%s)...", self.model)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SPECIALIST_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,  # Low temperature for factual, grounded responses
            max_tokens=1500,
        )

        answer = response.choices[0].message.content or "No answer generated."
        logger.info("Specialist generated answer (%d characters)", len(answer))
        return answer
