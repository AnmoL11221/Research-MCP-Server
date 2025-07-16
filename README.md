# AI-Driven Research Assistant MCP Server

## Overview
This project is an AI-powered research assistant server that aggregates, summarizes, and synthesizes academic literature from arXiv, PubMed, and Semantic Scholar. It provides a unified API for searching, summarizing, synthesizing, and citing academic papers, making it easier for students, researchers, and educators to access and understand scientific knowledge.

## Features
- Unified academic search across arXiv, PubMed, and Semantic Scholar
- Summarization of academic texts using state-of-the-art models
- Synthesis of multiple paper abstracts into a single summary
- Q&A over a set of papers using Retrieval-Augmented Generation (RAG)
- Citation generation in APA style
- Redis caching for efficient repeated queries
- Professional logging and error handling

## Setup Instructions

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

### 5. Run the Server
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