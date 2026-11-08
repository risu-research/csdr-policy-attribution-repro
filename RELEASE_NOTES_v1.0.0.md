# CSDR Sponsor-Policy Attribution Reproduction Package, v1.0.0

First public research reproducibility release for *When Trial Data Portals Move: What Remains Findable?* (BIBM 2026 poster P283).

## Contents and verified scope

- Exact Common Crawl WARC byte-range coordinates and expected SHA-256 hashes for 15 dated HTTP responses, plus their corresponding original sponsor-page URLs and capture times.
- A standalone Python workflow that downloads, verifies, parses, and compares those original archived captures; it fails on missing, altered, or unexpected input rather than silently replacing evidence.
- Reproduction of three source-policy whole-body matches: Lilly / Boehringer Ingelheim (27/27 HTML paragraphs), Bayer / Sanofi (25/25), and ONO / UCB (21/21).
- Six selected cross-sponsor negative-control comparisons without a complete policy-body match, plus historical self-policy controls.
- Frozen expected summary tables, documented original trial-route observations, unit tests, Windows and Unix runners, and a GitHub Actions remote verification workflow.

## Boundaries

The initial 14-trial routing study and the exploratory 19-page comparison are historical recorded observations; their complete original HTTP response sets were not independently preserved for byte-for-byte replay. The 15-record Common Crawl/WARC experiment **is** independently reproducible from the published archive coordinates. The selected cases and controls cannot estimate the overall frequency of policy misattribution or effects on actual data-access requests.

Third-party webpage/WARC payloads are **not redistributed** in the release archive. The repository includes code, original research metadata, source coordinates, expected hashes, and derived results. Software source is MIT licensed; applicable original research metadata is released under CC0 to the extent the author holds rights.

## Verification

On a clean machine with Python 3.10+ and network access to Common Crawl:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python reproduce.py all
python check_outputs.py
```

GitHub: https://github.com/risu-research/csdr-policy-attribution-repro
