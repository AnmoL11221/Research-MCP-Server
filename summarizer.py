from transformers import pipeline
import sys

summarizer = None

try:
    summarizer = pipeline("summarization", model="t5-small")
except Exception as e:
    print(f"Failed to load t5-small summarization model: {e}", file=sys.stderr)
    summarizer = None

def summarize_text(text: str, max_length: int, min_length: int = 30):
    if summarizer is None:
        raise Exception("No summarization model is available.")
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]["summary_text"] 