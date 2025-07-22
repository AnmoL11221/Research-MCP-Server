import asyncio
import os
from fastmcp import FastMCP
from fastapi import FastAPI
from academic_search import search_arxiv, search_pubmed, search_semantic_scholar
from summarizer import summarize_text
from cache import get_from_cache, set_to_cache

mcp = FastMCP("research-assistant")
app = FastAPI(title="Research Assistant Server", version="1.0.0")

@mcp.tool()
async def search(query: str, max_results: int = 5) -> dict:
    try:
        cache_key = f"search:{query}:{max_results}"
        cached_result = get_from_cache(cache_key)
        if cached_result:
            return {"status": "success", "results": cached_result, "source": "cache"}

        tasks = [
            search_arxiv(query, max_results),
            search_pubmed(query, max_results),
            search_semantic_scholar(query, max_results)
        ]
        
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = []
        for results in results_list:
            if isinstance(results, list):
                all_results.extend(results)
        
        set_to_cache(cache_key, all_results)
        
        return {"status": "success", "results": all_results, "source": "live"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def summarize(text: str, max_length: int = 150) -> dict:
    try:
        summary = await summarize_text(text, max_length=max_length)
        return {"status": "success", "summary": summary}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def search_and_summarize(query: str, max_results: int = 5, summary_max_length: int = 50, summary_min_length: int = 25) -> dict:
    try:
        search_result = await search(query, max_results)
        if search_result["status"] != "success":
            return search_result
        
        papers = search_result["results"]
        
        summarized_papers = []
        for paper in papers:
            if "abstract" in paper and paper["abstract"]:
                summary_result = await summarize(paper["abstract"], summary_max_length)
                if summary_result["status"] == "success":
                    paper["summary"] = summary_result["summary"]
            summarized_papers.append(paper)
        
        return {"status": "success", "results": summarized_papers}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def synthesize(papers: list) -> dict:
    try:
        if not papers:
            return {"status": "error", "message": "No papers provided for synthesis"}
        
        combined_text = "\n\n".join([
            f"Paper: {paper.get('title', 'Unknown')}\nAbstract: {paper.get('abstract', 'No abstract available')}"
            for paper in papers[:5]
        ])
        
        synthesis = await summarize_text(combined_text, max_length=300)
        
        return {
            "status": "success",
            "synthesis": synthesis,
            "papers_count": len(papers)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def cite(paper: dict) -> dict:
    try:
        title = paper.get("title", "Unknown Title")
        authors = paper.get("authors", ["Unknown Author"])
        year = paper.get("year", "Unknown Year")
        source = paper.get("source", "Unknown Source")
        
        author_str = ", ".join(authors[:3])
        if len(authors) > 3:
            author_str += ", et al."
        
        citation = f"{author_str} ({year}). {title}. {source}."
        
        return {"status": "success", "citation": citation}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def qa(papers: list, question: str) -> dict:
    try:
        if not papers or not question:
            return {"status": "error", "message": "Papers and question are required"}
        
        context = "\n\n".join([
            f"Title: {paper.get('title', 'Unknown')}\nAbstract: {paper.get('abstract', 'No abstract')}"
            for paper in papers[:3]
        ])
        
        prompt = f"Question: {question}\n\nContext:\n{context}\n\nBased on the context above, provide a concise answer:"
        answer = await summarize_text(prompt, max_length=200)
        
        return {
            "status": "success",
            "question": question,
            "answer": answer,
            "papers_used": len(papers[:3])
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {
        "message": "Research Assistant Server",
        "status": "running",
        "mode": "dual (HTTP + MCP)",
        "endpoints": {
            "health": "/health",
            "search": "/api/search",
            "summarize": "/api/summarize",
            "search_and_summarize": "/api/search_and_summarize",
            "synthesize": "/api/synthesize",
            "cite": "/api/cite",
            "qa": "/api/qa"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "research-assistant"}

@app.post("/api/search")
async def api_search(request: dict):
    query = request.get("query", "")
    max_results = request.get("max_results", 5)
    return await search(query, max_results)

@app.post("/api/summarize")
async def api_summarize(request: dict):
    text = request.get("text", "")
    max_length = request.get("max_length", 150)
    return await summarize(text, max_length)

@app.post("/api/search_and_summarize")
async def api_search_and_summarize(request: dict):
    query = request.get("query", "")
    max_results = request.get("max_results", 5)
    summary_max_length = request.get("summary_max_length", 50)
    return await search_and_summarize(query, max_results, summary_max_length)

@app.post("/api/synthesize")
async def api_synthesize(request: dict):
    papers = request.get("papers", [])
    return await synthesize(papers)

@app.post("/api/cite")
async def api_cite(request: dict):
    paper = request.get("paper", {})
    return await cite(paper)

@app.post("/api/qa")
async def api_qa(request: dict):
    papers = request.get("papers", [])
    question = request.get("question", "")
    return await qa(papers, question)

if __name__ == "__main__":
    port = os.getenv("PORT")
    if port:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(port))
    else:
        mcp.run(transport="stdio")