# Multi-Agent Document Analysis System

A modular, multi-agent system that answers complex, cross-document questions by combining a **Model Context Protocol (MCP) Tool Server** for knowledge retrieval with an **Agent-to-Agent (A2A) orchestration** pipeline powered by OpenAI.

---

## Architecture

```
                          ┌─────────────────────┐
                          │    User (CLI)        │
                          └──────────┬──────────┘
                                     │ question
                                     ▼
                          ┌─────────────────────┐
                          │   Manager Agent      │
                          │   (Orchestrator)     │
                          │                     │
                          │  LLM Call #1:       │
                          │  "Do I need to      │
                          │   retrieve docs?"   │
                          └──────┬──────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │ YES: retrieve            │ NO: direct answer
                    ▼                          ▼
         ┌──────────────────┐          Return answer
         │  MCP Tool Server │          directly
         │  (FastAPI)       │
         │                  │
         │  ChromaDB        │
         │  semantic search │
         └────────┬─────────┘
                  │ snippets + metadata
                  ▼
         ┌──────────────────┐
         │ Specialist Agent │
         │ (Synthesizer)    │
         │                  │
         │ LLM Call #2:     │
         │ "Synthesize a    │
         │  cited answer"   │
         └────────┬─────────┘
                  │ final answer
                  ▼
         Printed to CLI
```

### File Structure

```
syfe/
├── config.py                 # Centralized configuration loader (.env)
├── logger.py                 # Shared logging setup
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration template
│
├── knowledge_base/           # 5 interlinked markdown documents
│   ├── q3_model_performance.md
│   ├── data_pipeline_architecture.md
│   ├── feature_roadmap.md
│   ├── incident_report_aug.md
│   └── team_structure.md
│
├── mcp_server/               # MCP Tool Server (Component 1)
│   ├── server.py             # FastAPI app with MCP endpoints
│   ├── retriever.py          # ChromaDB document retriever
│   └── models.py             # Pydantic schemas for MCP protocol
│
└── agents/                   # A2A Orchestration (Component 2)
    ├── manager.py            # Manager Agent (orchestrator)
    ├── specialist.py         # Specialist Agent (synthesizer)
    └── prompts.py            # System prompts for both agents
```

---

## MCP Specification

The MCP Tool Server implements a simplified Model Context Protocol with two key endpoints:

### Tool Discovery: `GET /mcp/v1/tools`

Returns the specification of all available tools.

**Response example:**
```json
{
  "tools": [
    {
      "name": "document_retriever",
      "description": "Searches the internal knowledge base and returns relevant text snippets.",
      "input_schema": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "The search query to run against the knowledge base."
          }
        },
        "required": ["query"]
      }
    }
  ]
}
```

### Tool Invocation: `POST /mcp/v1/tools/document_retriever`

Invokes the retriever tool with a query.

**Request:**
```json
{
  "query": "Q3 model accuracy improvement"
}
```

**Response:**
```json
{
  "tool_name": "document_retriever",
  "results": [
    {
      "text": "Our primary classification model achieved an accuracy of 94.7%...",
      "source": "q3_model_performance.md",
      "section": "Key Metrics",
      "relevance_score": 0.8721
    }
  ]
}
```

### Why MCP?

The MCP pattern decouples data access from agent logic. The Manager Agent doesn't know *how* retrieval works — it only knows the tool's interface. This means:
- The retrieval backend (ChromaDB) could be swapped without changing agent code.
- Multiple agents or systems could share the same MCP server.
- The tool specification serves as a self-documenting API contract.

---

## A2A Design Choices

### State Management

The Manager Agent passes state to the Specialist via a **constructed prompt** — the original question plus all retrieved context snippets (with source metadata). This is the simplest and most transparent form of A2A state passing:

- **Pros:** No shared mutable state, easy to debug (full context is logged), no infrastructure overhead.
- **Cons:** Context window limits could be an issue with very large knowledge bases.

### Protocol Definition

The agents communicate via **direct function calls** within the orchestration script:
- Manager calls `specialist.run(question, context_snippets)`.
- This is a synchronous, in-process call.
- For a production system, this could evolve into HTTP calls between microservices, or a message queue.

I made the choice of direct function calls to avoid avoids unnecessary infrastructure.

### Specialization

Each agent has a **distinct system prompt** that defines its role and behavior:

| Agent | Personality | Key Behaviors |
|---|---|---|
| **Manager** | Analytical coordinator | Decides actions, formulates search queries, delegates work |
| **Specialist** | Meticulous technical analyst | Synthesizes from context only, cites sources, flags missing info |

The Manager is never asked to write the final answer. The Specialist is never asked to decide what tools to call. This separation ensures each agent stays focused on its strength.

---

### Knowledge Base Design

The documents are intentionally designed so that important questions require information from multiple sources:

- *"What caused Q3 improvements?"* → needs `q3_model_performance.md` + `data_pipeline_architecture.md`
- *"How was the August incident resolved and what prevented future issues?"* → needs `incident_report_aug.md` + `data_pipeline_architecture.md` + `feature_roadmap.md`
- *"Who is responsible for the real-time inference project?"* → needs `feature_roadmap.md` + `team_structure.md`

### Grounding and Citations

Each chunk stored in ChromaDB carries metadata (`source` filename + `section` heading) and a cosine similarity relevance score. The Specialist Agent is instructed to cite these inline: `[Source: filename, Section: section_name, Score: relevance_score]`. The Sources footer at the end of each answer also includes relevance scores so the reader can assess retrieval confidence. This enables verifiable, grounded, and transparent answers.

---

## Setup & Installation

### Prerequisites

- Python 3.12.8
- An OpenAI API key

### Step 1: Clone and Install

```bash
git clone <repository-url>
cd syfe

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Step 3: Start the MCP Tool Server

In **Terminal 1**:

```bash
uvicorn mcp_server.server:app --host 0.0.0.0 --port 8000
```

### Step 4: Run the Orchestration Script

In **Terminal 2**:

```bash
python main.py
```

For verbose logging (DEBUG level):

```bash
python main.py --verbose
```

---

## Usage

### Interactive CLI

```
╔══════════════════════════════════════════════════════════════╗
║       Multi-Agent Document Analysis System                  ║
╚══════════════════════════════════════════════════════════════╝

Connecting to MCP Tool Server...
Connected! Discovered 1 tool(s): document_retriever

> Ask a question (or 'quit' to exit): What caused the Q3 model performance improvement?

Processing...

────────────────────────────────────────────────────────────────
ANSWER:
────────────────────────────────────────────────────────────────
The Q3 model performance improvement was driven by two key factors...
[Source: q3_model_performance.md, Section: Contributing Factors, Score: 0.8342]
...

Sources:
- q3_model_performance.md, Section: Contributing Factors, Relevance: 0.8342
- data_pipeline_architecture.md, Section: Integration with ML Models, Relevance: 0.8124
────────────────────────────────────────────────────────────────
```

### Sample Questions to Try

1. **Single-document:** "What are the Q3 model performance metrics?"
2. **Cross-document:** "What caused the Q3 model performance improvement, and how did the August incident affect the data pipeline that contributed to it?"
3. **Team + Roadmap:** "Who is responsible for the Q4 real-time inference project, and what does it depend on?"
4. **Conversational (no retrieval):** "Hello, what can you help me with?"

---

## Bonus Features

### Source Grounding and Citations

The Specialist Agent is instructed to cite every factual claim inline with `[Source: filename, Section: section_name, Score: relevance_score]` and include a Sources footer with relevance scores. The relevance score (0.0–1.0, derived from ChromaDB cosine similarity) gives the reader transparency into how confident the retrieval was for each cited snippet. This is enabled by ChromaDB metadata and distance scores attached to each chunk.

### Logging and Monitoring

All key events are logged using Python's `logging` module:
- Manager's decision to call the tool (or not)
- MCP tool call latency (in milliseconds)
- Retrieved snippet details (source, section, relevance score)
- The full prompt sent to the Specialist (at DEBUG level)

Logs are written to both the console and `system.log` file.

### Configuration Management

All settings are externalized in a `.env` file:
- `OPENAI_API_KEY`, `OPENAI_MODEL` (default: `gpt-4o-mini`)
- `MCP_SERVER_HOST`, `MCP_SERVER_PORT` (default: `localhost:8000`)
- `TOP_K_RESULTS` (default: `5` — number of snippets returned per retrieval)
- `LOG_LEVEL` (default: `INFO`; set to `DEBUG` for full prompt visibility)

A `.env.example` template is provided. No secrets are hardcoded.

### Containerization

A `Dockerfile` and `docker-compose.yml` are provided to run the entire system in containers. See the Docker section below.

#### Running with Docker

```bash
# Build and start both services in the background
docker-compose up --build -d

# Wait ~2 minutes for the MCP server to download the embedding model and index documents
# You can check progress with:
docker logs -f mcp-tool-server

# Once you see "MCP Tool Server is ready", attach to the orchestrator to ask questions:
docker attach a2a-orchestrator

# To stop everything:
docker-compose down
```

---

## Self-Evaluation

### Strengths

- **Clean separation of concerns:** MCP server, Manager agent, and Specialist agent are fully decoupled. Each can be modified independently.
- **MCP compliance:** The server implements standard tool discovery and invocation endpoints with well-defined Pydantic schemas.
- **Semantic search:** ChromaDB provides meaningful retrieval beyond keyword matching, which improves answer quality.
- **Grounded answers:** Citations trace every claim back to a specific document and section.
- **Comprehensive logging:** Full observability of the decision and retrieval pipeline.
- **Configuration management:** All secrets and settings externalized; no hardcoded values.

### Limitations

- **Knowledge base scale:** With only 5 documents, retrieval quality could be better tested with a larger corpus.
- **Single retrieval pass:** The Manager makes one retrieval call. A production system might iterate (retrieve → assess → retrieve more).
- **No conversation memory:** Each question is independent. Multi-turn conversation would require session state.
- **No evaluation framework:** There are no automated tests for retrieval quality or answer correctness.
- **Simplified MCP:** The protocol implementation covers discovery and invocation but does not implement the full MCP specification (e.g., streaming, authentication).
