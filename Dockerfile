FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed by some Python packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY . .

# Expose the MCP server port
EXPOSE 8000

# Default command: start the MCP Tool Server
CMD ["uvicorn", "mcp_server.server:app", "--host", "0.0.0.0", "--port", "8000"]
