"""Resumable openFDA extraction for the frozen 2020--2025 FTR/FWM cohort.

No network request is made on import. Raw pages and checkpoints remain local and
are excluded from Git. The extraction can be interrupted and resumed safely.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.paginated_extractor import (
    build_first_url,
    next_url_from_link,
    redact_api_key,
    write_json_atomic,
)

FROZEN_START_DATE = "20200101"
FROZEN_END_DATE = "20251231"
FROZEN_CODES = ("FTR", "FWM")
SORT_ORDER = "date_received:asc"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def add_api_key(url: str, api_key: str | None) -> str:
    """Add the secret at request time; checkpoint URLs always remain redacted."""
    if not api_key:
        return url
    parts = urlsplit(url)
    query = [(key, value) for key, value in parse_qsl(parts.query) if key != "api_key"]
    query.insert(0, ("api_key", api_key))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def read_page(path: Path, expected_sha256: str | None = None) -> dict:
    payload = path.read_bytes()
    if expected_sha256 and sha256_bytes(payload) != expected_sha256:
        raise ValueError(f"checksum mismatch: {path}")
    return json.loads(payload)


def validate_checkpoint(checkpoint: dict, code: str, start: str, end: str, page_size: int) -> None:
    expected = {
        "product_code": code,
        "start_date": start,
        "end_date": end,
        "page_size": page_size,
        "sort": SORT_ORDER,
    }
    mismatches = [key for key, value in expected.items() if checkpoint.get(key) != value]
    if mismatches:
        raise ValueError("checkpoint does not match requested run: " + ", ".join(mismatches))


def load_seen_keys(run_dir: Path, checkpoint: dict) -> tuple[set[str], set[str]]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for page in checkpoint.get("pages", []):
        parsed = read_page(run_dir / page["file"], page.get("sha256"))
        for item in parsed.get("results", []):
            key = str(item.get("mdr_report_key", "")).strip()
            if key and key in seen:
                duplicates.add(key)
            if key:
                seen.add(key)
    return seen, duplicates


def initial_checkpoint(code: str, start: str, end: str, page_size: int) -> dict:
    now = utc_now()
    first_url = build_first_url(code, start, end, page_size)
    return {
        "schema_version": 1,
        "status": "running",
        "started_at_utc": now,
        "updated_at_utc": now,
        "product_code": code,
        "start_date": start,
        "end_date": end,
        "page_size": page_size,
        "sort": SORT_ORDER,
        "pagination_method": "openFDA search_after via Link rel=next",
        "pages": [],
        "records_downloaded": 0,
        "unique_mdr_report_keys": 0,
        "duplicate_keys_across_pages": [],
        "next_url_without_api_key": redact_api_key(first_url),
        "total_matching_records_reported_by_api": None,
        "qc_gate_passed": False,
    }


def request_page(url: str, retries: int, retry_base_seconds: float) -> tuple[bytes, str | None]:
    for attempt in range(retries + 1):
        try:
            request = Request(url, headers={"User-Agent": "clinical-data-portfolio/0.5"})
            with urlopen(request, timeout=60) as response:
                return response.read(), response.headers.get("Link")
        except (HTTPError, URLError, TimeoutError):
            if attempt == retries:
                raise
            time.sleep(retry_base_seconds * (2**attempt))
    raise RuntimeError("unreachable")


def extract_full_code(
    product_code: str,
    output_dir: Path,
    *,
    start_date: str = FROZEN_START_DATE,
    end_date: str = FROZEN_END_DATE,
    page_size: int = 1000,
    delay_seconds: float = 0.25,
    retries: int = 4,
    retry_base_seconds: float = 1.0,
    max_pages: int | None = None,
    api_key: str | None = None,
) -> Path:
    code = product_code.upper()
    if code not in FROZEN_CODES:
        raise ValueError(f"product_code must be one of {FROZEN_CODES}")
    if not 1 <= page_size <= 1000:
        raise ValueError("page_size must be between 1 and 1000")
    if retries < 0:
        raise ValueError("retries must be non-negative")

    run_dir = output_dir / f"{code}_{start_date}_{end_date}"
    run_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = run_dir / "checkpoint.json"

    if checkpoint_path.exists():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        validate_checkpoint(checkpoint, code, start_date, end_date, page_size)
        if checkpoint.get("status") == "complete" and checkpoint.get("qc_gate_passed"):
            return checkpoint_path
    else:
        checkpoint = initial_checkpoint(code, start_date, end_date, page_size)
        write_json_atomic(checkpoint_path, checkpoint)

    seen, duplicates = load_seen_keys(run_dir, checkpoint)
    url = checkpoint.get("next_url_without_api_key")
    if not url:
        raise ValueError("incomplete checkpoint has no resume URL")
    first_new_page = len(checkpoint.get("pages", [])) + 1
    pages_this_run = 0

    while url and (max_pages is None or pages_this_run < max_pages):
        request_url = add_api_key(url, api_key or os.environ.get("OPENFDA_API_KEY"))
        payload, link_header = request_page(request_url, retries, retry_base_seconds)
        parsed = json.loads(payload)
        results = parsed.get("results", [])
        if not isinstance(results, list):
            raise ValueError("openFDA response results must be a list")

        page_number = first_new_page + pages_this_run
        page_path = run_dir / f"page_{page_number:05d}.json"
        temporary = page_path.with_suffix(".json.tmp")
        temporary.write_bytes(payload)
        temporary.replace(page_path)

        page_keys = [str(item.get("mdr_report_key", "")).strip() for item in results]
        for key in page_keys:
            if key and key in seen:
                duplicates.add(key)
            if key:
                seen.add(key)

        next_url = next_url_from_link(link_header)
        checkpoint["pages"].append({
            "page_number": page_number,
            "file": page_path.name,
            "records": len(results),
            "sha256": sha256_bytes(payload),
            "first_mdr_report_key": page_keys[0] if page_keys else None,
            "last_mdr_report_key": page_keys[-1] if page_keys else None,
        })
        checkpoint["records_downloaded"] += len(results)
        checkpoint["unique_mdr_report_keys"] = len(seen)
        checkpoint["duplicate_keys_across_pages"] = sorted(duplicates)
        checkpoint["total_matching_records_reported_by_api"] = (
            parsed.get("meta", {}).get("results", {}).get("total")
        )
        checkpoint["next_url_without_api_key"] = redact_api_key(next_url)
        checkpoint["updated_at_utc"] = utc_now()
        checkpoint["status"] = "complete" if not next_url else "paused"
        checkpoint["qc_gate_passed"] = bool(
            not next_url
            and not duplicates
            and checkpoint["records_downloaded"] == len(seen)
        )
        write_json_atomic(checkpoint_path, checkpoint)

        pages_this_run += 1
        url = next_url
        if url and (max_pages is None or pages_this_run < max_pages):
            time.sleep(max(0.0, delay_seconds))

    return checkpoint_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resume the frozen full-cohort openFDA extraction.")
    parser.add_argument("--product-code", required=True, choices=FROZEN_CODES)
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw/full_extraction"))
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument("--max-pages", type=int, default=None,
                        help="Optional dry-run bound; omit for all remaining pages.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = extract_full_code(
        args.product_code,
        args.output_dir,
        page_size=args.page_size,
        max_pages=args.max_pages,
    )
    print(f"Checkpoint: {result}")
