# AI-Driven Research Assistant MCP Server

## Overview
This project is an AI-powered research assistant platform that aggregates, summarizes, synthesizes, and answers questions about academic literature from arXiv, PubMed, and Semantic Scholar. It is implemented as a **true Model Context Protocol (MCP) server** using FastMCP, making it directly usable as a tool by AI hosts like Claude Desktop and deployable on MCP registries like Smythery.

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

### 5. Run the MCP Server (Local Testing)
```bash
python mcp_server.py
```
- This will start the MCP server using FastMCP and stdio transport.
- **Do NOT use FastAPI/uvicorn for MCP tool integration.**

## MCP Tool Integration with Claude Desktop

1. **Edit your Claude Desktop config** (usually at `~/Library/Application Support/Claude/claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "research-assistant": {
         "command": "/absolute/path/to/python3",
         "args": ["/absolute/path/to/mcp_server.py"]
       }
     }
   }
   ```
2. **Restart Claude Desktop** and enable the tool in the Developer > Local MCP servers panel.
3. **Test the tool** in Claude Desktop.

## Deploying on Smythery or Other MCP Registries

1. **Ensure your Dockerfile uses:**
   ```dockerfile
   CMD ["python", "mcp_server.py"]
   ```
   - Do NOT use `uvicorn` or expose a port for stdio MCP servers.
2. **Add a `smithery.yaml` file:**
   ```yaml
   name: research-mcp-server
   description: AI-Driven Research Assistant MCP Server
   language: python
   entrypoint: python mcp_server.py
   transport: stdio
   dependencies:
     - requirements.txt
   ```
3. **Push your code and deploy on Smythery.**

## Troubleshooting
- **Server disconnected / Could not attach:** Make sure you are running a true MCP server (not FastAPI/HTTP) and using FastMCP with stdio transport.
- **Timeouts or handshake errors:** Ensure all logs/prints go to stderr, and only JSON-RPC is sent to stdout.
- **Docker build errors:** Use a standard torch version (e.g., `torch==2.2.2`) and do not use `+cpu` unless you add the correct extra index URL.
- **smithery.yaml missing:** Add the file as shown above for Smythery/cloud deployment.

## Not a REST API
This project is **not a REST API** and is not intended to be used with HTTP clients or as a web server. It is a true MCP tool server for use with Claude Desktop and MCP registries.

## License
MIT License 
