"""
MCP Tool Server — FastAPI application exposing the document_retriever tool
via MCP-compliant endpoints.
"""

import time

from fastapi import FastAPI, HTTPException

from config import KNOWLEDGE_BASE_DIR, TOP_K_RESULTS
from logger import get_logger
from mcp_server.models import (
    RetrievedSnippet,
    ToolInputSchema,
    ToolInvocationRequest,
    ToolInvocationResponse,
    ToolListResponse,
    ToolSpec,
)
from mcp_server.retriever import DocumentRetriever

logger = get_logger("MCP.Server")

# --- FastAPI Application ---

app = FastAPI(
    title="MCP Tool Server",
    description="Model Context Protocol server exposing a document_retriever tool for semantic search over a knowledge base.",
    version="1.0.0",
)

# --- Global retriever instance (initialized on startup) ---

retriever: DocumentRetriever | None = None

# --- Tool Specification ---

DOCUMENT_RETRIEVER_SPEC = ToolSpec(
    name="document_retriever",
    description=(
        "Searches the internal knowledge base and returns relevant text snippets. "
        "Use this tool when you need factual information from internal documents "
        "such as performance reports, architecture docs, incident reports, roadmaps, "
        "and team structure."
    ),
    input_schema=ToolInputSchema(
        type="object",
        properties={
            "query": {
                "type": "string",
                "description": "The search query to run against the knowledge base.",
            }
        },
        required=["query"],
    ),
)


# --- Startup Event ---


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize the document retriever on server startup."""
    global retriever
    logger.info("Starting MCP Tool Server...")
    logger.info("Loading knowledge base from: %s", KNOWLEDGE_BASE_DIR)

    start_time = time.time()
    retriever = DocumentRetriever(KNOWLEDGE_BASE_DIR)
    elapsed = time.time() - start_time

    logger.info("Knowledge base indexed in %.2f seconds", elapsed)
    logger.info("MCP Tool Server is ready.")


# --- Endpoints ---


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for Docker and monitoring."""
    return {"status": "healthy"}


@app.get("/mcp/v1/tools", response_model=ToolListResponse)
async def list_tools() -> ToolListResponse:
    """
    MCP Tool Discovery endpoint.
    Returns the specification of all available tools on this server.
    """
    logger.info("Tool discovery request received.")
    return ToolListResponse(tools=[DOCUMENT_RETRIEVER_SPEC])


@app.post(
    "/mcp/v1/tools/document_retriever",
    response_model=ToolInvocationResponse,
)
async def invoke_document_retriever(
    request: ToolInvocationRequest,
) -> ToolInvocationResponse:
    """
    MCP Tool Invocation endpoint for the document_retriever tool.
    Accepts a query and returns relevant snippets from the knowledge base.
    """
    if retriever is None:
        raise HTTPException(status_code=503, detail="Retriever not initialized yet.")

    logger.info("Tool invocation: document_retriever(query='%s')", request.query[:80])

    start_time = time.time()
    snippets: list[RetrievedSnippet] = retriever.query(
        query_text=request.query,
        top_k=TOP_K_RESULTS,
    )
    latency_ms = (time.time() - start_time) * 1000

    logger.info(
        "document_retriever returned %d snippets in %.1f ms",
        len(snippets),
        latency_ms,
    )

    return ToolInvocationResponse(
        tool_name="document_retriever",
        results=snippets,
    )
