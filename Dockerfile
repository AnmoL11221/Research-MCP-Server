FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -c "from transformers import pipeline; pipeline('summarization', model='t5-small')"

ENV TRANSFORMERS_OFFLINE=1

EXPOSE 8080

CMD ["python", "mcp_server.py"]