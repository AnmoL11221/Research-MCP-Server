# AI-Driven Research Assistant MCP Server

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
- **Streamlit frontend**: User-friendly web app for search, citation, summarization, and Q&A
- Configurable backend URL in the frontend
- Backend warnings (e.g., rate limits) are suppressed in the UI for a cleaner experience

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

### 6. Run the Streamlit Frontend
```bash
streamlit run app.py
```
- Open your browser to `http://localhost:8501`.
- Enter your backend API URL (e.g., `http://localhost:8000` for local development).

## Streamlit App Features
- **Configurable Backend URL**: Easily switch between local and deployed backends.
- **Search**: Enter a research query and view results from all sources.
- **Cite**: Generate APA-style citations for any paper.
- **Summarize**: Get concise summaries of paper abstracts.
- **Q&A**: Ask natural language questions about the search results using RAG.
- **Clean UI**: Backend warnings (e.g., rate limits) are not shown to users; only critical errors are displayed.

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
- You can continue to use the FastAPI server (`main.py`) for HTTP API access and the Streamlit frontend (`app.py`).
- The MCP server (`mcp_server.py`) is for direct tool integration with AI hosts. 