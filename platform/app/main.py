import os
import shutil
import uuid
from pathlib import Path
from threading import Thread
from typing import Any, Dict, Optional

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .jobs import JobStatus, job_store
from .kaggle_loader import download_kaggle_dataset
from .pipeline import build_preview, load_dataframe, run_generation_pipeline

PLATFORM_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PLATFORM_DIR / ".env")
STATIC_DIR = PLATFORM_DIR / "static"
DATA_DIR = PLATFORM_DIR / "data" / "tmp"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class GenerateRequest(BaseModel):
    job_id: str
    num_rows: Optional[int] = None
    target_variable: Optional[str] = None
    fast_result: bool = False
    with_missing_values: bool = True
    epochs: int = 1000
    method: str = "auto"
    merge_with_input: bool = False


class KaggleUploadRequest(BaseModel):
    kaggle_url: str
    file_name: Optional[str] = None
    kaggle_username: Optional[str] = None
    kaggle_key: Optional[str] = None


app = FastAPI(
    title="DataSynthesis131 Platform",
    description="Web platform for synthetic tabular data generation",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.middleware("http")
async def dev_disable_static_cache(request, call_next):
    response = await call_next(request)
    if os.getenv("PLATFORM_DEV") and (
        request.url.path.startswith("/static")
        or request.url.path in ("/", "/about")
    ):
        response.headers["Cache-Control"] = "no-store, must-revalidate"
    return response


def create_job_work_dir(job_id: str) -> Path:
    work_dir = DATA_DIR / job_id
    work_dir.mkdir(parents=True, exist_ok=True)
    return work_dir


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/about")
async def about():
    return FileResponse(STATIC_DIR / "about.html")


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename or "dataset.csv"
    suffix = Path(filename).suffix.lower()
    if suffix not in (".csv", ".xlsx", ".xls"):
        raise HTTPException(
            status_code=400,
            detail="Supported formats: .csv, .xlsx, .xls",
        )

    contents = await file.read()
    job_id = str(uuid.uuid4())
    work_dir = create_job_work_dir(job_id)
    temp_path = work_dir / f"upload{suffix}"
    temp_path.write_bytes(contents)

    try:
        df = load_dataframe(temp_path)
    except Exception as exc:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f"Failed to read file: {exc}") from exc

    input_path = work_dir / "input.csv"
    df.to_csv(input_path, index=False)
    preview = build_preview(df)
    preview["source"] = "file"
    preview["filename"] = filename

    job = job_store.create(
        work_dir=str(work_dir),
        input_path=str(input_path),
        preview=preview,
        job_id=job_id,
    )
    return {"job_id": job.id, "preview": preview}


@app.post("/api/upload/kaggle")
async def upload_kaggle(body: KaggleUploadRequest):
    job_id = str(uuid.uuid4())
    work_dir = create_job_work_dir(job_id)
    download_dir = work_dir / "kaggle"

    try:
        csv_path = download_kaggle_dataset(
            body.kaggle_url,
            download_dir,
            file_name=body.file_name,
            kaggle_username=body.kaggle_username,
            kaggle_key=body.kaggle_key,
        )
        df = pd.read_csv(csv_path)
    except Exception as exc:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    input_path = work_dir / "input.csv"
    df.to_csv(input_path, index=False)
    preview = build_preview(df)
    preview["source"] = "kaggle"
    preview["filename"] = csv_path.name
    preview["kaggle_url"] = body.kaggle_url

    job = job_store.create(
        work_dir=str(work_dir),
        input_path=str(input_path),
        preview=preview,
        job_id=job_id,
    )
    return {"job_id": job.id, "preview": preview}


@app.get("/api/jobs/{job_id}/analyze")
async def analyze_job(job_id: str):
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.input_path is None:
        raise HTTPException(status_code=400, detail="No input data for job")

    from DataSynthesis131 import GenerationParams, Synthesizer

    df = load_dataframe(Path(job.input_path))
    gen_params = GenerationParams(num_rows=df.shape[0])
    synthesizer = Synthesizer(df, gen_params)
    analysis = synthesizer.analyze()
    job_store.update(job_id, analysis=analysis)
    return analysis


@app.post("/api/generate")
async def generate(body: GenerateRequest):
    job = job_store.get(body.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status == JobStatus.RUNNING:
        raise HTTPException(status_code=409, detail="Job is already running")

    job_store.update(
        body.job_id,
        status=JobStatus.QUEUED,
        progress=0,
        message="Queued for generation",
        error=None,
    )

    params = body.model_dump()
    thread = Thread(
        target=run_generation_pipeline,
        args=(body.job_id, params),
        daemon=True,
    )
    thread.start()

    return {"job_id": body.job_id, "status": "queued"}


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "status": job.status.value,
        "progress": job.progress,
        "message": job.message,
        "method_used": job.method_used,
        "analysis": job.analysis,
        "preview": job.preview,
        "error": job.error,
    }


@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    job_store.cancel(job_id)
    return {"job_id": job_id, "status": "cancelling"}


@app.get("/api/jobs/{job_id}/download")
async def download_synthetic(
    job_id: str,
    format: str = Query(default="csv", pattern="^(csv|xlsx)$"),
):
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.synthetic_path is None or not Path(job.synthetic_path).exists():
        raise HTTPException(status_code=404, detail="Synthetic file not ready")

    is_merged = job.report and job.report.get("merge_with_input")
    base_name = "synthetic_merged" if is_merged else "synthetic"

    if format == "xlsx":
        xlsx_path = Path(job.work_dir) / f"{base_name}.xlsx"
        if not xlsx_path.exists():
            df = pd.read_csv(job.synthetic_path)
            df.to_excel(xlsx_path, index=False)
        return FileResponse(
            xlsx_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"{base_name}.xlsx",
        )

    return FileResponse(
        job.synthetic_path,
        media_type="text/csv",
        filename=f"{base_name}.csv",
    )


@app.get("/api/jobs/{job_id}/report")
async def get_report(job_id: str):
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.report is None:
        raise HTTPException(status_code=404, detail="Report not ready")

    def to_url(name: str) -> str:
        return f"/api/jobs/{job_id}/plots/{name}"

    plots = [to_url(n) for n in job.report.get("plots", [])]
    column_plot_urls = {col: to_url(f) for col, f in job.report.get("column_plots", {}).items()}
    histogram_plot_urls = {col: to_url(f) for col, f in job.report.get("histogram_plots", {}).items()}
    correlation_plot_urls = [to_url(f) for f in job.report.get("correlation_plots", [])]

    return {
        **job.report,
        "plot_urls": plots,
        "column_plot_urls": column_plot_urls,
        "histogram_plot_urls": histogram_plot_urls,
        "correlation_plot_urls": correlation_plot_urls,
    }


@app.get("/api/jobs/{job_id}/report.pdf")
async def download_pdf_report(job_id: str):
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.report is None or job.work_dir is None:
        raise HTTPException(status_code=404, detail="Report not ready")

    work_dir = Path(job.work_dir)
    pdf_path = work_dir / "report.pdf"
    if not pdf_path.exists():
        from .pdf_report import generate_pdf_report
        generate_pdf_report(job.report, work_dir)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="quality_report.pdf",
    )


@app.get("/api/jobs/{job_id}/plots/{plot_name}")
async def get_plot(job_id: str, plot_name: str):
    job = job_store.get(job_id)
    if job is None or job.work_dir is None:
        raise HTTPException(status_code=404, detail="Job not found")

    plot_path = Path(job.work_dir) / "plots" / plot_name
    if not plot_path.exists() or plot_path.suffix.lower() != ".png":
        raise HTTPException(status_code=404, detail="Plot not found")

    return FileResponse(plot_path, media_type="image/png")
