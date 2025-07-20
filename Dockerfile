FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ENV TRANSFORMERS_OFFLINE=1

CMD ["python", "mcp_server.py"]