from enum import Enum

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