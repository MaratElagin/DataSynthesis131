# Build from repository root:
#   docker compose -f platform/docker-compose.yml up --build

FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY DataSynthesis131 ./DataSynthesis131
COPY platform/requirements.txt ./platform/requirements.txt

# CPU-only PyTorch first — avoids ~800MB CUDA/cuDNN wheels inside the container
RUN pip install --upgrade pip hatchling \
    && pip install "numpy==1.26.4" "pandas==2.0.3" \
    && pip install torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install -e ".[web]" \
    && pip install -r platform/requirements.txt

COPY platform ./platform

WORKDIR /app/platform

RUN mkdir -p data/tmp

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
