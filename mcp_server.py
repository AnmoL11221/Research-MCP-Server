from fastapi import FastAPI, Request
from academic_search import search_arxiv, search_pubmed, search_semantic_scholar
from summarizer import summarize_text
from cache import get_from_cache, set_to_cache
import asyncio

app = FastAPI()

@app.post("/search")
async def search_endpoint(request: Request):
    data = await request.json()
    query = data.get("query")
    max_results = data.get("max_results", 5)
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

@app.post("/summarize")
async def summarize_endpoint(request: Request):
    data = await request.json()
    text = data.get("text", "")
    max_length = data.get("max_length", 150)
    try:
        summary = summarize_text(text, max_length=max_length)
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}

@app.post("/search_and_summarize")
async def search_and_summarize_endpoint(request: Request):
    data = await request.json()
    query = data.get("query")
    max_results = data.get("max_results", 5)
    summary_max_length = data.get("summary_max_length", 50)
    summary_min_length = data.get("summary_min_length", 25)
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

@app.post("/synthesize")
async def synthesize_endpoint(request: Request):
    data = await request.json()
    papers = data.get("papers", [])
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

@app.post("/cite")
async def cite_endpoint(request: Request):
    paper = await request.json()
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

@app.post("/qa")
async def qa_endpoint(request: Request):
    data = await request.json()
    papers = data.get("papers", [])
    question = data.get("question", "")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 