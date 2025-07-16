import requests
import feedparser
import httpx
import os
import xml.etree.ElementTree as ET

ARXIV_API_URL = "http://export.arxiv.org/api/query"
PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def search_arxiv(query: str, max_results: int):
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results
    }
    response = requests.get(ARXIV_API_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"arXiv API error: {response.status_code}")
    feed = feedparser.parse(response.text)
    results = []
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        authors = [author.get("name", "") for author in entry.get("authors", [])]
        publication_date = entry.get("published", "")
        abstract = entry.get("summary", "").strip()
        url = entry.get("link", "")
        results.append({
            "title": title,
            "authors": authors,
            "publication_date": publication_date,
            "source": "arXiv",
            "abstract": abstract,
            "url": url
        })
    return results

def search_pubmed(query: str, max_results: int):
    esearch_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json"
    }
    esearch_resp = requests.get(PUBMED_ESEARCH_URL, params=esearch_params)
    if esearch_resp.status_code != 200:
        raise Exception(f"PubMed esearch error: {esearch_resp.status_code}")
    id_list = esearch_resp.json().get("esearchresult", {}).get("idlist", [])
    if not id_list:
        return []
    efetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml"
    }
    efetch_resp = requests.get(PUBMED_EFETCH_URL, params=efetch_params)
    if efetch_resp.status_code != 200:
        raise Exception(f"PubMed efetch error: {efetch_resp.status_code}")
    root = ET.fromstring(efetch_resp.text)
    results = []
    for article in root.findall('.//PubmedArticle'):
        pmid_elem = article.find('.//PMID')
        pmid = pmid_elem.text if pmid_elem is not None else ""
        title_elem = article.find('.//ArticleTitle')
        title = title_elem.text if title_elem is not None else ""
        abstract_elem = article.find('.//Abstract/AbstractText')
        abstract = abstract_elem.text if abstract_elem is not None else ""
        authors = []
        for author in article.findall('.//AuthorList/Author'):
            last = author.find('LastName')
            fore = author.find('ForeName')
            if last is not None and fore is not None:
                authors.append(f"{fore.text} {last.text}")
            elif last is not None:
                authors.append(last.text)
        pub_date_elem = article.find('.//PubDate')
        year = pub_date_elem.find('Year').text if pub_date_elem is not None and pub_date_elem.find('Year') is not None else ""
        month = pub_date_elem.find('Month').text if pub_date_elem is not None and pub_date_elem.find('Month') is not None else ""
        day = pub_date_elem.find('Day').text if pub_date_elem is not None and pub_date_elem.find('Day') is not None else ""
        publication_date = "-".join(filter(None, [year, month, day]))
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
        results.append({
            "title": title,
            "authors": authors,
            "publication_date": publication_date,
            "source": "PubMed",
            "abstract": abstract,
            "url": url
        })
    return results

async def search_semantic_scholar(query: str, max_results: int):
    params = {
        "query": query,
        "fields": "title,authors,year,abstract,url",
        "limit": max_results
    }
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    async with httpx.AsyncClient() as client:
        response = await client.get(SEMANTIC_SCHOLAR_API_URL, params=params, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Semantic Scholar API error: {response.status_code}")
        data = response.json()
        results = []
        for paper in data.get("data", []):
            title = paper.get("title", "")
            authors = [a.get("name", "") for a in paper.get("authors", [])]
            publication_date = str(paper.get("year", ""))
            abstract = paper.get("abstract", "")
            url = paper.get("url", "")
            results.append({
                "title": title,
                "authors": authors,
                "publication_date": publication_date,
                "source": "Semantic Scholar",
                "abstract": abstract,
                "url": url
            })
        return results

def get_paper_details_semantic_scholar(paper_id: str, fields: str = 'title,authors,abstract'):
    import os
    import requests
    base_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
    params = {"fields": fields}
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Semantic Scholar paper details error: {response.status_code}")
    data = response.json()
    title = data.get("title", "")
    authors = [a.get("name", "") for a in data.get("authors", [])]
    abstract = data.get("abstract", "")
    url = data.get("url", f"https://www.semanticscholar.org/paper/{paper_id}")
    return {
        "title": title,
        "authors": authors,
        "publication_date": "",
        "source": "Semantic Scholar",
        "abstract": abstract,
        "url": url
    } 