import re
import subprocess
import tempfile
from pathlib import Path
import os
from typing import List, Optional, Tuple


KAGGLE_URL_PATTERN = re.compile(
    r"kaggle\.com/datasets/(?P<owner>[^/]+)/(?P<slug>[^/?#]+)"
)


def parse_kaggle_url(url: str) -> Tuple[str, str]:
    match = KAGGLE_URL_PATTERN.search(url.strip())
    if not match:
        raise ValueError(
            "Invalid Kaggle URL. Expected format: "
            "https://www.kaggle.com/datasets/owner/dataset-name"
        )
    return match.group("owner"), match.group("slug")


def download_kaggle_dataset(
    url: str,
    destination: Path,
    file_name: Optional[str] = None,
    kaggle_username: Optional[str] = None,
    kaggle_key: Optional[str] = None,
) -> Path:
    owner, slug = parse_kaggle_url(url)
    dataset_ref = f"{owner}/{slug}"

    destination.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    if kaggle_username:
        env["KAGGLE_USERNAME"] = kaggle_username
    if kaggle_key:
        env["KAGGLE_KEY"] = kaggle_key

    try:
        subprocess.run(
            [
                "kaggle",
                "datasets",
                "download",
                "-d",
                dataset_ref,
                "-p",
                str(destination),
                "--unzip",
            ],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Kaggle CLI not found. Install with: pip install kaggle"
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr or exc.stdout or str(exc)
        if "401" in stderr or "403" in stderr or "Unauthorized" in stderr:
            raise RuntimeError(
                "Kaggle authentication failed. Set KAGGLE_USERNAME and "
                "KAGGLE_KEY environment variables or configure ~/.kaggle/kaggle.json"
            ) from exc
        raise RuntimeError(f"Kaggle download failed: {stderr}") from exc

    csv_files = list(destination.rglob("*.csv"))
    if not csv_files:
        raise RuntimeError("No CSV files found in downloaded Kaggle dataset")

    if file_name:
        matches = [p for p in csv_files if p.name == file_name]
        if not matches:
            available = ", ".join(p.name for p in csv_files[:10])
            raise RuntimeError(
                f"File '{file_name}' not found. Available CSV files: {available}"
            )
        return matches[0]

    return csv_files[0]


def list_kaggle_csv_files(url: str) -> List[str]:
    owner, slug = parse_kaggle_url(url)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        subprocess.run(
            [
                "kaggle",
                "datasets",
                "download",
                "-d",
                f"{owner}/{slug}",
                "-p",
                str(tmp_path),
                "--unzip",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return sorted(p.name for p in tmp_path.rglob("*.csv"))
