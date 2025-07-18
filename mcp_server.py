import sys
import builtins
import logging

builtins.print = lambda *args, **kwargs: __builtins__.print(*args, file=sys.stderr, **kwargs)
logging.basicConfig(stream=sys.stderr)

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from academic_search import search_arxiv, search_pubmed, search_semantic_scholar
from summarizer import summarize_text
from cache import get_from_cache, set_to_cache

app = Server("research-assistant")

@app.tool()
async def search(query: str, max_results: int = 5) -> dict:
    cache_key = f"search:{query}:{max_results}"
    cached = get_from_cache(cache_key)
    if cached is not None:
        return cached
    results = []
    errors = []
    loop = asyncio.get_event_loop()
    def run_sync(func, *args, **kwargs):
        return loop.run_in_executor(None, func, *args, **kwargs)
    tasks = [
        run_sync(search_arxiv, query, max_results),
        run_sync(search_pubmed, query, max_results),
        search_semantic_scholar(query, max_results)
    ]
    results_list = await asyncio.gather(*tasks, return_exceptions=True)
    for idx, res in enumerate(results_list):
        if isinstance(res, Exception):
            if idx == 0:
                errors.append(f"arXiv: {str(res)}")
            elif idx == 1:
                errors.append(f"PubMed: {str(res)}")
            elif idx == 2:
                errors.append(f"Semantic Scholar: {str(res)}")
        else:
            results.extend(res)
    response = {"results": results, "errors": errors}
    set_to_cache(cache_key, response, 3600)
    return response

@app.tool()
async def summarize(text: str, max_length: int = 150) -> dict:
    try:
        summary = summarize_text(text, max_length=max_length)
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def search_and_summarize(query: str, max_results: int = 5, summary_max_length: int = 50, summary_min_length: int = 25) -> dict:
    results = []
    errors = []
    loop = asyncio.get_event_loop()
    def run_sync(func, *args, **kwargs):
        return loop.run_in_executor(None, func, *args, **kwargs)
    tasks = [
        run_sync(search_arxiv, query, max_results),
        run_sync(search_pubmed, query, max_results),
        search_semantic_scholar(query, max_results)
    ]
    results_list = await asyncio.gather(*tasks, return_exceptions=True)
    for idx, res in enumerate(results_list):
        if isinstance(res, Exception):
            if idx == 0:
                errors.append(f"arXiv: {str(res)}")
            elif idx == 1:
                errors.append(f"PubMed: {str(res)}")
            elif idx == 2:
                errors.append(f"Semantic Scholar: {str(res)}")
        else:
            results.extend(res)
    summarized = []
    for entry in results:
        try:
            summary = summarize_text(
                entry["abstract"],
                max_length=summary_max_length,
                min_length=summary_min_length
            )
        except Exception as e:
            summary = f"Summarization failed: {e}"
        summarized.append({
            "source": entry["source"],
            "title": entry["title"],
            "original_abstract": entry["abstract"],
            "summary": summary
        })
    return {"results": summarized, "errors": errors}

@app.tool()
async def synthesize(papers: list[dict]) -> dict:
    if not papers:
        return {"synthesis": "No papers provided."}
    combined_abstracts = "\n\n---\n\n".join([p.get("abstract", "") for p in papers if p.get("abstract")])
    prompt = (
        "Please provide a synthesis of the following research abstracts. "
        "Focus on the common themes, key findings, and any notable differences. "
        f"Abstracts: {combined_abstracts}"
    )
    try:
        synthesis = summarize_text(prompt, max_length=300, min_length=100)
        return {"synthesis": synthesis}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def cite(paper: dict) -> dict:
    authors = paper.get("authors", [])
    year = ""
    if paper.get("publication_date"):
        year = paper["publication_date"][:4]
    def format_author(name):
        parts = name.split()
        if not parts:
            return ""
        last = parts[-1]
        initials = " ".join([p[0] + "." for p in parts[:-1] if p])
        return f"{last}, {initials}" if initials else last
    author_str = ", ".join([format_author(a) for a in authors])
    citation = f"{author_str} ({year}). {paper.get('title', '')}. {paper.get('source', '')}."
    return {"citation": citation}

@app.tool()
async def qa(papers: list[dict], question: str) -> dict:
    if not papers:
        return {"answer": "No papers provided."}
    context = "\n\n---\n\n".join([p.get("abstract", "") for p in papers if p.get("abstract")])
    prompt = (
        f"Answer the following question based only on the provided research abstracts. "
        f"If the answer is not present, say so.\n"
        f"Question: {question}\n"
        f"Abstracts: {context}"
    )
    try:
        answer = summarize_text(prompt, max_length=200, min_length=50)
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}

async def main():
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main()) 