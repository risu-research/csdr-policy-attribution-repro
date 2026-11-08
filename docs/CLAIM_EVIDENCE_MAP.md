# Claim-to-evidence map (BIBM V62)

| Paper claim | Primary basis | Reproduced by `python reproduce.py all`? | Exact limitation |
|---|---|---|---|
| 15 original WARC responses from nine sponsor-page identities (11 literal target URLs) | `data/captures.csv` + Common Crawl HTTP byte ranges | YES | Requires original archive objects online |
| Lilly displays BI policy in 2019 (27/27) | Lilly & BI 2019 original WARC records | YES | 83 sec apart, not the website's edit time |
| Bayer displays Sanofi policy in 2023 (25/25) | Bayer & Sanofi 2023-02-01 originals | YES | 647 sec apart, not a causal explanation |
| ONO displays UCB policy in 2024 (21/21) | ONO Sep 2024 & UCB Oct 2024 originals | YES | ~31 days apart, corroborated separately by Wayback Aug 2024 |
| 0/6 complete matches against purposive other-company controls | Six recorded recipient-control pairs | YES | Controls were selected after cases; not false-positive rate |
| Roche own policy 19 paragraphs unchanged | Roche 2019, 2023, 2024 originals | YES | Only at these three observed states |
| BI own policy 27 paragraphs unchanged | BI 2019 & 2023 originals | YES | Only at these two observed states |
| Bayer own policy in 2020 and 2022 | Bayer 2020 & 2022 original WARC | YES | Does not prove every day between captures |
| Bayer's transition occurred between two observations | 2022 WARC plus dated 2023 Wayback evidence pointer | PARTIAL | Original Jan. 27 Wayback body not independently byte-verified in this release |
| Lilly pre-transition text named Lilly | July 2019 Wayback pointer | NO (historical lead) | Earlier raw response not in the 15-WARC set |
| ONO pre-transition text named ONO | Feb. 2023 Wayback pointer | NO (historical lead) | Earlier raw response not in the 15-WARC set |
| 14 trial records / five sponsor handoffs | `data/exploratory_route_14.csv` and `data/exploratory_route_5_sponsors.csv` | COUNTS ONLY | Original Oct. 28, 2026 HTTP transactions not retained |
| 19 sponsor pages / 171 unordered comparison pairs | Exploratory browser inspection described in paper | NO | The 19 full original pages were not preserved immutably |
| Conditions apply to another sponsor | Identical actual pages + company names within policy | YES for textual attribution | Not an authorized claim about underlying legal rights or request adjudication |
| Effect on researcher requests | No applicant records used | NO | No measured applicant outcomes or causality |

`YES` means the actual historical source content is retrieved byte-for-byte, rehashed, reparsed and the result recomputed, not merely that a saved CSV agrees. The manuscript should accurately distinguish this reproducibility tier from exploratory evidence.

## Interpretation details

The 27/27, 25/25 and 21/21 values count parsed HTML `<p>` elements after removing the first retirement notice paragraph. Those are **HTML element counts, not 73 independent legal violations**. Each matched full policy is one page-level finding.

The six other-company controls compare **entire paragraph sequences**. The sample is fixed and intentionally chosen, not random, and the controls were selected after the three cases were recognized.
