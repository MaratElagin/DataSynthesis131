# DataSynthesis131

Synthetic tabular data generation and quality evaluation — as a **Python library** and a **local web platform**.

[![PyPI version](https://badge.fury.io/py/DataSynthesis131.svg)](https://badge.fury.io/py/DataSynthesis131)
[![Downloads](https://pepy.tech/badge/DataSynthesis131)](https://pepy.tech/project/DataSynthesis131)
[![Downloads](https://pepy.tech/badge/DataSynthesis131/month)](https://pepy.tech/project/DataSynthesis131)

Developed as part of the final qualification work at the [Institute of Technical Cybernetics and Informatics (ITIS, KAI)](https://kai.ru/structure/general/institutes/institute-of-technical-cybernetics-and-informatics/), Kazan Federal University (KFU).

## What's in this repository

| Component | Description | Documentation |
|-----------|-------------|---------------|
| **Library** (`DataSynthesis131/`) | PyPI package: auto-select SDV synthesizer, generate synthetic tables, evaluate fidelity | [DataSynthesis131/README.md](DataSynthesis131/README.md) |
| **Platform** (`platform/`) | FastAPI + web UI: upload data, run generation, download CSV, view metrics and plots | [platform/README.md](platform/README.md) · `/about` · [How to run](platform/docs/how-to-run.md) |

## Library — at a glance

- **Synthesizer** — picks among GC, CTGAN, CGAN, and TVAE (SDV) based on dataset characteristics
- **QualityEvaluator** — propensity score, log-cluster metric, prediction accuracy, SDV quality report, distribution plots
- Install: `pip install DataSynthesis131`

Full API, metrics, and model comparison: **[DataSynthesis131/README.md](DataSynthesis131/README.md)**

## Platform — at a glance

- Upload **CSV**, **Excel**, or a **Kaggle URL**
- Automatic or manual synthesizer selection, progress bar, quality report
- Run via **Docker** or **local venv**

Setup guide: **[platform/docs/how-to-run.md](platform/docs/how-to-run.md)**

Quick start (Docker):

```bash
cd platform
cp .env.docker.example .env   # optional: Kaggle credentials
docker compose up --build
```

Open http://localhost:8000

## Demo

- [Google Colab](https://colab.research.google.com/drive/1D66Nfn_miaiLtaa09fVR0Uu6_pDr6LCm?usp=sharing)
- [Video demo](https://youtu.be/6htWtSxMVWM)

## Contacts

Issues: [GitHub](https://github.com/MaratElagin/DataSynthesis131/issues) · Telegram: [@TBag2002](https://t.me/TBag2002)
