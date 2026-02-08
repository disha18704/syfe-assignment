AI Engineering Intern Technical Assignment
Multi-Agent Document Analysis System
1. Assignment Scenario: The Analyst Team
Your team is developing an advanced internal system to answer complex, cross-document questions. This requires a
modular architecture where a central orchestrator (the Manager Agent) can access specialized data services (via MCP)
and delegate final synthesis to a specialized agent (the Specialist Agent).
You are tasked with building a minimal viable prototype of this Multi-Agent Document Analysis System.
2. Deliverables
The candidate must submit a single repository containing:

3. Technical Requirements
A. Component 1: The MCP Tool Server (Knowledge Retriever)
You must create a simple web service that acts as a Model Context Protocol (MCP) Server.

B. Component 2: A2A Orchestration (Manager and Specialist Agents)
You must implement a Python script that orchestrates a two-agent workflow.

C. Engineering & MLOps Basics
1. Source Code: Python project containing the MCP Server and the A2A Orchestration script.
2. Knowledge Base: A small set of 3-5 technical documents (e.g., Markdown or text files) to serve as the data source.
3. README.md: A comprehensive document detailing the setup, usage, MCP specification implementation, A2A design
choices, and self-evaluation.

Framework: Use a Python web framework (e.g., FastAPI or Flask).
Tool Implementation: The server must expose a tool named document_retriever .
Function: This tool accepts a query (string) and returns a list of relevant text snippets from your local Knowledge
Base. A simple implementation (e.g., using basic string matching or a small in-memory vector store like faiss or
chroma ) is acceptable.
MCP Compliance: The server must expose the tool's specification via the standard MCP endpoint (e.g.,
/mcp/v1/tools ) and handle tool invocation requests according to the protocol.

Manager Agent (Orchestrator):
Receives a user question (e.g., from command line input).
Uses an LLM (simulated or real API call) to determine if the document_retriever tool is needed.
If needed, it calls the document_retriever tool on your local MCP Server.
It then constructs a final prompt for the Specialist Agent, including the original question and the retrieved context.
Specialist Agent (Synthesizer):
This is an LLM invocation with a specific system prompt (e.g., "You are a meticulous technical analyst. Your job is
to synthesize a clear, concise answer based only on the provided context and the user's question.").
It generates the final, high-quality answer.

Dependencies: Include a requirements.txt or pyproject.toml file.
Execution: Provide clear instructions in the README.md on how to start the MCP Server and how to run the A2A
Orchestration script.
Version Control: The final submission must be a link to a Git repository.

4 A2A Implementation Guidance
While the implementation details are up to the candidate, a successful submission should address the following A2A
concepts:

5. Knowledge Base
The candidate should create a small knowledge base (e.g., 3-5 files) in their repository. Each file should contain a few
paragraphs of technical text on a specific topic (e.g., "Q3 Model Performance Report," "Data Pipeline Architecture," "Future
Feature Roadmap"). The Manager Agent's query should require information from at least two of these documents to test the
retrieval and synthesis process.
6. Bonus & Extra Credit Features (Optional)
These features are not mandatory but will significantly increase the score and demonstrate a deeper understanding of
production-ready AI systems.
State Management: How is the conversation state passed from the Manager to the Specialist? (e.g., passing the entire
history, or a summarized context).
Protocol Definition: How do the agents "talk" to each other? Is it via a shared database, a direct API call, or a
message queue? For this prototype, a direct function call or HTTP request is sufficient, but the candidate should explain
the choice.
Specialization: The Specialist Agent should have a distinct "personality" or "expertise" defined in its system prompt that
differs from the Manager Agent.

1. Source Grounding and Citation (Highly Recommended): The final answer from the Specialist Agent should include a
footer or inline references that point back to the specific document(s) and, if possible, the section/paragraph from the
Knowledge Base that was used to formulate the answer. This demonstrates an understanding of grounding and
hallucination mitigation.
2. Basic Monitoring/Logging: Implement simple logging (e.g., using Python's logging module) to track key events, such as:
Manager Agent's decision to call the tool.
Latency of the MCP tool call.
The final prompt sent to the Specialist Agent.
3. Containerization: Provide a Dockerfile that allows the entire system (MCP Server and A2A script) to be built and run
easily within a containerized environment. This demonstrates familiarity with MLOps best practices.
4. Configuration Management: Externalize all key configurations (e.g., LLM API keys, model names, server port) into a
configuration file (e.g., .env or config.yaml) instead of hardcoding them.