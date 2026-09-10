"""Small, dependency-free openFDA Device Event extraction client.

Raw API responses are written under data/raw/ and must never be committed.
The companion manifest contains no API key and no narrative or patient data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_ENDPOINT = "https://api.fda.gov/device/event.json"
ALLOWED_CODES = {"FTR", "FWM"}


def validate_date(value: str) -> str:
    """Accept YYYYMMDD only and reject impossible calendar dates."""
    datetime.strptime(value, "%Y%m%d")
    return value


def build_search(product_code: str, start_date: str, end_date: str) -> str:
    code = product_code.upper()
    if code not in ALLOWED_CODES:
        raise ValueError(f"product_code must be one of {sorted(ALLOWED_CODES)}")
    start = validate_date(start_date)
    end = validate_date(end_date)
    if start > end:
        raise ValueError("start_date must not be after end_date")
    return (
        f"device.device_report_product_code:{code} "
        f"AND date_received:[{start} TO {end}]"
    )


def build_url(product_code: str, start_date: str, end_date: str, limit: int) -> str:
    if not 1 <= limit <= 1000:
        raise ValueError("limit must be between 1 and 1000")
    params = {
        "search": build_search(product_code, start_date, end_date),
        "limit": str(limit),
    }
    return f"{API_ENDPOINT}?{urlencode(params)}"


def extract(product_code: str, start_date: str, end_date: str, limit: int, output_dir: Path) -> tuple[Path, Path]:
    code = product_code.upper()
    url = build_url(code, start_date, end_date, limit)
    request = Request(url, headers={"User-Agent": "clinical-data-portfolio/0.2"})
    with urlopen(request, timeout=60) as response:
        payload = response.read()

    parsed = json.loads(payload)
    returned = len(parsed.get("results", []))
    total = parsed.get("meta", {}).get("results", {}).get("total")
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"device_event_{code}_{start_date}_{end_date}_limit{limit}"
    raw_path = output_dir / f"{stem}.json"
    manifest_path = output_dir / f"{stem}.manifest.json"
    raw_path.write_bytes(payload)
    manifest = {
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint": API_ENDPOINT,
        "query_url_without_api_key": url,
        "product_code": code,
        "start_date": start_date,
        "end_date": end_date,
        "requested_limit": limit,
        "returned_records": returned,
        "total_matching_records_reported_by_api": total,
        "raw_file": raw_path.name,
        "raw_sha256": hashlib.sha256(payload).hexdigest(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return raw_path, manifest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a small openFDA Device Event API pilot.")
    parser.add_argument("--product-code", required=True, choices=sorted(ALLOWED_CODES))
    parser.add_argument("--start-date", default="20200101")
    parser.add_argument("--end-date", default="20251231")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raw, manifest = extract(
        args.product_code, args.start_date, args.end_date, args.limit, args.output_dir
    )
    print(f"Raw response: {raw}")
    print(f"Manifest: {manifest}")
