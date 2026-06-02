from enum import Enum

import pandas as pd
from sklearn.impute import SimpleImputer


def _assign_imputed_columns(df: pd.DataFrame, columns: list, values) -> None:
    """Assign imputer output without pandas single-column assignment bug."""
    if not columns:
        return
    if len(columns) == 1:
        df[columns[0]] = values.ravel()
    else:
        df[columns] = values


def impute_missing_values(df: pd.DataFrame) -> None:
    """Fill NaNs in-place (numeric → mean, categorical → mode)."""
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = df.select_dtypes(
        include=["object", "category", "string"]
    ).columns.tolist()

    if numeric_columns and df[numeric_columns].isna().any().any():
        imputer = SimpleImputer(strategy="mean")
        _assign_imputed_columns(
            df, numeric_columns, imputer.fit_transform(df[numeric_columns])
        )

    if categorical_columns and df[categorical_columns].isna().any().any():
        imputer = SimpleImputer(strategy="most_frequent")
        _assign_imputed_columns(
            df, categorical_columns, imputer.fit_transform(df[categorical_columns])
        )


class DatasetType(Enum):
    NUMERICAL = "Numerical"
    CATEGORICAL = "Categorical"
    MIXED = "Mixed"

class BalancedType(Enum):
    BALANCED = "Balanced"
    WEAKLY_BALANCED = "Weakly Balanced"
    NOT_BALANCED = "Not Balanced"

class GenerationMethod(Enum):
    CONDITIONAL_GAN = "Conditional GAN"
    GAUSSIAN_COPULA = "Gaussian Copula"
    COPULA_GAN = "Copula GAN"
    TVAE = "Tabular VAE"

class GenerationParams:
    def __init__(self, num_rows, fast_result=False, target_variable=None, with_missing_values=True, epochs=1000):
        self.num_rows = num_rows
        self.fast_result=fast_result
        self.target_variable = target_variable
        self.with_missing_values = with_missing_values
        self.epochs = epochs