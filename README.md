# Research Assistant API

AI-powered research assistant that searches academic papers across arXiv, PubMed, and Semantic Scholar. Provides summarization, synthesis, and Q&A capabilities through both HTTP API and MCP integration for Claude Desktop.

## Features

- Search across multiple academic databases
- AI-powered text summarization
- Multi-paper synthesis
- Question answering over research papers
- Citation generation
- Redis caching
- **Dual Mode**: HTTP API + MCP Server for Claude Desktop

## Quick Start

### Local Setup

```bash
git clone <your-repo-url>
cd research-mcp-server
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

```bash
SEMANTIC_SCHOLAR_API_KEY=your_key_here  # Optional
REDIS_URL=redis://localhost:6379       # Optional
PORT=8080                              # For HTTP mode only
```

## Usage

### As MCP Server (Claude Desktop Integration)

1. **Update Claude Desktop Config** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "research-assistant": {
      "command": "/Users/home/Desktop/research-mcp-server/.venv/bin/python3",
      "args": ["/Users/home/Desktop/research-mcp-server/mcp_server.py"]
    }
  }
}
```

2. **Start MCP Server**:
```bash
source .venv/bin/activate
python mcp_server.py
```

3. **Restart Claude Desktop** and look for the research tools in your chat!

### As HTTP API Server

```bash
source .venv/bin/activate
PORT=8080 python mcp_server.py
# OR
uvicorn mcp_server:app --host 0.0.0.0 --port 8080
```

## API Endpoints

- `GET /` - Service info and available endpoints
- `GET /health` - Health check
- `POST /api/search` - Search academic papers
- `POST /api/summarize` - Summarize text
- `POST /api/search_and_summarize` - Search and summarize papers
- `POST /api/synthesize` - Combine multiple papers
- `POST /api/cite` - Generate citations
- `POST /api/qa` - Answer questions based on papers

## MCP Tools (Available in Claude)

- `search` - Search academic papers
- `summarize` - Summarize text
- `search_and_summarize` - Search and summarize papers
- `synthesize` - Combine multiple papers
- `cite` - Generate citations
- `qa` - Answer questions based on papers

## Usage Examples

### HTTP API
```bash
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "max_results": 5}'
```

### Claude Desktop
Just ask Claude: *"Search for recent papers on machine learning and summarize them"*

## Requirements

- **Python 3.11+** (required for MCP functionality)
- Virtual environment (recommended)
- Redis (optional, for caching)

## Docker Deployment

```bash
docker build -t research-assistant .
docker run -p 8080:8080 -e PORT=8080 research-assistant
```

## License

MIT License
