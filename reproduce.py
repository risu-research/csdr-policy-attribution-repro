#!/usr/bin/env python3
"""Re-run recorded historical policy comparisons, starting only with public files."""
import argparse
from pathlib import Path
from src.repro import verify_all, records, obtain_capture, ROOT

def main():
    p=argparse.ArgumentParser(description='Retrieve and verify 15 exact Common Crawl WARC records (no APIs or account needed).')
    p.add_argument('command',choices=['all','fetch','verify','manifest'],help='all: download+reproduce; fetch: download-only; verify: offline cache; manifest: show provenance')
    p.add_argument('--cache-dir',type=Path,default=ROOT/'cache'/'warc',help='local untracked copy of third-party WARC records')
    p.add_argument('--output-dir',type=Path,default=ROOT/'results',help='generated results path')
    args=p.parse_args()
    if args.command=='manifest':
        for row in records():print(row['record_id'],row['cc_collection'],row['byte_offset'],row['byte_length'],row['expected_gzip_sha256'])
        return
    if args.command=='fetch':
        for row in records():
            _,state=obtain_capture(row,args.cache_dir,fetch=True)
            print('PASS',row['record_id'],state)
        return
    verify_all(args.cache_dir,args.output_dir,fetch=args.command=='all')

if __name__=='__main__':main()
