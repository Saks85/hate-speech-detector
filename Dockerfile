FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Keep system deps minimal to reduce final image size.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.deploy.txt ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.deploy.txt \
    && python -m spacy download en_core_web_sm \
    && python -c "import nltk; nltk.download('stopwords')"

# Copy only backend-relevant source; frontend/data/models are excluded via .dockerignore.
COPY . .

CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker -w 1 -b 0.0.0.0:${PORT:-8000} api.main:app"]
