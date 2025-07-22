from transformers import pipeline
import sys
import asyncio

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

async def summarize_text(text: str, max_length: int = 150, min_length: int = 30):
    loop = asyncio.get_event_loop()
    
    def _summarize():
        summarizer = get_summarizer()
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]["summary_text"]
    
    return await loop.run_in_executor(None, _summarize) 