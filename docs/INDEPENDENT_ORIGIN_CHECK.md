# Verify a record independently of the bundled Python downloader

This file describes an alternative verification method using **curl**, which is useful for checking the range downloader itself.

For the **Sanofi policy capture at 2023-02-01 19:13:24 UTC**, the public Common Crawl coordinates (see `data/captures.csv`) are:

- Collection: `CC-MAIN-2023-06`
- WARC file path: `crawl-data/CC-MAIN-2023-06/segments/1674764499949.24/warc/CC-MAIN-20230201180036-20230201210036-00811.warc.gz`
- Start: `193866021`
- Compressed record length: `11174` bytes
- End: `193877194` inclusive
- Expected compressed SHA-256: `3d31c1f8cdedcd8d57fb06b7998d6b6d75f2d29f5a371947f371595f66c750e2`

With curl, independently download those exact bytes:

```bash
curl --fail --silent --show-error --location \
  --header 'Range: bytes=193866021-193877194' \
  'https://data.commoncrawl.org/crawl-data/CC-MAIN-2023-06/segments/1674764499949.24/warc/CC-MAIN-20230201180036-20230201210036-00811.warc.gz' \
  --output sanofi_original_record.warc.gz
sha256sum sanofi_original_record.warc.gz
```

The SHA-256 must match **exactly**. If the server returns an unbounded full WARC object, the size or hash check will fail. The archive's public URL describes the source; it is **not a claim that the paper's author owns or licenses the page content**.

For byte-level checks of the rest of the dataset, use one range in `data/captures.csv` per file. The script enforces HTTP status 206 and an exact `Content-Range` header as well as the SHA-256 checks. Cross-check the original WARC `WARC-Target-URI`, `WARC-Date`, `WARC-Block-Digest`, `WARC-Payload-Digest`, and normalized policy digest using `src/repro.py` or a separately implemented parser.

Reference: [Common Crawl documentation, CDXJ byte ranges](https://commoncrawl.org/cdxj-index).
