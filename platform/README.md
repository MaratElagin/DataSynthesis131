# DataSynthesis131 Platform

Web UI for synthetic tabular data generation, built on the [DataSynthesis131 library](../DataSynthesis131/README.md).

## Features

- Upload **CSV**, **Excel**, or **Kaggle URL**
- Automatic SDV synthesizer selection (or manual method)
- Training progress bar
- Download synthetic CSV
- Quality report: metrics + distribution and correlation plots

## Quick start

**Docker (recommended):**

```bash
cd platform
cp .env.docker.example .env   # optional: Kaggle API
docker compose up --build
```

Open http://localhost:8000 (about: http://localhost:8000/about)

UI/backend on the host are bind-mounted into the container — after code changes, `docker compose up -d` and hard-refresh the browser. Rebuild the image only when dependencies change. See [docs/how-to-run.md](docs/how-to-run.md).

**Local venv:**

```bash
bash platform/scripts/dev.sh
```

Full setup, Kaggle credentials, and troubleshooting: **[docs/how-to-run.md](docs/how-to-run.md)**

## API

OpenAPI docs: http://localhost:8000/docs

Example flow (upload → generate → download) is in [docs/how-to-run.md](docs/how-to-run.md#api-quick-reference).

## Structure

```
platform/
  app/                 # FastAPI backend
  static/              # HTML, CSS, JS
  docs/                # how-to-run and other guides
  scripts/dev.sh       # local launch via venv
  data/tmp/            # job artifacts (Docker volume)
  .env.example         # env template (local)
  .env.docker.example  # env template (Docker Compose)
  Dockerfile
  docker-compose.yml
  requirements.txt
```

## Demo script (screencast)

1. `docker compose up --build` in `platform/`
2. Small CSV (100–500 rows, 5–10 columns)
3. Enable **«Быстрый результат»** or **Gaussian Copula**
4. Show preview, progress, metrics, plots
5. Download `synthetic.csv`
