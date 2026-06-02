import json
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import pandas as pd

from DataSynthesis131 import GenerationParams, QualityEvaluator, Synthesizer

from .jobs import JobStatus, job_store


def load_dataframe(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")

    if df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated(keep="first")]
    return df


def build_preview(df: pd.DataFrame, max_rows: int = 5) -> Dict[str, Any]:
    preview_df = df.head(max_rows)
    return {
        "num_rows": int(df.shape[0]),
        "num_columns": int(df.shape[1]),
        "columns": list(df.columns),
        "preview_rows": preview_df.fillna("").astype(str).values.tolist(),
        "preview_row_count": int(len(preview_df)),
    }


def run_generation_pipeline(
    job_id: str,
    params: Dict[str, Any],
    progress_callback: Optional[Callable[[int, str], None]] = None,
):
    class Cancelled(Exception):
        pass

    def update(progress: int, message: str):
        job = job_store.get(job_id)
        if job and job.cancel_event.is_set():
            raise Cancelled()
        job_store.update(
            job_id, status=JobStatus.RUNNING, progress=progress, message=message
        )
        if progress_callback:
            progress_callback(progress, message)

    job = job_store.get(job_id)
    if job is None or job.input_path is None or job.work_dir is None:
        return

    work_dir = Path(job.work_dir)

    MAX_TRAIN_ROWS = 10_000

    try:
        update(5, "Loading dataset")
        df = load_dataframe(Path(job.input_path))

        if len(df) > MAX_TRAIN_ROWS:
            df = df.sample(n=MAX_TRAIN_ROWS, random_state=42).reset_index(drop=True)
            update(8, f"Dataset sampled to {MAX_TRAIN_ROWS} rows for training")

        num_rows = int(params.get("num_rows", df.shape[0]))
        gen_params = GenerationParams(
            num_rows=num_rows,
            fast_result=bool(params.get("fast_result", False)),
            target_variable=params.get("target_variable") or None,
            with_missing_values=bool(params.get("with_missing_values", True)),
            epochs=int(params.get("epochs", 1000)),
        )

        update(15, "Analyzing dataset characteristics")
        synthesizer = Synthesizer(df, gen_params)
        analysis = synthesizer.analyze()
        job_store.update(job_id, analysis=analysis)

        method_override = params.get("method", "auto")
        if method_override == "auto":
            method_override = None

        update(25, f"Training synthesizer ({analysis['recommended_method']})")
        data_generated = synthesizer.generate(method_override=method_override)
        method_used = synthesizer.method_used

        merge_with_input = bool(params.get("merge_with_input", False))

        update(90, "Saving synthetic dataset")
        if merge_with_input:
            synthetic_path = work_dir / "synthetic_merged.csv"
            merged_df = pd.concat([df, data_generated], ignore_index=True)
            merged_df.to_csv(synthetic_path, index=False)
        else:
            synthetic_path = work_dir / "synthetic.csv"
            data_generated.to_csv(synthetic_path, index=False)

        update(95, "Evaluating quality and building report")
        evaluator = QualityEvaluator(
            synthesizer.data,
            data_generated,
            synthesizer.metadata,
            gen_params,
        )
        report = evaluator.export_report(work_dir)

        report["analysis"] = analysis
        report["method_used"] = method_used
        report["merge_with_input"] = merge_with_input

        report_path = work_dir / "report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        job_store.update(
            job_id,
            status=JobStatus.COMPLETED,
            progress=100,
            message="Generation completed",
            method_used=method_used,
            report=report,
            synthetic_path=str(synthetic_path),
        )
    except Cancelled:
        job_store.update(
            job_id,
            status=JobStatus.CANCELLED,
            progress=0,
            message="Cancelled",
        )
    except Exception as exc:
        job_store.update(
            job_id,
            status=JobStatus.FAILED,
            progress=100,
            message="Generation failed",
            error=str(exc),
        )
