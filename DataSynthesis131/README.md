# 🎲  Synthesizer

A class to generate sythetic tabular data.

You configure the generation settings, edit the dataset metadata if needed, and then generate synthetic data. The synthesizer uses four models for generating tabular data: TVAE, CGAN, CTGAN, and GC.

### ⚙️ GenerationParams

There is GenerationParams class, it allows configure the generation settings, such as:

- The number of rows to generate (`num_rows`);
- Whether to prioritize fast results (`fast_result`); False by default.
- Specify the target variable (`target_variable`); If you do not provide a target variable, your dataset will be clustered, and the *cluster* labels will be used as the `target_variable`.
- Include missing values if needed (`with_missing_values`); True by default. If you want to remove NaNs or empty values from your dataset, you can disable it.
- Set the number of training epochs (`epochs`); 1000 by default. This default is optimal for most cases. You can decrease the number of epochs to speed up the process, but this may reduce the quality of the generated data. Conversely, increasing the number of epochs can improve data quality slightly, but it will also increase the training time.

**Creating a gen_params:**

```python
gen_params = GenerationParams(
	num_rows=1000,
	fast_result=False,
	target_variable=None,
	with_missing_values=True
	epochs=1000)
```

### Dataset metadata

The `SingleTableMetadata` from SDV is an object that describes your table. Using metadata, you can set various parameters for generation, such as column types, primary keys, data ranges and formats, and regular expressions. SDV provides good [documentation](https://docs.sdv.dev/sdv/single-table-data/data-preparation/single-table-metadata-api) for it.

Fortunately, metadata is automatically determined based on the dataset when you create the synthesizer.

**Creating a synthesizer:**

```python
synthesizer = Synthesizer.create(
	data, # pandas dataframe
	gen_params # generation parameters
)
```

This will return the metadata for your dataset. You can edit the metadata if needed (see [documentation](https://docs.sdv.dev/sdv/single-table-data/data-preparation/single-table-metadata-api#update-api))

| <img width="259" alt="image" src="https://github.com/MaratElagin/DataSynthesis131/assets/78168429/167ef16c-bdfe-49f4-9de0-e7b90fcf312a"> |
|:--:| 
| *Example of metadata* |

Additionally, you can use the `synthesizer.visualize_metadata()` method to get detailed information about your metadata after the synthesizer has been created.

When everything ready you can generate data! You can select a specific generation algorithm.

```python
data_generated = synthesizer.ctgan_generate() # CTGAN
data_generated = synthesizer.gaussian_copula_generate() # GC
data_generated = synthesizer.copula_gan_generate() # CGAN
data_generated = synthesizer.tvae_generate() # TVAE
```

If you prefer an automatic selection of the most suitable algorithm for your dataset, use the `generate()` method:

```python
data_generated = synthesizer.generate() # automatically choose the best generation algorithm
```

It will automatically select the most suitable generation algorithm for your dataset, following the algorithm presented in the diagram.

# 📐 QualityEvaluator

A class to evaluate the quality of synthetic data. It compares real and generated datasets and provides quality metrics, graphs. The quality evaluator is based on the metrics described here.

**Creating a quality_evaluator:**

```python
quality_evaluator = QualityEvaluator(
	data, # real data
	data_generated, # generated
	synthesizer.metadata, # metadata
	gen_params # generation parameters
)
```

**Generated data evaluation:**

```python
quality_evaluator.evaluate(with_details=False)
```

The `with_details` parameter is `False` by default. If set to `True`, the evaluation report will include the TableEvaluator.

The evaluation report returns various metrics such as Propensity Score, Log-Cluster Metric, Prediction Accuracy, Data Validity, and SDV Score. It also includes three plots showing the distribution by column in real and synthetic data:

1. The best matching distributions

2. The middle matching distributions

3. The worst matching distributions

- If you want to print distribution plot for specific column, you should use `print_column_plot`

```python
quality_evaluator.print_column_plot(column_name)
```

- If you want get only metrics as Propensity Score, Log-Cluster Metric, Prediction Accuracy, you should use `evaluate_metrics`. It return tuple `(propensity_score, log_cluster_metric, prediction_accuracy)`

```python
quality_evaluator.evaluate_metrics()
```

**Examples:**

| ![The best matching distributions between real and synthetic data for the `MinorAxisLength` column.](https://github.com/MaratElagin/DataSynthesis131/assets/78168429/6244cd31-ce2c-4f52-be93-e4a1f47bbdd7) |
|:--:| 
| *The best matching distributions between real and synthetic data for the `MinorAxisLength` column.* |

The best matching distributions between real and synthetic data for the `MinorAxisLength` column.


| <img width="463" alt="image" src="https://github.com/MaratElagin/DataSynthesis131/assets/78168429/cbde5f54-748d-4f8d-b545-1cc08f61750e"> |
|:--:| 
| *Table evaluator report* |


| ![Table evaluator visualization](https://github.com/MaratElagin/DataSynthesis131/assets/78168429/200317ed-6693-46d9-a708-1c071a15ca4c) |
|:--:| 
| *Table evaluator visualization* |
