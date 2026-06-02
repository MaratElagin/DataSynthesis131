# How to run the platform

Two ways to start the web UI: **Docker** (recommended) or **local Python venv**.

## Prerequisites

- **Docker:** Docker Engine + Docker Compose v2
- **Local:** Python 3.11+ (3.8+ may work for the library; the platform is tested on 3.11)

## Kaggle credentials (optional)

Needed only if you use **Kaggle URL** upload in the UI.

1. Log in at [kaggle.com](https://www.kaggle.com)
2. **Account → Settings → API → Create New Token** — downloads `kaggle.json`
3. Copy `username` and `key` into your env file

Docs: [Kaggle API credentials](https://github.com/Kaggle/kaggle-api#api-credentials)

| Scenario | Env file template | Copy command |
|----------|-------------------|--------------|
| Docker | [`.env.docker.example`](../.env.docker.example) | `cp .env.docker.example .env` |
| Local | [`.env.example`](../.env.example) | `cp .env.example .env` |

Edit `.env` and set:

```env
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

Alternative for local dev: place `kaggle.json` in `~/.kaggle/kaggle.json` (chmod 600).

---

## Docker (recommended)

From the `platform/` directory:

```bash
cd platform
cp .env.docker.example .env   # optional, for Kaggle
docker compose up --build
```

Open http://localhost:8000

### Обновления кода (UI / backend)

`docker-compose.yml` монтирует с хоста папки `static/`, `app/` и `DataSynthesis131/` — **пересборка образа для правок UI не нужна**.

После `git pull` или локальных изменений:

```bash
cd platform
docker compose up -d    # пересоздать контейнер с новыми volume/mount
# или один раз после смены compose-файла:
docker compose down && docker compose up --build -d
```

В браузере: жёсткое обновление (**Cmd+Shift+R** / **Ctrl+Shift+R**).

Полная пересборка образа (`docker compose up --build`) нужна только если менялись **зависимости** (`requirements.txt`, `pyproject.toml`, `Dockerfile`).

**First build takes 5–15 minutes** — pip downloads SDV and CPU PyTorch (~500 MB). Later rebuilds use Docker cache.

If the build seems stuck on `Downloading torch` / `nvidia_cudnn`, cancel (`Ctrl+C`) and rebuild: the Dockerfile uses CPU-only PyTorch without CUDA.

**Stop:**

```bash
docker compose down
```

**Rebuild after code changes:**

```bash
docker compose up --build
```

---

## Local (without Docker)

Recommended: isolated **venv** to avoid numpy/pandas conflicts with system Python.

From the **repository root**:

```bash
bash platform/scripts/dev.sh
```

The script creates `.venv`, installs dependencies, loads `platform/.env` if present, and starts uvicorn on port 8000.

### Manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r platform/requirements.txt
pip install -e ".[web]"

cp platform/.env.example platform/.env   # optional, for Kaggle

cd platform
uvicorn app.main:app --reload --port 8000
```

If you see `numpy.dtype size changed`, reinstall in a fresh venv:

```bash
pip install --force-reinstall -r platform/requirements.txt
pip install -e ".[web]"
```

---

## Verify

- UI: http://localhost:8000
- OpenAPI: http://localhost:8000/docs

Upload a small CSV (100–500 rows), enable **«Быстрый результат»** or **Gaussian Copula** for a quick demo run.

## API quick reference

```bash
# Upload CSV
curl -F "file=@data.csv" http://localhost:8000/api/upload

# Start generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"job_id": "<JOB_ID>", "num_rows": 100, "fast_result": true}'

# Job status
curl http://localhost:8000/api/jobs/<JOB_ID>

# Download synthetic CSV
curl -O http://localhost:8000/api/jobs/<JOB_ID>/download

# Quality report
curl http://localhost:8000/api/jobs/<JOB_ID>/report
```

Kaggle upload:

```bash
curl -X POST http://localhost:8000/api/upload/kaggle \
  -H "Content-Type: application/json" \
  -d '{"kaggle_url": "https://www.kaggle.com/datasets/owner/dataset", "file_name": "train.csv"}'
```

More details: [platform/README.md](../README.md)
