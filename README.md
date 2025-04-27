# Datasynthesis131. Overview
[![PyPI version](https://badge.fury.io/py/DataSynthesis131.svg)](https://badge.fury.io/py/DataSynthesis131)
[![Downloads](https://pepy.tech/badge/DataSynthesis131)](https://pepy.tech/project/DataSynthesis131)
[![Downloads](https://pepy.tech/badge/DataSynthesis131/month)](https://pepy.tech/project/DataSynthesis131)

Library to generate synthetic tabular data and evaluate quality of generated data.

The library was developed as part of the final qualification work at the ITIS Institute, Kazan Federal University.

### The main workflow of the library
![image](https://github.com/MaratElagin/DataSynthesis131/assets/78168429/7df94cc6-c702-4229-8ac8-a43b4bd909de)

### Library components
![image](https://github.com/MaratElagin/DataSynthesis131/assets/78168429/f51280cf-2a96-40ee-828d-8c08dea7e761)

### 🎲 **Synthesizer**
A class to generate synthetic tabular data. We use open-source [The Synthetic Data Vault](https://docs.sdv.dev/sdv) python library, which is considered top-tier for this purpose. It ensures high realism and statistical fidelity in the generated data and is scalable for large datasets. Additionally, SDV allows for table metadata configuration to specify the type and format of generated data. Its user-friendly APIs and comprehensive documentation make it easy to integrate and use
We compared 4 synthesizers of SDV on different types of datasets (see [Model comparison](https://www.notion.so/Datasynthesis131-documentation-59e40c1fac4e406d88f2674a59ea83c4?pvs=21) section):

- [Gaussian Copula Synthesizer (GC)](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer)
- [Conditional GAN Synthesizer (CTGAN)](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer)
- [Copula GAN Synthesizer (CGAN)](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer)
- [Table Variational Autoencoder (TVAE)](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer)

As a result, we have developed an algorithm for choosing the best generation method depending on the characteristics of the input dataset. This is the core of the synthesizer.

| ![image](https://github.com/MaratElagin/DataSynthesis131/assets/78168429/4150d04e-0438-4492-b037-29c297167147) |
|:--:| 
| *Algorithm to choose best generation method depending on dataset* |

Algorithm to choose best generation method depending on dataset

### 📐 **QualityEvaluator**

A class to evaluate the quality of synthetic data. It compares real and generated datasets and provides quality metrics, graphs.

### Metrics

In the modern context, the quality of synthetic data is evaluated based on three primary aspects:

1. Fidelity
2. Utility
3. Privacy

The quality of the generated data for different purposes hinges on these various aspects. Some applications require high fidelity, while others may prioritize utility or privacy. There is no universal metric for evaluating synthetic data. To keep our focus concise, we will adopt fidelity as the primary aspect for assessing the quality of the synthetic data.

We use 3 key metrics to evaluate the quality of the generated data:

- [Propensity score](https://www.mdpi.com/2227-7390/11/15/3278#:~:text=distribution%20%5B26%5D.-,The%20propensity%20score,-%5B27%5D%20evaluates) to determine the distinguishability between the real and generated synthetic data.

$$
pMSE\quad=\quad\frac{1}{N}\sum_{n}\left(\widehat{p}_{n}-0.5\right)^{2}
$$

- [Log-Cluster metric](https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-020-00977-1#:~:text=the%20dataset%20level.-,The%20log%2Dcluster%20metric,-%5B39%5D%20is) indicates how easily real and synthetic data can be clustered and, therefore, distinguished from each other.

$$
U_c(X_R, X_S) = \log\left( \frac{1}{G} \sum_{j=1}^G \left[ \frac{n_j^R}{n_j} - c \right]^2 \right), \quad c = \frac{n^R}{n^R + n^S}
$$

- Prediction accuracy is used to measure how well a machine learning model trained on synthetic data performs on classification tasks using real data. We classify using a Random Forest Classifier, which has proven to be an effective classifier for many complex classification problems.

Additionaly we use:

- [Quality Report](https://docs.sdv.dev/sdmetrics/reports/quality-report) from [SDMetrics](https://docs.sdv.dev/sdmetrics) to evaluate data fidelity.
- [Table evaluator](https://github.com/Baukebrenninkmeijer/table-evaluator/tree/master) by Baukebrenninkmeijer.

We chose the propensity score and log cluster metrics over other evaluated metrics, such as KL Divergence, because they are more intuitive to understand and use. These metrics can be easily utilized and interpreted by practitioners who may not be familiar with the complex mathematics and statistics behind synthetic data generation. Additionally, their straightforward implementation will encourage future researchers to expand upon this work.
We also selected prediction accuracy as an evaluation metric because it reflects how effectively machine learning models perform using the generated synthetic data.

### Models comparison

Based on the evaluation metrics, we compared generative methods for tabular data across different types of datasets. Datasets can be categorized 

**By their balance:**

- Balanced: Range [0.9 * 100/n; 1.1 * 100/n], where n **-** is the number of classes of the target variable.
- Weakly balanced: Range [0.6 * 100/n; 1.4 * 100/n], where n **-** is the number of classes of the target variable.
- Not balanced: Anything outside the above two ranges.
If the datasets do not have a target variable, we apply the K-Means clustering algorithm and analyze the distribution of clusters.

**By their data type:**

- Numerical: if numerical features amount more than 60%
- Categorical: if categorical features amount more than 60%
- Mixed: otherwise

**Other factors to consider:**

- Dimensionality: Number of features.
- Size: Number of rows.

**Datasets selection.**

To minimize systematic bias due to differences in datasets of the same type, careful attention was given to selecting datasets with similar characteristics. For all types, datasets were chosen with the same level of balance in terms of the output class.

In datasets with a large number of instances, smaller samples were selected while ensuring the preservation of the required characteristics.

For consistency, we generated synthetic datasets that match the size of the original datasets exactly.

No preprocessing operations on real data are performed before creating synthetic data. [Dankar and Ibrahim (2021)](https://www.mdpi.com/2076-3417/11/5/2158#:~:text=Does%20preprocessing%20real%20data%20prior%20to%20the%20generation%20of%20synthetic%20data%20improve%20the%20utility%20of%20the%20generated%20synthetic%20data%3F) noted that synthetic data with higher utility, that is, synthetic data with a higher propensity score, are generated when raw data are used for synthesis.

All results are in [google spreadsheet](https://docs.google.com/spreadsheets/d/1zOwbl4434EyLFWBd1YC-W45_H1f1AFZaTMWjnS6VhUY/edit?usp=sharing), example for numerical weakly balanced datasets:
![image](https://github.com/MaratElagin/DataSynthesis131/assets/78168429/c94370e9-8a21-4b82-8963-e5d549a20bc9)

## How to use?

### Installation

```python
!pip install -qqq DataSynthesis131
from DataSynthesis131 import QualityEvaluator, Synthesizer, GenerationParams
```

Please see documentation [here](https://github.com/MaratElagin/DataSynthesis131/blob/main/DataSynthesis131/README.md) to get more information and examples.

### Demo

[Google-colab](https://colab.research.google.com/drive/1D66Nfn_miaiLtaa09fVR0Uu6_pDr6LCm?usp=sharing) with a demonstration of the library's work.

[Live demo](https://youtu.be/6htWtSxMVWM)

### Contacts

If you notice any inaccuracies, please add issue [here](https://github.com/MaratElagin/DataSynthesis131/issues).

Also you can find me in the [Telegram](https://t.me/TBag2002).
