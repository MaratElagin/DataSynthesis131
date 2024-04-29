import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from table_evaluator import TableEvaluator
from sdv.evaluation.single_table import get_column_plot, run_diagnostic, evaluate_quality
from IPython.display import display, Markdown

class QualityEvaluator:
    def __init__(self, data, data_generated, metadata, generation_params):
        self.data = data.copy()
        self.data_generated = data_generated.copy()
        self.metadata = metadata
        self.generation_params = generation_params
        self.target_variable = generation_params.target_variable if generation_params.target_variable is not None else "cluster"
        self._prepare_datasets()

    def _prepare_datasets(self):
        self._impute_missing_values(self.data)
        self._impute_missing_values(self.data_generated)
    
    def _impute_missing_values(self, df):
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        
        if numeric_columns.any() and df[numeric_columns].isna().any().any():
            numeric_imputer = SimpleImputer(strategy='mean')
            df[numeric_columns] = numeric_imputer.fit_transform(df[numeric_columns])
        
        if categorical_columns.any() and df[categorical_columns].isna().any().any():
            categorical_imputer = SimpleImputer(strategy='most_frequent')
            df[categorical_columns] = categorical_imputer.fit_transform(df[categorical_columns])

    def _combine_datasets(self):    
        data = self.data.copy()
        data_generated = self.data_generated.copy()

        data['is_synthetic'] = 0
        data_generated['is_synthetic'] = 1
        combined_data = pd.concat([data, data_generated], axis=0).reset_index(drop=True)

        categorical_columns = combined_data.select_dtypes(include=['object']).columns

        ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        encoded_data = ohe.fit_transform(combined_data[categorical_columns])
        encoded_df = pd.DataFrame(encoded_data, columns=ohe.get_feature_names_out(categorical_columns))

        combined_data = combined_data.drop(columns=categorical_columns).join(encoded_df)
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
    
    def _prediction_accuracy(self):
        X_generated = pd.get_dummies(self.data_generated.drop(self.target_variable, axis=1))
        y_generated = self.data_generated[self.target_variable]

        X_real = pd.get_dummies(self.data.drop(self.target_variable, axis=1))
        y_real = self.data[self.target_variable]

        X_real = X_real.reindex(columns=X_generated.columns, fill_value=0)
        
        clf = RandomForestClassifier(random_state=42)
        clf.fit(X_generated, y_generated)

        real_predictions = clf.predict(X_real)

        accuracy = accuracy_score(y_real, real_predictions)

        print(f'Prediction accuracy: {accuracy}')
        return accuracy

    def evaluate_metrics(self):
        propensity_score = self._propensity_score()
        log_cluster_metric = self._log_cluster_metric()
        prediction_accuracy = self._prediction_accuracy()

        return (propensity_score, log_cluster_metric, prediction_accuracy)

    def get_visual_evaluation(self):
        all_cols_set = set(self.metadata.get_column_names())
        numerical_cols_set = set(self.metadata.get_column_names(sdtype='numerical'))
        
        cat_cols = list(all_cols_set - numerical_cols_set)

        table_evaluator = TableEvaluator(self.data, self.data_generated, cat_cols=cat_cols)
        table_evaluator.evaluate(target_col=self.target_variable)
        table_evaluator.visual_evaluation()

    def print_column_plot(self, column_name, word_to_add = ''):
        fig = get_column_plot(
            real_data=self.data,
            synthetic_data=self.data_generated,
            column_name=column_name,
            metadata=self.metadata
        )

        title = (fig.layout.title.text if fig.layout.title else '') + ' ' + word_to_add

        fig.update_layout(title_text = title)

        fig.show()

    def evaluate_data_validity_with_structure(self, verbose=True):
        return run_diagnostic(
            real_data=self.data,
            synthetic_data=self.data_generated,
            metadata=self.metadata,
            verbose=verbose
        )

    def get_quality_report(self, verbose=True):
        return evaluate_quality(
            self.data,
            self.data_generated,
            self.metadata,
            verbose=verbose
        )
    
    def _print_distribution_plots(self, quality_report):
        column_shapes = quality_report.get_details('Column Shapes')

        rows_to_drop = column_shapes[column_shapes['Column'] == "cluster"].index
        column_shapes.drop(rows_to_drop, inplace=True)

        sorted_df = column_shapes.sort_values('Score', ignore_index=True)

        min_score_col = sorted_df.loc[0, 'Column']
        min_score = sorted_df.loc[0, 'Score']
        
        median_index = len(sorted_df) // 2
        median_score_col = sorted_df.loc[median_index, 'Column']
        median_score = sorted_df.loc[median_index, 'Score']
        
        max_score_col = sorted_df.loc[len(sorted_df) - 1, 'Column']
        max_score = sorted_df.loc[len(sorted_df) - 1, 'Score']

        self.print_column_plot(max_score_col, word_to_add=f'(Best distribution column: {max_score * 100:.2f}%)')
        self.print_column_plot(median_score_col, word_to_add=f'(Representative distribution column: {median_score * 100:.2f}%)')
        self.print_column_plot(min_score_col, word_to_add=f'(Worst distribution column: {min_score * 100:.2f}%)')
    
    def evaluate(self, with_details = False):
        self.evaluate_metrics()

        diagnostic_report = self.evaluate_data_validity_with_structure(verbose=False)
        data_validity = diagnostic_report.get_score()
        print(f'Data validity: {data_validity * 100:.2f}%')

        quality_report = self.get_quality_report(verbose=False)
        sdv_score = quality_report.get_score()
        print(f'SDV score: {sdv_score * 100:.2f}%')

        self._print_distribution_plots(quality_report)

        if (with_details):
            display(Markdown('# Table evaluator visualization'))
            self.get_visual_evaluation()
