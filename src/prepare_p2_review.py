"""Split the frequency-ranked P2 taxonomy queue into auditable review batches."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def prepare(queue_path: Path, output_dir: Path, batch_size: int = 25) -> Path:
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")

    p2_rows = [row for row in read_csv(queue_path) if row["priority"] == "P2"]
    p2_rows.sort(key=lambda row: (-int(row["report_count"]), row["source_field"], row["raw_label"]))

    output_dir.mkdir(parents=True, exist_ok=True)
    output_fields = [
        "review_order", "batch_id", "source_field", "taxonomy_source_field",
        "raw_label", "report_count", "pct_of_reports", "proposed_category",
        "proposed_clinical_domain", "proposed_specificity", "proposed_analysis_role",
        "decision", "review_notes",
    ]

    for index, row in enumerate(p2_rows, start=1):
        row["review_order"] = index
        row["batch_id"] = f"P2-{((index - 1) // batch_size) + 1:02d}"
        row["proposed_analysis_role"] = ""

    packet_path = output_dir / "p2_review_packet.csv"
    with packet_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(p2_rows)

    summary = {
        "source_queue": str(queue_path),
        "priority": "P2",
        "labels": len(p2_rows),
        "batch_size": batch_size,
        "batches": max((len(p2_rows) + batch_size - 1) // batch_size, 0),
        "label_report_links": sum(int(row["report_count"]) for row in p2_rows),
        "qc_gate_passed": all(row["decision"] == "pending_review" for row in p2_rows),
        "warning": "Counts are label-report links, not unique patients, devices, or adverse-event incidence.",
    }
    summary_path = output_dir / "p2_review_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare frequency-ranked P2 taxonomy review batches.")
    parser.add_argument(
        "--queue",
        type=Path,
        default=Path("data/processed/taxonomy_review_v2/taxonomy_review_queue.csv"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/taxonomy_p2_review"))
    parser.add_argument("--batch-size", type=int, default=25)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"P2 review: {prepare(args.queue, args.output_dir, args.batch_size)}")
