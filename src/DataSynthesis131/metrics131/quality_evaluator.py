import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans
from table_evaluator import TableEvaluator
from sdv.evaluation.single_table import get_column_plot, run_diagnostic, evaluate_quality

class QualityEvaluator:
    def __init__(self, data, data_generated, metadata):
        self.data = data
        self.data_generated = data_generated
        self.metadata = metadata

    def _combine_datasets(self):
        data = self.data.copy()
        data_generated = self.data_generated.copy()
        
        data['is_synthetic'] = 0
        data_generated['is_synthetic'] = 1
        combined_data = pd.concat([data, data_generated], axis=0).reset_index(drop=True)

        categorical_columns = combined_data.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            combined_data_encoded = pd.DataFrame(ohe.fit_transform(combined_data[categorical_columns]))
            combined_data_encoded.columns = ohe.get_feature_names_out(categorical_columns)

            combined_data = combined_data.drop(columns=categorical_columns)
            combined_data = pd.concat([combined_data, combined_data_encoded], axis=1)

        combined_data = combined_data.sample(frac=1, random_state=42).reset_index(drop=True)

        return combined_data

    def _propensity_score(self):
        combined_data = self._combine_datasets()

        X = combined_data.drop('is_synthetic', axis=1)
        y = combined_data['is_synthetic']

        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

        clf = RandomForestClassifier(random_state=42)
        clf.fit(X_train, y_train)

        y_proba = clf.predict_proba(X)[:, 1]

        pMSE = np.mean((y_proba - 0.5) ** 2)

        print(f"Propensity score: {pMSE}")

        return pMSE

    def _log_cluster_metric(self, m=20):
        combined_data = self._combine_datasets()
        numeric_columns = combined_data.select_dtypes(include=['int64', 'float64']).columns
        scaler = StandardScaler()
        combined_data[numeric_columns] = scaler.fit_transform(combined_data[numeric_columns])

        kmeans = KMeans(n_clusters=m, n_init=10, random_state=42)
        kmeans.fit(combined_data[numeric_columns])
        combined_labels = kmeans.labels_

        boundary_index = len(self.data)
        ni = np.bincount(combined_labels, minlength=m)
        niR = np.bincount(combined_labels[:boundary_index], minlength=m)

        c = boundary_index / len(combined_labels)

        sum_of_squares = 0
        for i in range(m):
            sum_of_squares += (niR[i] / np.clip(ni[i], 1, None) - c) ** 2

        log_cluster_metric = np.log(sum_of_squares / m)
        print(f"Log-Cluster Metric: {log_cluster_metric}")

        return log_cluster_metric

    def _prediction_accuracy(self, target_column):
        X_generated = self.data_generated.drop(target_column, axis=1)
        y_generated = self.data_generated[target_column]

        X_real = self.data.drop(target_column, axis=1)
        y_real = self.data[target_column]

        clf = RandomForestClassifier(random_state=42)
        clf.fit(X_generated, y_generated)

        real_predictions = clf.predict(X_real)

        accuracy = accuracy_score(y_real, real_predictions)

        print(f'Prediction accuracy: {accuracy}')
        return accuracy

    def evaluate_metrics(self, target_column):
        propensity_score = self._propensity_score()
        log_cluster_metric = self._log_cluster_metric()
        prediction_accuracy = self._prediction_accuracy(target_column)

        return (propensity_score, log_cluster_metric, prediction_accuracy)

    def get_visual_evaluation(self, target_col):
        table_evaluator = TableEvaluator(self.data, self.data_generated)
        table_evaluator.evaluate(target_col=target_col)
        table_evaluator.visual_evaluation()

    def print_column_plot(self, column_name):
        fig = get_column_plot(
            real_data=self.data,
            synthetic_data=self.data_generated,
            column_name=column_name,
            metadata=self.metadata
        )

        fig.show()

    def evaluate_data_validity_with_structure(self):
        run_diagnostic(
            real_data=self.data,
            synthetic_data=self.data_generated,
            metadata=self.metadata
        )

    def get_quality_report(self):
        return evaluate_quality(
            self.data,
            self.data_generated,
            self.metadata
        )