import streamlit as st
import requests
import json

st.set_page_config(page_title="AI Research Assistant", layout="wide")

if "search_results" not in st.session_state:
    st.session_state.search_results = []

st.title("🤖 AI Research Assistant")

backend_url = st.text_input(
    "Backend API URL",
    value="https://your-backend-url.vercel.app",
    help="Enter the URL of your deployed backend API."
)

with st.form(key='search_form'):
    query = st.text_input("Enter your research query")
    search_submitted = st.form_submit_button("Search")

if search_submitted and query and backend_url:
    with st.spinner("Searching academic sources..."):
        try:
            response = requests.post(
                f"{backend_url.rstrip('/')}/search",
                json={"query": query, "max_results": 10},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            st.session_state.search_results = data.get("results", [])
            # Remove backend warning display for errors
            # errors = data.get("errors", [])
            # if errors:
            #     for err in errors:
            #         st.warning(f"Backend warning: {err}")
        except Exception as e:
            st.error(f"Search failed: {e}")

if st.session_state.search_results:
    st.subheader("Search Results")
    for idx, paper in enumerate(st.session_state.search_results):
        with st.expander(paper.get("title", f"Paper {idx+1}")):
            st.markdown(f"**Authors:** {', '.join(paper.get('authors', []))}")
            st.markdown(f"**Publication Date:** {paper.get('publication_date', 'N/A')}")
            st.markdown(f"**Source:** {paper.get('source', 'N/A')}")
            st.markdown(f"**URL:** [{paper.get('url', 'N/A')}]({paper.get('url', '#')})")
            st.markdown(f"**Abstract:**\n{paper.get('abstract', 'No abstract available.')}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Cite {idx}", key=f"cite_{idx}"):
                    try:
                        cite_resp = requests.post(
                            f"{backend_url.rstrip('/')}/cite",
                            json=paper,
                            timeout=15
                        )
                        cite_resp.raise_for_status()
                        citation = cite_resp.json().get("citation", "No citation returned.")
                        st.success(citation)
                    except Exception as e:
                        st.error(f"Citation failed: {e}")
            with col2:
                if st.button(f"Summarize {idx}", key=f"summarize_{idx}"):
                    try:
                        sum_resp = requests.post(
                            f"{backend_url.rstrip('/')}/summarize",
                            json={"text": paper.get("abstract", ""), "max_length": 100},
                            timeout=30
                        )
                        sum_resp.raise_for_status()
                        summary = sum_resp.json().get("summary", "No summary returned.")
                        st.info(summary)
                    except Exception as e:
                        st.error(f"Summarization failed: {e}")

if st.session_state.search_results:
    st.subheader("Ask a Question About These Results")
    with st.form(key='qa_form'):
        user_question = st.text_area(
            "e.g., What was the primary limitation mentioned in these studies?",
            height=80
        )
        qa_submitted = st.form_submit_button("Get Answer")
    if qa_submitted and user_question:
        with st.spinner("Getting answer from AI..."):
            try:
                qa_payload = {
                    "papers": st.session_state.search_results,
                    "question": user_question
                }
                qa_resp = requests.post(
                    f"{backend_url.rstrip('/')}/qa",
                    json=qa_payload,
                    timeout=60
                )
                qa_resp.raise_for_status()
                answer = qa_resp.json().get("answer", "No answer returned.")
                st.markdown(f"> **AI Answer:** {answer}")
            except Exception as e:
                st.error(f"Q&A failed: {e}") 