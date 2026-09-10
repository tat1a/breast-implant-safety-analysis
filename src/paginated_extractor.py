"""Checkpointed openFDA extraction using the API's search-after Link header.

This module deliberately defaults to two small pages. Full extraction must not be
started until the pilot output and storage requirements have been reviewed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from src.openfda_client import API_ENDPOINT, ALLOWED_CODES, build_search

NEXT_LINK_RE = re.compile(r'<([^>]+)>;\s*rel="next"', re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_first_url(product_code: str, start_date: str, end_date: str, page_size: int) -> str:
    if not 1 <= page_size <= 1000:
        raise ValueError("page_size must be between 1 and 1000")
    params = {
        "search": build_search(product_code, start_date, end_date),
        "limit": str(page_size),
        "sort": "date_received:asc",
    }
    return f"{API_ENDPOINT}?{urlencode(params)}"


def next_url_from_link(link_header: str | None) -> str | None:
    if not link_header:
        return None
    match = NEXT_LINK_RE.search(link_header)
    return match.group(1) if match else None


def redact_api_key(url: str | None) -> str | None:
    if not url:
        return None
    parts = urlsplit(url)
    safe_query = [(key, value) for key, value in parse_qsl(parts.query) if key != "api_key"]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(safe_query), parts.fragment))


def write_json_atomic(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def extract_pages(
    product_code: str,
    start_date: str,
    end_date: str,
    page_size: int,
    max_pages: int,
    output_dir: Path,
    delay_seconds: float = 0.25,
) -> Path:
    if not 1 <= max_pages <= 10000:
        raise ValueError("max_pages must be between 1 and 10000")
    code = product_code.upper()
    if code not in ALLOWED_CODES:
        raise ValueError(f"product_code must be one of {sorted(ALLOWED_CODES)}")

    run_dir = output_dir / f"{code}_{start_date}_{end_date}"
    run_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = run_dir / "checkpoint.json"
    manifest = {
        "status": "running",
        "started_at_utc": utc_now(),
        "updated_at_utc": utc_now(),
        "product_code": code,
        "start_date": start_date,
        "end_date": end_date,
        "page_size": page_size,
        "requested_max_pages": max_pages,
        "sort": "date_received:asc",
        "pagination_method": "openFDA search_after via Link rel=next",
        "pages": [],
        "records_downloaded": 0,
        "unique_mdr_report_keys": 0,
        "duplicate_keys_across_pages": [],
        "next_url_without_api_key": redact_api_key(
            build_first_url(code, start_date, end_date, page_size)
        ),
    }
    write_json_atomic(checkpoint_path, manifest)

    url = build_first_url(code, start_date, end_date, page_size)
    seen_keys: set[str] = set()
    duplicates: set[str] = set()

    for page_number in range(1, max_pages + 1):
        request = Request(url, headers={"User-Agent": "clinical-data-portfolio/0.3"})
        with urlopen(request, timeout=60) as response:
            payload = response.read()
            link_header = response.headers.get("Link")
        parsed = json.loads(payload)
        results = parsed.get("results", [])
        total = parsed.get("meta", {}).get("results", {}).get("total")
        page_keys = [str(item.get("mdr_report_key", "")) for item in results]
        for key in page_keys:
            if key and key in seen_keys:
                duplicates.add(key)
            if key:
                seen_keys.add(key)

        page_path = run_dir / f"page_{page_number:05d}.json"
        page_path.write_bytes(payload)
        next_url = next_url_from_link(link_header)
        manifest["total_matching_records_reported_by_api"] = total
        manifest["pages"].append(
            {
                "page_number": page_number,
                "file": page_path.name,
                "records": len(results),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "first_mdr_report_key": page_keys[0] if page_keys else None,
                "last_mdr_report_key": page_keys[-1] if page_keys else None,
            }
        )
        manifest["records_downloaded"] += len(results)
        manifest["unique_mdr_report_keys"] = len(seen_keys)
        manifest["duplicate_keys_across_pages"] = sorted(duplicates)
        manifest["next_url_without_api_key"] = redact_api_key(next_url)
        manifest["updated_at_utc"] = utc_now()
        manifest["status"] = "complete" if not next_url else "pilot_stopped"
        write_json_atomic(checkpoint_path, manifest)

        if not next_url:
            break
        url = next_url
        if page_number < max_pages:
            time.sleep(max(0.0, delay_seconds))

    return checkpoint_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a bounded search-after pagination pilot.")
    parser.add_argument("--product-code", required=True, choices=sorted(ALLOWED_CODES))
    parser.add_argument("--start-date", default="20200101")
    parser.add_argument("--end-date", default="20251231")
    parser.add_argument("--page-size", type=int, default=5)
    parser.add_argument("--max-pages", type=int, default=2)
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw/pagination_pilot"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    checkpoint = extract_pages(
        args.product_code,
        args.start_date,
        args.end_date,
        args.page_size,
        args.max_pages,
        args.output_dir,
    )
    print(f"Checkpoint: {checkpoint}")
