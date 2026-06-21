# event-study/src/preflight.py
"""
Pre-flight checks for the FOXA/ROKU event study.

Two jobs:
1. Nail the exact 8-K disclosure timestamp so we know whether day zero is
   June 15 (pre-market or intraday filing) or June 16 (after-hours filing).
2. Confound check: find any OTHER 8-Ks filed by FOXA or ROKU in the
   surrounding window that might contaminate our event window.

We use the SEC EDGAR submissions API, which returns an acceptanceDatetime
field — the exact second the filing hit EDGAR's system. That is the authoritative
timestamp, more reliable than news-wire timestamps which can lag by minutes.
"""

import requests
from datetime import date

EDGAR_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
HEADERS = {"User-Agent": "udayadityapatil.99@gmail.com"}


def get_8k_filings(cik: str, start: str, end: str) -> list[dict]:
    """
    Fetch 8-K filings for a company CIK within a date range.
    CIK must be zero-padded to 10 digits.
    Returns list of dicts with keys: accessionNumber, filingDate, reportDate,
    primaryDocument, and acceptanceDatetime (if available).
    """
    url = EDGAR_SUBMISSIONS.format(cik=cik.zfill(10))
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()

    filings = data["filings"]["recent"]
    available_fields = list(filings.keys())

    results = []
    for i, form in enumerate(filings["form"]):
        if form not in ("8-K", "8-K/A"):
            continue
        filed = filings["filingDate"][i]
        if start <= filed <= end:
            entry = {
                "form": form,
                "accessionNumber": filings["accessionNumber"][i],
                "filingDate": filed,
                "reportDate": filings["reportDate"][i],
                "primaryDocument": filings["primaryDocument"][i],
            }
            # acceptanceDateTime is the gold standard — exact second filed with SEC
            # Note: EDGAR JSON uses camelCase "acceptanceDateTime" (capital D, capital T)
            if "acceptanceDateTime" in available_fields:
                entry["acceptanceDateTime"] = filings["acceptanceDateTime"][i]
            results.append(entry)
    return results


def get_filing_index(accession_number: str, cik: str) -> dict:
    """
    Fetch the filing index JSON from EDGAR for a specific accession number.
    This sometimes contains additional metadata including the exact filing time.
    """
    acc_clean = accession_number.replace("-", "")
    cik_int = int(cik)
    index_url = (
        f"https://www.sec.gov/Archives/edgar/data/{cik_int}/"
        f"{acc_clean}/{accession_number}-index.htm"
    )
    resp = requests.get(index_url, headers=HEADERS)
    if resp.status_code == 404:
        return {"error": f"Index not found at {index_url}"}
    # Return first 2000 chars for inspection
    return {"url": index_url, "content": resp.text[:2000]}


def get_filing_header_timestamp(accession_number: str, cik: str) -> str:
    """
    Fetch the SGML header of an EDGAR filing to get the exact submission timestamp.
    The header contains ACCEPTANCE-DATETIME which gives the precise filing time.
    Returns raw header text (first 4000 chars) for inspection.
    """
    acc_clean = accession_number.replace("-", "")
    cik_int = int(cik)
    header_url = (
        f"https://www.sec.gov/Archives/edgar/data/{cik_int}/"
        f"{acc_clean}/{accession_number}.txt"
    )
    resp = requests.get(header_url, headers=HEADERS)
    if resp.status_code == 404:
        return f"Header not found at {header_url}"
    return resp.text[:4000]


def print_all_fields(cik: str, start: str, end: str, label: str):
    """Debug helper: print every field available for 8-K filings in range."""
    url = EDGAR_SUBMISSIONS.format(cik=cik.zfill(10))
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    filings = data["filings"]["recent"]

    print(f"\n=== {label}: all available fields in submissions JSON ===")
    print("Fields:", list(filings.keys()))

    for i, (form, filed) in enumerate(zip(filings["form"], filings["filingDate"])):
        if form not in ("8-K", "8-K/A"):
            continue
        if start <= filed <= end:
            print(f"\n  Filing #{i}: {form} filed {filed}")
            for field in filings.keys():
                print(f"    {field}: {filings[field][i]}")


if __name__ == "__main__":
    # -----------------------------------------------------------------------
    # CIKs (zero-padded to 10 digits per EDGAR convention)
    #   FOXA  : Fox Corporation         CIK 0001754301
    #   ROKU  : Roku, Inc.              CIK 0001428439
    # -----------------------------------------------------------------------
    FOXA_CIK = "1754301"
    ROKU_CIK  = "1428439"
    SEARCH_START = "2026-06-08"
    SEARCH_END   = "2026-06-22"

    # ------------------------------------------------------------------
    # Step 1: Pull all 8-K filings in the window for both tickers
    # ------------------------------------------------------------------
    print("=" * 70)
    print("STEP 1 — 8-K filings in June 8–22, 2026")
    print("=" * 70)

    print("\n--- FOXA 8-K filings ---")
    foxa_filings = get_8k_filings(FOXA_CIK, SEARCH_START, SEARCH_END)
    if not foxa_filings:
        print("  [None found in this window]")
    for f in foxa_filings:
        print(f"  {f}")

    print("\n--- ROKU 8-K filings ---")
    roku_filings = get_8k_filings(ROKU_CIK, SEARCH_START, SEARCH_END)
    if not roku_filings:
        print("  [None found in this window]")
    for f in roku_filings:
        print(f"  {f}")

    # ------------------------------------------------------------------
    # Step 2: Print every metadata field for any 8-K in range (debug)
    # ------------------------------------------------------------------
    print_all_fields(FOXA_CIK, SEARCH_START, SEARCH_END, "FOXA")
    print_all_fields(ROKU_CIK,  SEARCH_START, SEARCH_END, "ROKU")

    # ------------------------------------------------------------------
    # Step 3: Pull SGML header for each filing to get exact timestamps
    # The SGML header always contains:
    #   <ACCEPTANCE-DATETIME>YYYYMMDDHHMMSS
    # which is the authoritative filing time in Eastern time.
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 3 — Exact timestamps from SGML filing headers")
    print("=" * 70)

    for ticker, cik, filings in [
        ("FOXA", FOXA_CIK, foxa_filings),
        ("ROKU", ROKU_CIK, roku_filings),
    ]:
        for f in filings:
            print(f"\n{ticker} | accession: {f['accessionNumber']} | filed: {f['filingDate']}")
            header = get_filing_header_timestamp(f["accessionNumber"], cik)
            if header.startswith("Header not found"):
                print(f"  WARNING: {header}")
                continue
            # Print only lines that contain timing information
            timing_keywords = [
                "ACCEPTANCE", "FILED", "CONFORMED", "DATE", "TIME",
                "PERIOD", "REPORT", "DATETIME"
            ]
            printed = 0
            for line in header.split("\n"):
                if any(kw in line.upper() for kw in timing_keywords):
                    print(f"  {line.strip()}")
                    printed += 1
            if printed == 0:
                # Fallback: print first 20 lines raw
                print("  [No timing keywords found — raw header snippet:]")
                for line in header.split("\n")[:20]:
                    print(f"  {line}")

    # ------------------------------------------------------------------
    # Step 4: Broaden check — look at wider window for confounds
    # Check 30 days before the event for any FOXA or ROKU 8-Ks that
    # might have established a trend confound (e.g. restructuring news)
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 4 — Broader confound scan (May 15 – June 22, 2026)")
    print("=" * 70)

    for ticker, cik in [("FOXA", FOXA_CIK), ("ROKU", ROKU_CIK)]:
        url = EDGAR_SUBMISSIONS.format(cik=cik.zfill(10))
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        filings_data = data["filings"]["recent"]

        print(f"\n--- {ticker}: all SEC filings May 15 – June 22, 2026 ---")
        found_any = False
        for i, (form, filed) in enumerate(
            zip(filings_data["form"], filings_data["filingDate"])
        ):
            if "2026-05-15" <= filed <= "2026-06-22":
                found_any = True
                acc = filings_data["accessionNumber"][i]
                primary = filings_data["primaryDocument"][i]
                report = filings_data["reportDate"][i]
                print(f"  {filed} | {form:12s} | {acc} | report: {report} | doc: {primary}")
        if not found_any:
            print("  [No filings found in this broader window]")
