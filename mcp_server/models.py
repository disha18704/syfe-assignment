"""
Pydantic models defining the MCP protocol request/response schemas.
"""

from typing import Any

from pydantic import BaseModel, Field


# --- Tool Discovery Models ---


class ToolInputSchema(BaseModel):
    """JSON Schema describing the input parameters for a tool."""

    type: str = "object"
    properties: dict[str, Any] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)


class ToolSpec(BaseModel):
    """Specification of a single MCP tool."""

    name: str = Field(..., description="Unique name of the tool")
    description: str = Field(..., description="Human-readable description of what the tool does")
    input_schema: ToolInputSchema = Field(
        ..., description="JSON Schema for the tool's input parameters"
    )


class ToolListResponse(BaseModel):
    """Response for GET /mcp/v1/tools — lists all available tools."""

    tools: list[ToolSpec]


# --- Tool Invocation Models ---


class ToolInvocationRequest(BaseModel):
    """Request body for invoking a tool."""

    query: str = Field(..., description="The search query to run against the knowledge base")


class RetrievedSnippet(BaseModel):
    """A single retrieved document snippet with source metadata."""

    text: str = Field(..., description="The content of the retrieved snippet")
    source: str = Field(..., description="The source filename (e.g., 'q3_model_performance.md')")
    section: str = Field(..., description="The section heading within the source document")
    relevance_score: float = Field(
        ..., description="Relevance score (0.0 to 1.0, higher is more relevant)"
    )


class ToolInvocationResponse(BaseModel):
    """Response for POST /mcp/v1/tools/document_retriever."""

    tool_name: str = Field(default="document_retriever")
    results: list[RetrievedSnippet] = Field(default_factory=list)
