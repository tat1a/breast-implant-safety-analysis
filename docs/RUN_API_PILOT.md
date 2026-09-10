# Reproducing the API Pilot

## Learning objectives

After this exercise, the project owner should be able to:

1. Explain why FTR and FWM are the primary product codes.
2. Explain why `date_received` is used for the cohort window.
3. Run automated query-builder tests and interpret pass/fail output.
4. retrieve a deliberately small API sample without changing raw data manually.
5. Distinguish report-level, device-level, patient-level, and narrative structures.
6. Explain why API totals are not patient counts or complication incidence.
7. Verify a raw file with its SHA-256 checksum and extraction manifest.

## Windows and VS Code procedure

1. Install Python 3.10+ and Git, then install Visual Studio Code with the Microsoft Python extension.
2. Extract the project ZIP to a stable folder such as `D:\Projects\breast-implant-safety-portfolio`.
3. In VS Code, choose **File → Open Folder** and select the repository folder—not its parent.
4. Open **Terminal → New Terminal** and confirm:

   ```powershell
   py --version
   git --version
   ```

5. Create a local environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\python.exe --version
   ```

   Directly calling the environment's Python works even if PowerShell activation is restricted.

6. Run the offline unit tests:

   ```powershell
   .\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
   ```

   Success criterion: five tests end with `OK`. The explicit `-t .` sets the
   repository root as the import root and is compatible with Python 3.14's
   stricter test discovery behavior.

7. Run two small live API requests:

   ```powershell
   .\.venv\Scripts\python.exe src\openfda_client.py --product-code FTR --limit 5
   .\.venv\Scripts\python.exe src\openfda_client.py --product-code FWM --limit 5
   ```

   Success criterion: each command prints a raw-response path and a manifest path.

8. Inspect `data/raw/` in VS Code. Open the two `.manifest.json` files first. Do not edit the raw `.json` responses.
9. Read `docs/API_FIELD_MAPPING.md` and locate one example each of a report, a nested device, a nested patient, and a narrative block in a raw sample.
10. Do not stage or upload anything in `data/raw/`. Confirm with `git status` that these files are absent from the change list.

## What each control accomplishes

| Control | Purpose | Evidence of completion |
|---|---|---|
| Virtual environment | Keeps this project's Python setup isolated and reproducible | `.venv` Python prints its version |
| Unit tests | Detect malformed dates, wrong product codes, and unsafe API limits before download | Five tests pass |
| Five-record limit | Learns the schema without a large or accidental extraction | Exactly five returned records per query |
| Raw-file immutability | Preserves source evidence and prevents undocumented manual changes | Raw hash matches its manifest |
| Extraction manifest | Records when, how, and from which query data were obtained | Manifest contains query, time, count, and SHA-256 |
| Separate entity levels | Prevents one report with multiple devices/patients from inflating counts | Report/device/patient fields can be identified separately |
| Git exclusion | Prevents sensitive narratives and bulky source data from entering a public repository | `git status` omits `data/raw` files |

## Written checkpoint

Before full extraction, write short answers in your own words:

1. What does the FTR/FWM API `total` count represent?
2. Why can it not answer “what percentage of implanted patients had rupture?”
3. What is the difference between `date_received` and the clinical event date?
4. Why should device arrays not be flattened into the report table without a key?
5. What would you do if `patient_age` is blank or recorded in different units?
6. Why is `report_source_code` alone insufficient for mandatory/voluntary classification?

These answers are part of the analyst training record; they are not a memory test. Use the orientation and mapping documents while answering.
