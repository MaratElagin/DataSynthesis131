from ..common import DatasetType, BalancedType, GenerationMethod
from sdv.metadata import SingleTableMetadata
from sdv.single_table import CTGANSynthesizer, GaussianCopulaSynthesizer, CopulaGANSynthesizer, TVAESynthesizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import logging

from ..common.common import impute_missing_values

class Synthesizer:
    def __init__(self, data, generation_params):
        self._metadata_obj = SingleTableMetadata()
        self._metadata_obj.detect_from_dataframe(data)
        self.data = data
        self.generation_params = generation_params
        self.num_rows = generation_params.num_rows
        self.epochs = generation_params.epochs
        self.target_variable = generation_params.target_variable
        self._prepare_dataset()
    
    def _log_info(self, message):
        current_logging_level = logging.getLogger().getEffectiveLevel()
        logging.getLogger().setLevel(logging.INFO)
        logging.info(message)
        logging.getLogger().setLevel(current_logging_level)
    
    def _prepare_dataset(self):
        if (self.generation_params.target_variable is None):
            self._log_info("You did not specify the name of the target variable (target_variable), so the dataset will be clustered and the target_variable will be - \"cluster\".")
            self._add_cluster_label()
            self.target_variable="cluster"
            self.metadata.add_column(
                column_name='cluster',
                sdtype='categorical')
        if (not self.generation_params.with_missing_values):
            self._impute_missing_values(self.data)

    def _impute_missing_values(self, data):
        impute_missing_values(data)
    
    def _find_optimal_number_of_clusters(self, data, max_clusters=20):
        wcss = []
        for n in range(1, max_clusters):
            kmeans = KMeans(n_clusters=n, init='k-means++', max_iter=300, n_init=10, random_state=0)
            kmeans.fit(data)
            wcss.append(kmeans.inertia_)
        
        distances = []
        for i in range(1, len(wcss)-1):
            d1 = (wcss[i+1] - wcss[i]) / (i+2 - (i+1))
            d2 = (wcss[i] - wcss[i-1]) / ((i+1) - i)
            d2d1 = d1 - d2
            distances.append(d2d1)
        
        return distances.index(max(distances)) + 2

    def _add_cluster_label(self):
        if "cluster" in self.data.columns:
            return

        data_copy = self.data.copy()
        
        self._impute_missing_values(data_copy)

        numeric_features = data_copy.select_dtypes(include=['int64', 'float64']).columns
        categorical_features = data_copy.select_dtypes(include=['object', 'category']).columns

        numeric_transformer = Pipeline(steps=[('scaler', StandardScaler())])
        categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore'))])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)])

        data_preprocessed = preprocessor.fit_transform(data_copy)

        n_clusters = self._find_optimal_number_of_clusters(data_preprocessed)

        kmeans = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=300, n_init=10, random_state=0)
        cluster_labels = kmeans.fit_predict(data_preprocessed)

        self.data['cluster'] = cluster_labels

    def _determine_dataset_type(self):
        numerical_cols = self.metadata.get_column_names(sdtype='numerical')
        categorical_cols = self.metadata.get_column_names(sdtype='categorical')
        num_total_cols = len(numerical_cols) + len(categorical_cols)
        if len(numerical_cols) / num_total_cols > 0.6:
            return DatasetType.NUMERICAL
        elif len(categorical_cols) / num_total_cols > 0.6:
            return DatasetType.CATEGORICAL
        else:
            return DatasetType.MIXED

    def _determine_target_variable_balance(self):
        class_distribution = self.data[self.target_variable].value_counts(normalize=True)
        n_classes = len(class_distribution)

        max_percentage = class_distribution.max() * 100

        balanced_percentage = 100 / n_classes

        if max_percentage <= 1.1 * balanced_percentage:
            return BalancedType.BALANCED
        elif max_percentage <= 1.4 * balanced_percentage:
            return BalancedType.WEAKLY_BALANCED
        else:
            return BalancedType.NOT_BALANCED
        
    def _determine_generation_method(self, dataset_type, dataset_balanced_type):
        if (self.generation_params.fast_result or self.data.shape[1] > 99):
            return GenerationMethod.GAUSSIAN_COPULA
        elif (self.data.shape[0] < 101):
            return GenerationMethod.COPULA_GAN
        elif (dataset_balanced_type is BalancedType.BALANCED):
            if (dataset_type is DatasetType.NUMERICAL or dataset_type is DatasetType.MIXED):
                return GenerationMethod.TVAE
            return GenerationMethod.CONDITIONAL_GAN
        elif (dataset_balanced_type is BalancedType.WEAKLY_BALANCED):
            if (dataset_type is DatasetType.NUMERICAL or dataset_type is DatasetType.MIXED):
                return GenerationMethod.TVAE
            return GenerationMethod.COPULA_GAN
        elif (dataset_balanced_type is BalancedType.NOT_BALANCED):
            if (dataset_type is DatasetType.NUMERICAL or dataset_type is DatasetType.CATEGORICAL):
                return GenerationMethod.GAUSSIAN_COPULA
            return GenerationMethod.TVAE

    def visualize_metadata(self):
        try:
            from IPython.display import display
        except ImportError:
            return

        visualization = self.metadata.visualize()
        if visualization is not None:
            display(visualization)

        summarized_visualization = self.metadata.visualize("summarized")
        if summarized_visualization is not None:
            display(summarized_visualization)

    def analyze(self):
        """Return dataset characteristics and recommended generation method."""
        dataset_type = self._determine_dataset_type()
        dataset_balanced_type = self._determine_target_variable_balance()
        generation_method = self._determine_generation_method(
            dataset_type, dataset_balanced_type
        )
        return {
            "dataset_type": dataset_type.value,
            "balance": dataset_balanced_type.value,
            "recommended_method": generation_method.value,
            "num_rows": int(self.data.shape[0]),
            "num_features": int(self.data.shape[1]),
            "target_variable": self.target_variable,
        }

    @classmethod
    def create(cls, data, generation_params, for_notebook=False):
        synthesizer = cls(data, generation_params)
        if for_notebook:
            synthesizer.visualize_metadata()

        return synthesizer

    @property
    def metadata(self):
        return self._metadata_obj

    @metadata.setter
    def metadata(self, value):
        if isinstance(value, SingleTableMetadata):
            self._metadata_obj = value
        else:
            raise ValueError("Incorrect type for metadata.")
        
    def ctgan_generate(self):
        synthesizer = CTGANSynthesizer(self.metadata, epochs=self.epochs, verbose=False)
        synthesizer.fit(self.data)
        data_generated = synthesizer.sample(num_rows=self.num_rows)
        
        return data_generated
    
    def gaussian_copula_generate(self):
        synthesizer = GaussianCopulaSynthesizer(self.metadata)
        synthesizer.fit(self.data)

        data_generated = synthesizer.sample(num_rows=self.num_rows)

        return data_generated
    
    def copula_gan_generate(self):
        synthesizer = CopulaGANSynthesizer(self.metadata, epochs=self.epochs, verbose=False)
        synthesizer.fit(self.data)

        data_generated = synthesizer.sample(num_rows=self.num_rows)

        return data_generated
    
    def tvae_generate(self):
        synthesizer = TVAESynthesizer(self.metadata, epochs=self.epochs)
        synthesizer.fit(self.data)

        data_generated = synthesizer.sample(num_rows=self.num_rows)

        return data_generated
    
    def generate(self, method_override=None):
        dataset_type = self._determine_dataset_type()
        dataset_balanced_type = self._determine_target_variable_balance()
        self._log_info(
            f"The type of the dataset is: {dataset_balanced_type.value}-{dataset_type.value}."
        )
        generation_method = self._determine_generation_method(
            dataset_type, dataset_balanced_type
        )

        if method_override is not None:
            method_map = {
                "auto": None,
                "ctgan": GenerationMethod.CONDITIONAL_GAN,
                "gc": GenerationMethod.GAUSSIAN_COPULA,
                "gaussian_copula": GenerationMethod.GAUSSIAN_COPULA,
                "cgan": GenerationMethod.COPULA_GAN,
                "copula_gan": GenerationMethod.COPULA_GAN,
                "tvae": GenerationMethod.TVAE,
            }
            override = method_map.get(method_override.lower())
            if override is not None:
                generation_method = override

        self._log_info(f"Dataset will be generated by {generation_method.value} method.")

        generation_methods = {
            GenerationMethod.CONDITIONAL_GAN: self.ctgan_generate,
            GenerationMethod.GAUSSIAN_COPULA: self.gaussian_copula_generate,
            GenerationMethod.COPULA_GAN: self.copula_gan_generate,
            GenerationMethod.TVAE: self.tvae_generate,
        }

        generate_func = generation_methods.get(generation_method)

        self.method_used = generation_method.value
        data_generated = generate_func()

        return data_generated