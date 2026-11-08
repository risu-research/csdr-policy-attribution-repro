import base64
import gzip
import hashlib
import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from email.message import Message
from unittest.mock import patch

from src.repro import (records,checked_range,capture_path,sha256,sha1_b32,parse_warc,
    request_range,obtain_capture,read_csv)

class StubResponse:
    def __init__(self,status,content_range,body):
        self.status=status
        self.headers=Message()
        self.headers['Content-Range']=content_range
        self.stream=io.BytesIO(body)
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n=-1):return self.stream.read(n)

class ReproductionTests(unittest.TestCase):
    def test_manifest_counts_and_coordinates(self):
        rows=records()
        self.assertEqual(len(rows),15)
        self.assertEqual(len(set(r['sponsor'] for r in rows)),9)
        self.assertTrue(all(int(r['byte_length'])>0 and len(r['expected_gzip_sha256'])==64 for r in rows))
        for row in rows:
            url,offset,length=checked_range(row)
            self.assertTrue(url.startswith('https://data.commoncrawl.org/crawl-data/'))
            self.assertGreaterEqual(offset,0)
            self.assertLessEqual(length,1000000)
    def test_range_requires_206_and_exact_bounds(self):
        row=records()[0]
        _,o,n=checked_range(row)
        body=b'x'*n
        response=lambda status,cr:lambda req,timeout:StubResponse(status,cr,body)
        with self.assertRaisesRegex(ValueError,'HTTP 206'):
            request_range(row,opener=response(200,f'bytes {o}-{o+n-1}/1000000'))
        with self.assertRaisesRegex(ValueError,'Content-Range'):
            request_range(row,opener=response(206,f'bytes {o+1}-{o+n}/1000000'))
        with self.assertRaisesRegex(ValueError,'SHA-256'):
            request_range(row,opener=response(206,f'bytes {o}-{o+n-1}/1000000000'))
    def test_untrusted_manifest_path_rejected(self):
        row=dict(records()[0]);row['cc_warc_path']='../../internal.txt'
        with self.assertRaises(AssertionError):checked_range(row)
    def test_corrupted_existing_cache_fails_closed(self):
        row=records()[0]
        with TemporaryDirectory() as d:
            dest=capture_path(d,row);dest.write_bytes(b'corrupted')
            with self.assertRaisesRegex(ValueError,'Corrupt cached capture'):
                obtain_capture(row,d,fetch=False)
    def test_synthetic_warc_digests_and_policy_extract(self):
        html=b'<html><p>Example is no longer accepting data sharing requests.</p><p>A <b>Trial</b> clause.</p><p>Second clause.</p></html>'
        http=b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'+html
        ts='2023-01-01T00:00:00Z';url='https://example.org/policy'
        head=(f'WARC/1.0\r\nWARC-Type: response\r\nWARC-Date: {ts}\r\nWARC-Target-URI: {url}\r\n'
              f'Content-Length: {len(http)}\r\nWARC-Block-Digest: sha1:{sha1_b32(http)}\r\n'
              f'WARC-Payload-Digest: sha1:{sha1_b32(html)}\r\n\r\n').encode()
        stream=gzip.compress(head+http+b'\r\n\r\n',mtime=0)
        policy=['a trial clause.','second clause.']
        row=dict(expected_gzip_sha256=sha256(stream),capture_utc=ts,target_url=url,record_id='synthetic',
            expected_notice='true',expected_paragraphs='2',expected_cc_payload_digest_b32=sha1_b32(html),
            expected_policy_sha256=sha256('\n'.join(policy).encode()))
        got=parse_warc(row,stream)
        self.assertEqual(got['normalized_paragraphs'],policy)
        self.assertEqual(len(got['raw_paragraphs']),2)
        row['expected_policy_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Ordered policy digest'):parse_warc(row,stream)
        row['expected_policy_sha256']=sha256('\n'.join(policy).encode())
        row['expected_cc_payload_digest_b32']='BAD'
        with self.assertRaisesRegex(ValueError,'index payload digest'):parse_warc(row,stream)
    def test_exploratory_route_counts_distinct(self):
        rows=read_csv(Path(__file__).resolve().parents[1]/'data'/'exploratory_route_14.csv')
        self.assertEqual(len(rows),14)
        self.assertEqual(len(set(r['nct_id'] for r in rows)),14)

if __name__=='__main__': unittest.main()
