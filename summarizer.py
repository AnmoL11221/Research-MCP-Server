from transformers import pipeline
import sys

summarizer = None

try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    print(f"Failed to load BART summarization model: {e}", file=sys.stderr)
    try:
        summarizer = pipeline("summarization", model="t5-base")
        print("Loaded fallback summarization model: t5-base", file=sys.stderr)
    except Exception as e2:
        summarizer = None
        print(f"Failed to load fallback summarization model: {e2}", file=sys.stderr)

def summarize_text(text: str, max_length: int, min_length: int = 30):
    if summarizer is None:
        raise Exception("No summarization model is available.")
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]["summary_text"] 