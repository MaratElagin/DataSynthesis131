import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sdv.evaluation.single_table import evaluate_quality, get_column_plot, run_diagnostic
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from ..common.common import impute_missing_values
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class QualityEvaluator:
    def __init__(self, data, data_generated, metadata, generation_params):
        self.data = data.copy()
        self.data_generated = data_generated.copy()
        self.metadata = metadata
        self.generation_params = generation_params
        self.target_variable = (
            generation_params.target_variable
            if generation_params.target_variable is not None
            else "cluster"
        )
        self._prepare_datasets()

    def _prepare_datasets(self):
        self._impute_missing_values(self.data)
        self._impute_missing_values(self.data_generated)

    def _impute_missing_values(self, df):
        impute_missing_values(df)

    def _combine_datasets(self):
        data = self.data.copy()
        data_generated = self.data_generated.copy()

        data["is_synthetic"] = 0
        data_generated["is_synthetic"] = 1
        combined_data = pd.concat([data, data_generated], axis=0).reset_index(drop=True)

        categorical_columns = combined_data.select_dtypes(include=["object"]).columns

        ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        encoded_data = ohe.fit_transform(combined_data[categorical_columns])
        encoded_df = pd.DataFrame(
            encoded_data, columns=ohe.get_feature_names_out(categorical_columns)
        )

        combined_data = combined_data.drop(columns=categorical_columns).join(encoded_df)
        combined_data = combined_data.sample(frac=1, random_state=42).reset_index(drop=True)

        return combined_data

    def _propensity_score(self):
        combined_data = self._combine_datasets()

        X = combined_data.drop("is_synthetic", axis=1)
        y = combined_data["is_synthetic"]

        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

        clf = RandomForestClassifier(random_state=42)
        clf.fit(X_train, y_train)

        y_proba = clf.predict_proba(X)[:, 1]

        return float(np.mean((y_proba - 0.5) ** 2))

    def _log_cluster_metric(self, m=20):
        combined_data = self._combine_datasets()
        numeric_columns = combined_data.select_dtypes(include=["int64", "float64"]).columns
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

        return float(np.log(sum_of_squares / m))

    def _prediction_accuracy(self):
        X_generated = pd.get_dummies(self.data_generated.drop(self.target_variable, axis=1))
        y_generated = self.data_generated[self.target_variable]

        X_real = pd.get_dummies(self.data.drop(self.target_variable, axis=1))
        y_real = self.data[self.target_variable]

        X_real = X_real.reindex(columns=X_generated.columns, fill_value=0)

        clf = RandomForestClassifier(random_state=42)
        clf.fit(X_generated, y_generated)

        real_predictions = clf.predict(X_real)

        return float(accuracy_score(y_real, real_predictions))

    def evaluate_metrics(self):
        propensity_score = self._propensity_score()
        log_cluster_metric = self._log_cluster_metric()
        prediction_accuracy = self._prediction_accuracy()

        return (propensity_score, log_cluster_metric, prediction_accuracy)

    def evaluate_data_validity_with_structure(self, verbose=True):
        return run_diagnostic(
            real_data=self.data,
            synthetic_data=self.data_generated,
            metadata=self.metadata,
            verbose=verbose,
        )

    def get_quality_report(self, verbose=True):
        return evaluate_quality(
            self.data,
            self.data_generated,
            self.metadata,
            verbose=verbose,
        )

    def _save_column_plot(self, column_name, output_path, title_suffix=""):
        fig = get_column_plot(
            real_data=self.data,
            synthetic_data=self.data_generated,
            column_name=column_name,
            metadata=self.metadata,
        )
        base_title = fig.layout.title.text if fig.layout.title else column_name
        fig.update_layout(title_text=f"{base_title} {title_suffix}".strip())
        fig.write_image(str(output_path), width=900, height=500, scale=1)

    def _save_distribution_plots(self, plots_dir, quality_report=None):
        """Save SDV column plots for all columns.
        Returns (dict {col_name: filename}, picks dict with best/median/worst info).
        """
        if quality_report is None:
            quality_report = self.get_quality_report(verbose=False)
        column_shapes = quality_report.get_details("Column Shapes")

        column_shapes = column_shapes[column_shapes["Column"] != "cluster"].copy()
        if column_shapes.empty:
            return {}, {}

        sorted_df = column_shapes.sort_values("Score", ignore_index=True)
        n = len(sorted_df)

        picks = {}
        if n >= 1:
            picks["best"] = {"col": sorted_df.iloc[-1]["Column"], "score": float(sorted_df.iloc[-1]["Score"])}
        if n >= 2:
            picks["worst"] = {"col": sorted_df.iloc[0]["Column"], "score": float(sorted_df.iloc[0]["Score"])}
        if n >= 3:
            picks["median"] = {"col": sorted_df.iloc[n // 2]["Column"], "score": float(sorted_df.iloc[n // 2]["Score"])}

        # Save picks first (best / median / worst) — log errors so we can debug
        pick_cols = {info["col"] for info in picks.values()}
        saved = {}
        for _, row in sorted_df.iterrows():
            col = row["Column"]
            score = row["Score"]
            filename = f"sdv_{col}.png"
            path = plots_dir / filename
            try:
                self._save_column_plot(col, path, title_suffix=f"({score * 100:.2f}%)")
                saved[col] = filename
            except Exception as exc:
                if col in pick_cols:
                    print(f"[QualityEvaluator] SDV plot failed for '{col}': {exc}", flush=True)

        return saved, picks

    def _save_numeric_histograms(self, plots_dir):
        """Save matplotlib histograms for all numeric columns. Returns {col_name: filename}."""
        numeric_cols = list(self.metadata.get_column_names(sdtype="numerical"))
        numeric_cols = [c for c in numeric_cols if c != "cluster"]
        saved = {}

        for col in numeric_cols:
            fig, ax = plt.subplots(figsize=(9, 5))
            real_vals = pd.to_numeric(self.data[col], errors="coerce").dropna()
            synth_vals = pd.to_numeric(self.data_generated[col], errors="coerce").dropna()

            if real_vals.empty or synth_vals.empty:
                plt.close(fig)
                continue

            ax.hist(real_vals, bins=30, alpha=0.5, label="Real", density=True)
            ax.hist(synth_vals, bins=30, alpha=0.5, label="Synthetic", density=True)
            ax.set_title(f"Distribution: {col}")
            ax.legend()
            filename = f"histogram_{col}.png"
            fig.savefig(plots_dir / filename, bbox_inches="tight", dpi=120)
            plt.close(fig)
            saved[col] = filename

        return saved

    def _save_correlation_heatmaps(self, plots_dir):
        saved = []

        for label, df in [("real", self.data), ("synthetic", self.data_generated)]:
            numeric_df = df.select_dtypes(include=["number"]).drop(
                columns=["cluster"], errors="ignore"
            )
            if numeric_df.shape[1] < 2:
                continue

            corr = numeric_df.corr(numeric_only=True)
            if corr.empty:
                continue

            size = min(12, max(6, corr.shape[0] * 0.4))
            fig, ax = plt.subplots(figsize=(size, size))
            sns.heatmap(corr, ax=ax, cmap="coolwarm", center=0, square=True)
            ax.set_title(f"Correlation matrix ({label})")
            filename = f"correlation_{label}.png"
            fig.savefig(plots_dir / filename, bbox_inches="tight", dpi=120)
            plt.close(fig)
            saved.append(filename)

        return saved

    def export_report(self, output_dir):
        """Compute metrics and save plot PNGs for web display."""
        output_dir = Path(output_dir)
        plots_dir = output_dir / "plots"
        plots_dir.mkdir(parents=True, exist_ok=True)

        propensity_score, log_cluster_metric, prediction_accuracy = self.evaluate_metrics()

        diagnostic_report = self.evaluate_data_validity_with_structure(verbose=False)
        data_validity = float(diagnostic_report.get_score())

        quality_report = self.get_quality_report(verbose=False)
        sdv_score = float(quality_report.get_score())

        column_shapes_details = []
        try:
            col_shapes_df = quality_report.get_details("Column Shapes")
            col_shapes_df = col_shapes_df[col_shapes_df["Column"] != "cluster"]
            col_shapes_df = col_shapes_df.sort_values("Score", ascending=False)
            column_shapes_details = col_shapes_df[["Column", "Score"]].to_dict(orient="records")
        except Exception:
            pass

        # Overall quality score (0–1): normalized weighted average of all metrics
        prop_normalized = max(0.0, 1.0 - propensity_score * 4)
        lc_normalized = max(0.0, min(1.0, (-log_cluster_metric) / 3))
        overall_score = (
            prop_normalized + lc_normalized + prediction_accuracy + data_validity + sdv_score
        ) / 5

        column_plots = {}
        distribution_picks = {}
        try:
            column_plots, distribution_picks = self._save_distribution_plots(plots_dir, quality_report=quality_report)
        except Exception:
            pass

        histogram_plots = {}
        try:
            histogram_plots = self._save_numeric_histograms(plots_dir)
        except Exception:
            pass

        correlation_plots = []
        try:
            correlation_plots = self._save_correlation_heatmaps(plots_dir)
        except Exception:
            pass

        # Flat list of all plot files (backwards compat)
        all_plots = list(column_plots.values()) + list(histogram_plots.values()) + correlation_plots

        report = {
            "propensity_score": propensity_score,
            "log_cluster_metric": log_cluster_metric,
            "prediction_accuracy": prediction_accuracy,
            "data_validity": data_validity,
            "sdv_score": sdv_score,
            "overall_score": overall_score,
            "column_shapes_details": column_shapes_details,
            "column_plots": column_plots,
            "distribution_picks": distribution_picks,
            "histogram_plots": histogram_plots,
            "correlation_plots": correlation_plots,
            "plots": all_plots,
        }

        report_path = output_dir / "report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report

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

    def get_visual_evaluation(self):
        from table_evaluator import TableEvaluator

        all_cols_set = set(self.metadata.get_column_names())
        numerical_cols_set = set(self.metadata.get_column_names(sdtype="numerical"))

        cat_cols = list(all_cols_set - numerical_cols_set)

        table_evaluator = TableEvaluator(
            self.data, self.data_generated, cat_cols=cat_cols, verbose=False
        )
        table_evaluator.evaluate(target_col=self.target_variable)
        table_evaluator.visual_evaluation()

    def print_column_plot(self, column_name, word_to_add=""):
        fig = get_column_plot(
            real_data=self.data,
            synthetic_data=self.data_generated,
            column_name=column_name,
            metadata=self.metadata,
        )

        title = (fig.layout.title.text if fig.layout.title else "") + " " + word_to_add

        fig.update_layout(title_text=title)
        fig.show()

    def _print_distribution_plots(self, quality_report):
        column_shapes = quality_report.get_details("Column Shapes")

        rows_to_drop = column_shapes[column_shapes["Column"] == "cluster"].index
        column_shapes.drop(rows_to_drop, inplace=True)

        sorted_df = column_shapes.sort_values("Score", ignore_index=True)

        min_score_col = sorted_df.loc[0, "Column"]
        min_score = sorted_df.loc[0, "Score"]

        median_index = len(sorted_df) // 2
        median_score_col = sorted_df.loc[median_index, "Column"]
        median_score = sorted_df.loc[median_index, "Score"]

        max_score_col = sorted_df.loc[len(sorted_df) - 1, "Column"]
        max_score = sorted_df.loc[len(sorted_df) - 1, "Score"]

        self.print_column_plot(
            max_score_col,
            word_to_add=f"(Best distribution column: {max_score * 100:.2f}%)",
        )
        self.print_column_plot(
            median_score_col,
            word_to_add=f"(Representative distribution column: {median_score * 100:.2f}%)",
        )
        self.print_column_plot(
            min_score_col,
            word_to_add=f"(Worst distribution column: {min_score * 100:.2f}%)",
        )

    def evaluate(self, with_details=False):
        propensity_score, log_cluster_metric, prediction_accuracy = self.evaluate_metrics()
        print(f"Propensity score: {propensity_score}")
        print(f"Log-Cluster Metric: {log_cluster_metric}")
        print(f"Prediction accuracy: {prediction_accuracy}")

        diagnostic_report = self.evaluate_data_validity_with_structure(verbose=False)
        data_validity = diagnostic_report.get_score()
        print(f"Data validity: {data_validity * 100:.2f}%")

        quality_report = self.get_quality_report(verbose=False)
        sdv_score = quality_report.get_score()
        print(f"SDV score: {sdv_score * 100:.2f}%")

        self._print_distribution_plots(quality_report)

        if with_details:
            try:
                from IPython.display import Markdown, display

                display(Markdown("# Table evaluator visualization"))
            except ImportError:
                pass
            self.get_visual_evaluation()
