# Use an official Python base image
FROM python:3.10-slim

WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies (with pip cache and pre-built wheels)
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -c "from transformers import pipeline; pipeline('summarization', model='t5-small')"

ENV TRANSFORMERS_OFFLINE=1

CMD ["python", "mcp_server.py"]