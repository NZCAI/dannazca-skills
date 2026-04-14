FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir "edgartools[ai]"

RUN addgroup --system edgar && \
    adduser --system --ingroup edgar --home /home/edgar edgar

USER edgar

EXPOSE 8765

CMD ["edgartools-mcp", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8765"]
