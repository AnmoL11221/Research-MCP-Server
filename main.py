from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from academic_search import search_arxiv, search_pubmed, search_semantic_scholar
from summarizer import summarize_text
import asyncio
from cache import get_from_cache, set_to_cache
from logger_config import logging
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="AI-Driven Research Assistant MCP Server",
    description="A prototype server for academic search and summarization."
)

class SearchQuery(BaseModel):
    query: str
    max_results: int = 5

class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 150

class SearchAndSummarizeRequest(BaseModel):
    query: str
    max_results: int = 5
    summary_max_length: int = 50
    summary_min_length: int = 25

class Paper(BaseModel):
    title: str
    authors: list[str]
    publication_date: str = ""
    source: str = ""
    abstract: str = ""
    url: str = ""

class SynthesizeRequest(BaseModel):
    papers: list[Paper]

class QARequest(BaseModel):
    papers: list[Paper]
    question: str

@app.get("/")
async def root():
    logging.info("Root endpoint called.")
    return {"message": "Research MCP Server is running."}

@app.post("/search")
async def search_endpoint(search_query: SearchQuery):
    logging.info(f"/search called with query='{search_query.query}', max_results={search_query.max_results}")
    cache_key = f"search:{search_query.query}:{search_query.max_results}"
    cached = get_from_cache(cache_key)
    if cached is not None:
        logging.info(f"Cache hit for key: {cache_key}")
        return cached
    logging.info(f"Cache miss for key: {cache_key}")
    results = []
    errors = []
    tasks = []
    loop = asyncio.get_event_loop()
    def run_sync(func, *args, **kwargs):
        return loop.run_in_executor(None, func, *args, **kwargs)
    tasks.append(run_sync(search_arxiv, search_query.query, search_query.max_results))
    tasks.append(run_sync(search_pubmed, search_query.query, search_query.max_results))
    tasks.append(search_semantic_scholar(search_query.query, search_query.max_results))
    results_list = await asyncio.gather(*tasks, return_exceptions=True)
    for idx, res in enumerate(results_list):
        if isinstance(res, Exception):
            if idx == 0:
                logging.warning(f"arXiv error: {res}")
                errors.append(f"arXiv: {str(res)}")
            elif idx == 1:
                logging.warning(f"PubMed error: {res}")
                errors.append(f"PubMed: {str(res)}")
            elif idx == 2:
                logging.warning(f"Semantic Scholar error: {res}")
                errors.append(f"Semantic Scholar: {str(res)}")
        else:
            results.extend(res)
    response = {"results": results, "errors": errors}
    set_to_cache(cache_key, response, 3600)
    return response

@app.post("/summarize")
async def summarize_endpoint(request: SummarizeRequest):
    logging.info("/summarize called.")
    try:
        summary = summarize_text(request.text, max_length=request.max_length)
        return {"summary": summary}
    except Exception as e:
        logging.error(f"Summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_and_summarize")
async def search_and_summarize_endpoint(request: SearchAndSummarizeRequest):
    logging.info(f"/search_and_summarize called with query='{request.query}', max_results={request.max_results}")
    try:
        results = []
        errors = []
        loop = asyncio.get_event_loop()
        def run_sync(func, *args, **kwargs):
            return loop.run_in_executor(None, func, *args, **kwargs)
        tasks = [
            run_sync(search_arxiv, request.query, request.max_results),
            run_sync(search_pubmed, request.query, request.max_results),
            search_semantic_scholar(request.query, request.max_results)
        ]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        for idx, res in enumerate(results_list):
            if isinstance(res, Exception):
                if idx == 0:
                    logging.warning(f"arXiv error: {res}")
                    errors.append(f"arXiv: {str(res)}")
                elif idx == 1:
                    logging.warning(f"PubMed error: {res}")
                    errors.append(f"PubMed: {str(res)}")
                elif idx == 2:
                    logging.warning(f"Semantic Scholar error: {res}")
                    errors.append(f"Semantic Scholar: {str(res)}")
            else:
                results.extend(res)
        summarized = []
        for entry in results:
            try:
                summary = summarize_text(
                    entry["abstract"],
                    max_length=request.summary_max_length,
                    min_length=request.summary_min_length
                )
            except Exception as e:
                logging.error(f"Summarization failed for paper '{entry['title']}': {e}")
                summary = f"Summarization failed: {e}"
            summarized.append({
                "source": entry["source"],
                "title": entry["title"],
                "original_abstract": entry["abstract"],
                "summary": summary
            })
        return {"results": summarized, "errors": errors}
    except Exception as e:
        logging.error(f"/search_and_summarize critical error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize")
async def synthesize_endpoint(request: SynthesizeRequest):
    logging.info(f"/synthesize called with {len(request.papers)} papers.")
    try:
        if not request.papers:
            return {"synthesis": "No papers provided."}
        combined_abstracts = "\n\n---\n\n".join([p.abstract for p in request.papers if p.abstract])
        prompt = (
            "Please provide a synthesis of the following research abstracts. "
            "Focus on the common themes, key findings, and any notable differences. "
            f"Abstracts: {combined_abstracts}"
        )
        synthesis = summarize_text(prompt, max_length=300, min_length=100)
        return {"synthesis": synthesis}
    except Exception as e:
        logging.error(f"/synthesize error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cite")
async def cite_endpoint(paper: Paper):
    logging.info(f"/cite called for paper: {paper.title}")
    # Simple APA formatting: Lastname, F. I., ... (Year). Title. Source.
    authors = paper.authors
    year = ""  # Try to extract year from publication_date
    if paper.publication_date:
        year = paper.publication_date[:4]
    def format_author(name):
        parts = name.split()
        if not parts:
            return ""
        last = parts[-1]
        initials = " ".join([p[0] + "." for p in parts[:-1] if p])
        return f"{last}, {initials}" if initials else last
    author_str = ", ".join([format_author(a) for a in authors])
    citation = f"{author_str} ({year}). {paper.title}. {paper.source}."
    # TODO: Use citeproc-py for more advanced citation formatting in the future.
    return {"citation": citation}

@app.post("/qa")
async def qa_endpoint(request: QARequest):
    logging.info(f"/qa called with question: {request.question}")
    try:
        if not request.papers:
            return {"answer": "No papers provided."}
        context = "\n\n---\n\n".join([p.abstract for p in request.papers if p.abstract])
        prompt = (
            f"Answer the following question based only on the provided research abstracts. "
            f"If the answer is not present, say so.\n"
            f"Question: {request.question}\n"
            f"Abstracts: {context}"
        )
        answer = summarize_text(prompt, max_length=200, min_length=50)
        return {"answer": answer}
    except Exception as e:
        logging.error(f"/qa error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 