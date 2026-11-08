# CSDR sponsor-policy attribution: reproducibility package

**Reproducible research companion to:** *When Trial Data Portals Move: What Remains Findable?* (BIBM 2026, poster P283)  
**Author:** Moon Hwan Lee, RISU Institute  
**Package version:** `v1.0.0` (2026-11-08)

## What this package actually reproduces

A third party can retrieve **15 exact historical Common Crawl WARC response records**, verify each against recorded public archive coordinates and cryptographic hashes, re-extract sponsor-page HTML paragraphs, and reproduce the historical sponsor-policy comparisons without access to the author's files, browser, chats, or API credentials.

Expected findings, verified locally against 15 independently retained originals:

| Test | Expected result |
|---|---|
| Lilly (Aug. 2019) vs Boehringer Ingelheim (83 seconds later) | 27/27 paragraph policy-body identity |
| Bayer (Feb. 2023) vs Sanofi (647 seconds later) | 25/25 identity |
| ONO (Sep. 2024) vs UCB (Oct. 2024, ~31 days later) | 21/21 identity |
| Other-sponsor control comparisons selected for those cases | 0/6 whole-policy identities |
| Roche across three dated records | 19 paragraphs unchanged at sampled dates |
| Boehringer Ingelheim across two dated records | 27 paragraphs unchanged at sampled dates |
| Bayer own 2020/2022 records vs 2023 later record | stable 16-paragraph earlier text; 0 paragraphs shared with 2023 changed text |

The case selection is **purposive**. Neither 3/3 nor 0/6 is a population prevalence or out-of-sample classifier accuracy estimate.

## Reproduce from a clean public download

Requires Python 3.10 or later (locally tested with Python 3.13; hosted CI uses 3.13), Internet access to **Common Crawl**, and approximately 180 KB of archive data. The historical web content is fetched at runtime, **not bundled** with this repository.

### Linux / macOS

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 reproduce.py all
python3 check_outputs.py
```

### Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_WINDOWS.ps1
```

Equivalent manual command after installing dependencies: `py -3 reproduce.py all`.

**Output:** `results/summary.json`, `results/comparisons.csv`, `results/record_provenance.csv`, `results/route_sponsor_counts.csv` (automatically generated, not manually edited). `check_outputs.py` then compares summary/comparison rows to `expected/` reference results. The 15 records are cached under `cache/warc/` and excluded from Git.

**Offline rerun after one successful download:**

```bash
python3 reproduce.py verify
```

**Inspect exact origin coordinates without downloading:**

```bash
python3 reproduce.py manifest
```

**If a capture is unavailable:** the program stops with a clear error. It will never substitute today's live webpage, a nearest Wayback snapshot, an alternative capture or a precomputed result. If an existing cached file has the wrong hash, it fails rather than silently replacing it.

## What each file is for

| Path | Purpose |
|---|---|
| `data/captures.csv` | 15 exact Common Crawl filenames, byte offsets/lengths, URL, UTC, expected hashes |
| `src/repro.py`, `reproduce.py` | archival range requests, WARC/HTTP/HTML parsing, comparisons, checks |
| `data/exploratory_route_14.csv` | preserved October 28, 2026 exploratory observations of 14 registered trials |
| `data/exploratory_route_5_sponsors.csv` | contemporary five-sponsor routing summary; historical observation, not raw-response reproduction |
| `data/historical_wayback_leads.csv` | chronological Wayback evidence *pointers*, not independent byte-verifiable raw records |
| `tests/` | synthetic independent parser and corrupt-input failure tests |
| `.github/workflows/` | local/CI unit tests and optional manual full remote re-verification |
| `docs/CLAIM_EVIDENCE_MAP.md` | which manuscript claims can/cannot be re-run from this repo |
| `docs/INDEPENDENT_ORIGIN_CHECK.md` | manual curl origin-range verification without trusting the Python downloader |
| `expected/` + `check_outputs.py` | public frozen expected results and deterministic comparison |
| `docs/PUBLISHING_GUIDE_KO.md` | Korean guide for GitHub, Zenodo and RISU release |

## Distinguish three datasets

1. **14 individual trial records from five companies**: a 2026-10-28 retrospective route inspection. This package publishes the anonymization-free, public-URL observation ledger; the original HTTP captures of the 2026 routes were **not retained in full**. Re-counting the ledger reproduces its recorded labels, not the historical server state independently.
2. **19 chosen CSDR sponsor pages, 171 browser-based pairwise checks**: an earlier exploratory comparison. The complete original browser-extracted HTML set was **not saved as immutable responses**, so this historical comparison cannot be reconstructed independently exactly from this package. The derived observations are contextual only; do not claim independent reproduction.
3. **15 original WARC captures from nine sponsor-page identities (11 literal target URLs, including `www` variants)**: the **fully re-executable primary evidence set**. The 15 exact ranges and known hashes allow fresh independent recovery and verification while available from Common Crawl.

The previously reported Lilly and ONO pre-transition *own-sponsor* pages are anchored by Internet Archive links in `historical_wayback_leads.csv`. They are not represented as original WARC files among these 15 verified captures. Their exact historical body-level comparison is a **separate limitation**, not silently claimed as reproduced.

## Research and redistribution boundaries

* We do not include third-party CSDR web-page text or full WARC records. Original site owners may retain copyright; the Common Crawl Terms of Use acknowledge third-party rights. Researchers download the source material themselves and follow applicable rules.
* `data/captures.csv` contains original metadata and hashes, not patient-level trial datasets, actual trial patient information, applicant records, server credentials, internal research logs or proprietary project files.
* No identifiable trial participant data were analyzed or are distributed.
* No submitted application, denial, applicant harm, underlying source-code fault or site-wide error incidence is inferred.
* **External availability is a condition**: if Common Crawl eventually removes a WARC object or changes delivery, hash-locked verification cannot succeed from a fresh download. A successful offline test does not imply a live origin was accessed.
* The source-author comparisons are not a blind holdout, and several controls and the ONO/UCB pair were not captured on the same date.

## Academic citation and versioning

Use `CITATION.cff` to credit the software and metadata. Once this repository has a public release and Zenodo has minted a DOI, cite the **version-specific** DOI in the manuscript. Do not paste placeholder URLs or DOIs into the paper.

**Licensing:** MIT license applies to original code only; original metadata tables are released under CC0-1.0 (`LICENSE-DATA`). Third-party CSDR page content remains subject to its owners' rights.

See `docs/RUNBOOK_KO.md` for a Korean walkthrough and `docs/CLAIM_EVIDENCE_MAP.md` for the evidence boundaries.
