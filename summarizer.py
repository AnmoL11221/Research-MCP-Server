from transformers import pipeline
import sys

_summarizer = None

def get_summarizer():
    global _summarizer
    if _summarizer is None:
        try:
            _summarizer = pipeline("summarization", model="t5-small")
        except Exception as e:
            print(f"Failed to load t5-small summarization model: {e}", file=sys.stderr)
            raise
    return _summarizer

def summarize_text(text: str, max_length: int, min_length: int = 30):
    summarizer = get_summarizer()
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]["summary_text"] 