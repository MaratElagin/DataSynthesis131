# DataSynthesis131 — Library

[![PyPI version](https://badge.fury.io/py/DataSynthesis131.svg)](https://badge.fury.io/py/DataSynthesis131)
[![Downloads](https://pepy.tech/badge/DataSynthesis131)](https://pepy.tech/project/DataSynthesis131)
[![Downloads](https://pepy.tech/badge/DataSynthesis131/month)](https://pepy.tech/project/DataSynthesis131)

Python library to generate synthetic tabular data and evaluate the quality of generated data.

Developed as part of the final qualification work at the [Institute of Technical Cybernetics and Informatics (ITIS, KAI)](https://kai.ru/structure/general/institutes/institute-of-technical-cybernetics-and-informatics/), Kazan Federal University (KFU).

## Overview

### Main workflow

![Main workflow](https://github.com/MaratElagin/DataSynthesis131/assets/78168429/7df94cc6-c702-4229-8ac8-a43b4bd909de)

### Library components

![Library components](https://github.com/MaratElagin/DataSynthesis131/assets/78168429/f51280cf-2a96-40ee-828d-8c08dea7e761)

## Installation

```bash
pip install DataSynthesis131
```

```python
from DataSynthesis131 import QualityEvaluator, Synthesizer, GenerationParams
```

## Quick start

```python
import pandas as pd
from DataSynthesis131 import Synthesizer, GenerationParams, QualityEvaluator

data = pd.read_csv("data.csv")

gen_params = GenerationParams(num_rows=1000)
synthesizer = Synthesizer.create(data, gen_params)
data_generated = synthesizer.generate()

quality_evaluator = QualityEvaluator(
    data, data_generated, synthesizer.metadata, gen_params
)
report = quality_evaluator.evaluate()
```

---

# 🎲 Synthesizer

A class to generate synthetic tabular data.

You configure the generation settings, edit the dataset metadata if needed, and then generate synthetic data. The synthesizer uses four models for generating tabular data: TVAE, CGAN, CTGAN, and GC.

The library is built on [The Synthetic Data Vault (SDV)](https://docs.sdv.dev/sdv). We compared four SDV synthesizers on different types of datasets (see [Model comparison](#models-comparison)):

- [Gaussian Copula Synthesizer (GC)](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer)
- [Conditional GAN Synthesizer (CTGAN)](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer)
- [Copula GAN Synthesizer (CGAN)](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer)
- [Table Variational Autoencoder (TVAE)](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer)

The core of the synthesizer is an algorithm that chooses the best generation method depending on dataset characteristics:

| ![Algorithm to choose best generation method](https://github.com/MaratElagin/DataSynthesis131/assets/78168429/4150d04e-0438-4492-b037-29c297167147) |
|:--:|
| *Algorithm to choose best generation method depending on dataset* |

## ⚙️ GenerationParams

`GenerationParams` configures generation settings:

- `num_rows` — number of rows to generate
- `fast_result` — prioritize speed (default: `False`)
- `target_variable` — target column; if omitted, the dataset is clustered and cluster labels are used
- `with_missing_values` — keep missing values (default: `True`)
- `epochs` — training epochs (default: `1000`)

```python
gen_params = GenerationParams(
    num_rows=1000,
    fast_result=False,
    target_variable=None,
    with_missing_values=True,
    epochs=1000,
)
```

## Dataset metadata

`SingleTableMetadata` from SDV describes your table (column types, keys, ranges, formats). Metadata is auto-detected when you create the synthesizer. See [SDV metadata docs](https://docs.sdv.dev/sdv/single-table-data/data-preparation/single-table-metadata-api).

**Creating a synthesizer:**

```python
synthesizer = Synthesizer.create(data, gen_params)
```

| <img width="259" alt="Example of metadata" src="https://github.com/MaratElagin/DataSynthesis131/assets/78168429/167ef16c-bdfe-49f4-9de0-e7b90fcf312a"> |
|:--:|
| *Example of metadata* |

Use `synthesizer.visualize_metadata()` for a detailed view after creation.

**Generating data:**

```python
data_generated = synthesizer.ctgan_generate()           # CTGAN
data_generated = synthesizer.gaussian_copula_generate()   # GC
data_generated = synthesizer.copula_gan_generate()        # CGAN
data_generated = synthesizer.tvae_generate()              # TVAE
data_generated = synthesizer.generate()                   # auto-select best method
```

---

# 📐 QualityEvaluator

Compares real and generated datasets and returns quality metrics and plots.

**Creating a quality evaluator:**

```python
quality_evaluator = QualityEvaluator(
    data,
    data_generated,
    synthesizer.metadata,
    gen_params,
)
```

**Evaluation:**

```python
quality_evaluator.evaluate(with_details=False)
```

With `with_details=True`, the report includes TableEvaluator output.

Returns Propensity Score, Log-Cluster Metric, Prediction Accuracy, Data Validity, SDV Score, and distribution plots (best / middle / worst matching columns).

```python
quality_evaluator.print_column_plot(column_name)
quality_evaluator.evaluate_metrics()  # (propensity_score, log_cluster_metric, prediction_accuracy)
```

**Examples:**

| ![Best matching distributions](https://github.com/MaratElagin/DataSynthesis131/assets/78168429/6244cd31-ce2c-4f52-be93-e4a1f47bbdd7) |
|:--:|
| *Best matching distributions for the `MinorAxisLength` column* |

| <img width="463" alt="Table evaluator report" src="https://github.com/MaratElagin/DataSynthesis131/assets/78168429/cbde5f54-748d-4f8d-b545-1cc08f61750e"> |
|:--:|
| *Table evaluator report* |

| ![Table evaluator visualization](https://github.com/MaratElagin/DataSynthesis131/assets/78168429/200317ed-6693-46d9-a708-1c071a15ca4c) |
|:--:|
| *Table evaluator visualization* |

---

## Metrics

Synthetic data quality is often assessed along three axes: **fidelity**, **utility**, and **privacy**. This library focuses on **fidelity** as the primary evaluation aspect.

Three key metrics:

- **[Propensity score](https://www.mdpi.com/2227-7390/11/15/3278)** — distinguishability between real and synthetic data:

$$
pMSE = \frac{1}{N}\sum_{n}\left(\widehat{p}_{n}-0.5\right)^{2}
$$

- **[Log-Cluster metric](https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-020-00977-1)** — how easily real and synthetic rows cluster apart:

$$
U_c(X_R, X_S) = \log\left( \frac{1}{G} \sum_{j=1}^G \left[ \frac{n_j^R}{n_j} - c \right]^2 \right), \quad c = \frac{n^R}{n^R + n^S}
$$

- **Prediction accuracy** — Random Forest trained on synthetic data, evaluated on real labels.

Additionally:

- [Quality Report](https://docs.sdv.dev/sdmetrics/reports/quality-report) from [SDMetrics](https://docs.sdv.dev/sdmetrics)
- [Table evaluator](https://github.com/Baukebrenninkmeijer/table-evaluator)

## Models comparison

Datasets are categorized **by balance** (balanced / weakly balanced / not balanced), **by data type** (numerical / categorical / mixed), and by dimensionality and size.

No preprocessing is applied before synthesis — [Dankar and Ibrahim (2021)](https://www.mdpi.com/2076-3417/11/5/2158) show that raw data often yields higher-utility synthetic data.

All comparison results: [Google Spreadsheet](https://docs.google.com/spreadsheets/d/1zOwbl4434EyLFWBd1YC-W45_H1f1AFZaTMWjnS6VhUY/edit?usp=sharing).

![Example for numerical weakly balanced datasets](https://github.com/MaratElagin/DataSynthesis131/assets/78168429/c94370e9-8a21-4b82-8963-e5d549a20bc9)

## Demo

- [Google Colab](https://colab.research.google.com/drive/1D66Nfn_miaiLtaa09fVR0Uu6_pDr6LCm?usp=sharing)
- [Video demo](https://youtu.be/6htWtSxMVWM)

## Web platform

A local web UI wraps this library — upload CSV/Excel/Kaggle datasets, run generation, view metrics and plots.

See [platform/README.md](../platform/README.md) and [platform/docs/how-to-run.md](../platform/docs/how-to-run.md).

## Contacts

Issues: [GitHub](https://github.com/MaratElagin/DataSynthesis131/issues) · Telegram: [@TBag2002](https://t.me/TBag2002)
