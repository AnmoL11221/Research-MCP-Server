# AI-Driven Research Assistant MCP Server

[![Docker Pulls](https://img.shields.io/docker/pulls/anmol1123/research-mcp-server)](https://hub.docker.com/r/anmol1123/research-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Quickstart](#quickstart)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Logging](#logging)
- [Contribution Guidelines](#contribution-guidelines)
- [License](#license)
- [MCP (Model-Context Protocol) Tool Integration](#mcp-model-context-protocol-tool-integration)
- [Example MCP Tool Usage](#example-mcp-tool-usage)
- [Docker Deployment](#docker-deployment)
- [Troubleshooting](#troubleshooting)
- [Links](#links)

---

## Overview
This project is an AI-powered research assistant platform that aggregates, summarizes, synthesizes, and answers questions about academic literature from arXiv, PubMed, and Semantic Scholar. It provides both a robust backend API (FastAPI) and a modern frontend (Streamlit) for searching, summarizing, synthesizing, Q&A, and citing academic papers.

## Features
- Unified academic search across arXiv, PubMed, and Semantic Scholar
- Summarization of academic texts using state-of-the-art models
- Synthesis of multiple paper abstracts into a single summary
- Q&A over a set of papers using Retrieval-Augmented Generation (RAG)
- Citation generation in APA style
- Redis caching for efficient repeated queries
- Professional logging and error handling

## Quickstart

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd research-mcp-server
```

### 2. Install Dependencies
It is recommended to use a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the project root:
```
SEMANTIC_SCHOLAR_API_KEY=your_actual_api_key_here  # Optional, for higher rate limits
REDIS_URL=redis://localhost:6379                   # Or your Redis instance URL
```
- The server will work without a Semantic Scholar API key, but at a lower rate limit.
- `.env` is loaded automatically using `python-dotenv`.

### 4. Start Redis (if not already running)
Make sure you have a Redis server running locally or update `REDIS_URL` in your `.env`.

### 5. Run the Backend API
```bash
uvicorn main:app --reload
```

## API Endpoints

### `POST /search`
Search for academic papers across all sources.
- **Request Body:**
  ```json
  { "query": "deep learning", "max_results": 5 }
  ```
- **Response:**
  ```json
  { "results": [ ... ], "errors": [ ... ] }
  ```

### `POST /summarize`
Summarize a given text.
- **Request Body:**
  ```json
  { "text": "...", "max_length": 150 }
  ```
- **Response:**
  ```json
  { "summary": "..." }
  ```

### `POST /search_and_summarize`
Search and summarize abstracts from all sources.
- **Request Body:**
  ```json
  { "query": "transformer models", "max_results": 3, "summary_max_length": 50, "summary_min_length": 25 }
  ```
- **Response:**
  ```json
  { "results": [ { "source": "arXiv", "title": "...", "original_abstract": "...", "summary": "..." } ], "errors": [ ... ] }
  ```

### `POST /synthesize`
Synthesize information from multiple papers into a single summary.
- **Request Body:**
  ```json
  { "papers": [ { "title": "...", "authors": ["..."], "abstract": "...", ... } ] }
  ```
- **Response:**
  ```json
  { "synthesis": "..." }
  ```

### `POST /qa`
Q&A over a set of papers using Retrieval-Augmented Generation (RAG).
- **Request Body:**
  ```json
  {
    "papers": [
      { "title": "Paper 1", "authors": ["Alice"], "abstract": "This study explores...", "source": "arXiv", "publication_date": "2023-01-01", "url": "..." },
      { "title": "Paper 2", "authors": ["Bob"], "abstract": "The main limitation was...", "source": "PubMed", "publication_date": "2022-12-01", "url": "..." }
    ],
    "question": "What was the primary limitation mentioned in these studies?"
  }
  ```
- **Response:**
  ```json
  { "answer": "The main limitation mentioned was..." }
  ```

### `POST /cite`
Generate an APA-style citation for a paper.
- **Request Body:**
  ```json
  { "title": "...", "authors": ["..."], "publication_date": "2023-01-01", "source": "arXiv", "abstract": "...", "url": "..." }
  ```
- **Response:**
  ```json
  { "citation": "..." }
  ```

## Environment Variables
- `SEMANTIC_SCHOLAR_API_KEY` (optional): For higher rate limits on Semantic Scholar API.
- `REDIS_URL`: Redis connection string (default: `redis://localhost:6379`).

## Logging
- Logs are output to the console with timestamps, log level, and message.
- Info, warning, and error logs are included for observability and debugging.

## Contribution Guidelines
- Fork the repository and create a feature branch.
- Write clear, well-documented code.
- Submit a pull request with a description of your changes.
- Please do not commit secrets or `.env` files.

## License
MIT License (or specify your license here) 

## MCP (Model-Context Protocol) Tool Integration

This project is now fully compliant with the Model-Context Protocol (MCP), making it directly usable as a tool by AI hosts like Claude Desktop and other MCP-compatible systems.

### How to Use as an MCP Tool

1. **Install dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the MCP server**:
   ```bash
   python mcp_server.py
   ```
   - By default, this uses the `stdio` transport, which is required for Claude Desktop integration.
   - The server exposes the following tools: `search`, `summarize`, `search_and_summarize`, `synthesize`, `cite`, and `qa`.

3. **Connect to Claude Desktop or another MCP host**:
   - In Claude Desktop, add a new MCP tool in your config (e.g., `claude_desktop_config.json`) pointing to your `mcp_server.py` script.
   - Example config snippet:
     ```json
     {
       "mcpServers": {
         "research-assistant": {
           "command": "/usr/bin/python3",
           "args": ["/absolute/path/to/mcp_server.py"]
         }
       }
     }
     ```
   - Restart Claude Desktop and enable the tool from the hammer icon in the chat UI.

4. **Usage**:
   - Claude (or any MCP host) will now be able to call your research tools directly, with full support for tool invocation, argument passing, and structured results.

### Dual API and MCP Support
- You can continue to use the FastAPI server (`main.py`) for HTTP API access.
- The MCP server (`mcp_server.py`) is for direct tool integration with AI hosts. 

## Docker Deployment

You can deploy this project as a containerized MCP server using Docker.

### 1. Create a Dockerfile
Add a file named `Dockerfile` to your project root with the following content:

```Dockerfile
# Use an official Python base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Set environment variables (optional)
# ENV SEMANTIC_SCHOLAR_API_KEY=your_actual_api_key_here
# ENV REDIS_URL=redis://localhost:6379

# Default command: run the MCP server
CMD ["python", "mcp_server.py"]
```

### 2. Build the Docker Image
```bash
docker build -t research-mcp-server .
```

### 3. Run the Docker Container
```bash
docker run --rm -it research-mcp-server
```
- You can pass environment variables with `-e` if needed, e.g.:
  ```bash
  docker run --rm -it -e SEMANTIC_SCHOLAR_API_KEY=your_key research-mcp-server
  ```

### 4. Connect to Claude Desktop or MCP Host
- Use the same config as before, but set the `command` to `docker` and use the appropriate arguments to run the container if you want Claude to launch it via Docker. (Or run the container manually and connect via HTTP/SSE if you adapt the transport.)

---

You now have a fully containerized, MCP-compliant research assistant ready for deployment and publishing! 

## Example MCP Tool Usage

**Request:**
```json
{
  "query": "AI artificial intelligence evolving daily development progress",
  "max_results": 8,
  "summary_max_length": 80,
  "summary_min_length": 40
}
```

**Response:**
```json
{
  "results": [
    {
      "source": "arXiv",
      "title": "Positive AI: Key Challenges in Designing Artificial Intelligence for Wellbeing",
      "summary": "Many people are increasingly worried about AI's impact on their lives. To ensure AI progresses beneficially, some researchers have proposed 'wellbeing' as a key objective to govern AI. This article addresses key challenges in designing AI for wellbeing."
    },
    // ... more results ...
  ],
  "errors": []
}
```

---

## Troubleshooting

- **Model download is slow or stuck:** The first run may take several minutes as models are downloaded. Check Docker or terminal logs for progress.
- **Out of memory or crash:** Use a machine with more RAM/CPU, or try a smaller model if available.
- **No response in Claude Desktop:** Ensure the MCP server is running, Docker is running, and your config paths are correct. Check logs for Python errors.
- **Docker image not found:** Make sure your image is public and the name matches what you pushed to Docker Hub.
- **Claude Desktop can't find the tool:** Double-check your config and restart Claude Desktop after changes.

---

## Links
- [Docker Hub: anmol1123/research-mcp-server](https://hub.docker.com/r/anmol1123/research-mcp-server)
- [Smythery MCP Registry](https://smythery.ai/)
- [Model Context Protocol (MCP) Docs](https://modelcontextprotocol.io/docs/)
- [Claude Desktop](https://www.anthropic.com/claude) 