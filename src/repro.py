"""Reproduce CSDR archived sponsor-policy comparisons from original Common Crawl ranges.

Only Python stdlib for downloading/WARC integrity; bs4 4.14.3 for original
paragraph parser. No private data, service keys, browser extensions, or models.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
import base64
import csv
import gzip
import hashlib
import json
import re
import sys
import unicodedata
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / 'data' / 'captures.csv'
USER_AGENT = 'csdr-reproducibility/1.0 (academic re-verification; https://commoncrawl.org/get-started)'


def read_csv(path):
    with Path(path).open('r', encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def sha1_b32(data):
    return base64.b32encode(hashlib.sha1(data).digest()).decode('ascii').rstrip('=')


def records():
    items = read_csv(CAPTURES)
    assert len(items) == 15, f'Expected 15 captures, found {len(items)}'
    assert len({r['record_id'] for r in items}) == 15
    assert len({(r['sponsor'], r['capture_utc']) for r in items}) == 15
    return items


def capture_path(cache_dir, row):
    name = row['record_id']
    assert re.fullmatch(r'[A-Za-z0-9_]+', name), 'Unexpected record id'
    return Path(cache_dir) / (name + '.warc.gz')


def checked_range(row):
    name = row['cc_warc_path']
    assert name.startswith('crawl-data/CC-MAIN-')
    assert re.fullmatch(r'[A-Za-z0-9_./-]+', name) and '..' not in name
    offset, length = int(row['byte_offset']), int(row['byte_length'])
    assert offset >= 0 and 100 <= length <= 1_000_000
    url = 'https://data.commoncrawl.org/' + name
    return url, offset, length


def request_range(row, opener=urllib.request.urlopen):
    url, offset, length = checked_range(row)
    ending = offset + length - 1
    headers = {
        'Range': f'bytes={offset}-{ending}',
        'Accept-Encoding': 'identity',
        'User-Agent': USER_AGENT,
    }
    req = urllib.request.Request(url, headers=headers, method='GET')
    with opener(req, timeout=60) as response:
        status = response.status
        if status != 206:
            raise ValueError(f'Expected HTTP 206 for {row["record_id"]}; got {status}')
        content_range = response.headers.get('Content-Range', '')
        match = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+|\*)', content_range.strip())
        if not match or (int(match.group(1)),int(match.group(2))) != (offset, ending):
            raise ValueError(f'Incorrect Content-Range: {content_range!r}')
        data = response.read(length + 1)
    if len(data) != length:
        raise ValueError(f'Byte range length mismatch for {row["record_id"]}: {len(data)}/{length}')
    if sha256(data) != row['expected_gzip_sha256']:
        raise ValueError(f'Original WARC SHA-256 mismatch: {row["record_id"]}')
    return data


def obtain_capture(row, cache_dir, fetch=False, opener=urllib.request.urlopen):
    dest = capture_path(cache_dir, row)
    if dest.exists():
        buf = dest.read_bytes()
        if len(buf) != int(row['byte_length']) or sha256(buf) != row['expected_gzip_sha256']:
            raise ValueError(f'Corrupt cached capture {dest}; remove manually before rerunning')
        return buf, 'cache-verified'
    if not fetch:
        raise FileNotFoundError(f'Missing {dest}; run `python reproduce.py all` to download from Common Crawl')
    buf = request_range(row, opener=opener)
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = dest.with_suffix(dest.suffix + '.part')
    temp.write_bytes(buf)
    temp.replace(dest)
    return buf, 'downloaded-and-verified'


def header_map(header_bytes):
    out = {}
    for line in header_bytes.split(b'\r\n')[1:]:
        if b': ' in line:
            key, value = line.split(b': ', 1)
            out[key.decode('latin1').lower()] = value.decode('latin1')
    return out


def parse_warc(row, gzip_bytes):
    """Fail closed on gzip, WARC, HTTP and policy digest disagreements."""
    if sha256(gzip_bytes) != row['expected_gzip_sha256']:
        raise ValueError('Stored gzip hash mismatch')
    decompressed = gzip.decompress(gzip_bytes)
    if len(decompressed) > 2_000_000:
        raise ValueError('WARC record exceeds expected maximum')
    warc_head, remainder = decompressed.split(b'\r\n\r\n', 1)
    wh = header_map(warc_head)
    if wh.get('warc-type') != 'response':
        raise ValueError('Not a WARC response record')
    if wh.get('warc-date') != row['capture_utc']:
        raise ValueError('WARC capture timestamp differs')
    if wh.get('warc-target-uri') != row['target_url']:
        raise ValueError('WARC target URI differs')
    total = int(wh['content-length'])
    if total <= 0 or total > len(remainder):
        raise ValueError('Invalid WARC Content-Length')
    record_body = remainder[:total]
    if sha1_b32(record_body) != wh['warc-block-digest'].split(':',1)[1]:
        raise ValueError('WARC block SHA-1 mismatch')
    response_head, payload = record_body.split(b'\r\n\r\n', 1)
    if not response_head.startswith(b'HTTP/1.1 200'):
        raise ValueError('HTTP response is not 200')
    if sha1_b32(payload) != wh['warc-payload-digest'].split(':',1)[1]:
        raise ValueError('WARC payload SHA-1 mismatch')
    if sha1_b32(payload) != row['expected_cc_payload_digest_b32']:
        raise ValueError('Common Crawl index payload digest disagreement')
    # Original author's extraction: BeautifulSoup(html.parser) over text p elements.
    # A replacement decoder/parser must be declared a new analysis version.
    from bs4 import BeautifulSoup
    paragraph_texts = [p.get_text(' ', strip=True) for p in BeautifulSoup(payload.decode('utf-8', errors='replace'), 'html.parser').find_all('p')]
    if not paragraph_texts:
        raise ValueError('No HTML p elements')
    has_notice = 'no longer accepting data sharing requests' in paragraph_texts[0].casefold()
    if has_notice != (row['expected_notice'] == 'true'):
        raise ValueError('Sponsor notice classification changed')
    raw_p = paragraph_texts[1:] if has_notice else paragraph_texts
    if len(raw_p) != int(row['expected_paragraphs']):
        raise ValueError(f'Paragraph count disagreement: {row["record_id"]}')
    norm_p = [unicodedata.normalize('NFC',' '.join(p.split())).casefold() for p in raw_p]
    if sha256('\n'.join(norm_p).encode('utf-8')) != row['expected_policy_sha256']:
        raise ValueError(f'Ordered policy digest disagreement: {row["record_id"]}')
    return {
        'raw_paragraphs': raw_p,
        'normalized_paragraphs': norm_p,
        'notice_present': has_notice,
        'policy_sha256': sha256('\n'.join(norm_p).encode('utf-8')),
    }

# A priori comparison specification: three matched donor policies, six other
# purposive comparator pages. Different-date controls are explicitly labelled.
COMPARE = [
    ('source', 'Lilly_20190819004537', 'Boehringer_Ingelheim_20190819004700'),
    ('other', 'Lilly_20190819004537', 'Roche_20190724094800'),
    ('source', 'Bayer_20230201190237', 'Sanofi_20230201191324'),
    ('other', 'Bayer_20230201190237', 'Boehringer_Ingelheim_20230201185708'),
    ('other', 'Bayer_20230201190237', 'Takeda_20230201185038'),
    ('other', 'Bayer_20230201190237', 'Roche_20230208004914'),
    ('source', 'ONO_20240914114855', 'UCB_20241015150157'),
    ('other', 'ONO_20240914114855', 'Roche_20240914112311'),
    ('other', 'ONO_20240914114855', 'GSK_20240914114012'),
]

STABILITY = [
    ('Roche_20190724094800','Roche_20230208004914'),
    ('Roche_20190724094800','Roche_20240914112311'),
    ('Boehringer_Ingelheim_20190819004700','Boehringer_Ingelheim_20230201185708'),
    ('Bayer_CC_2020_11_27','Bayer_CC_2022_11_27'),
    ('Bayer_20230201190237','Bayer_CC_2023_02_08'),
]


def verify_all(cache_dir, output_dir, fetch=False, opener=urllib.request.urlopen):
    all_records=records()
    parsed={}
    provenance=[]
    for row in all_records:
        gzip_bytes, status=obtain_capture(row, cache_dir, fetch=fetch, opener=opener)
        parsed[row['record_id']]=parse_warc(row, gzip_bytes)
        provenance.append({
            'record_id':row['record_id'], 'capture_utc':row['capture_utc'],
            'original_sha256':sha256(gzip_bytes), 'ordered_policy_sha256':parsed[row['record_id']]['policy_sha256'],
            'paragraphs':len(parsed[row['record_id']]['raw_paragraphs']),
            'provenance':status,
        })
        print('PASS',row['record_id'],status)
    comparisons=[]
    for role,a,b in COMPARE:
        pa=parsed[a]['raw_paragraphs'];pb=parsed[b]['raw_paragraphs']
        shared=sum((Counter(pa) & Counter(pb)).values())
        full_equal=pa==pb
        if role=='source' and not full_equal:
            raise AssertionError(f'Expected policy-source identity absent: {a} / {b}')
        if role=='other' and full_equal:
            raise AssertionError(f'Unexpected full identity with other-source control: {a} / {b}')
        aa=next(x for x in all_records if x['record_id']==a)
        bb=next(x for x in all_records if x['record_id']==b)
        delta_seconds=int((datetime.fromisoformat(bb['capture_utc'].replace('Z','+00:00'))-datetime.fromisoformat(aa['capture_utc'].replace('Z','+00:00'))).total_seconds())
        comparisons.append({
            'role':role,'recipient':aa['sponsor'],'recipient_id':a,'comparator':bb['sponsor'],
            'comparator_id':b,'recipient_paragraphs':len(pa),'comparator_paragraphs':len(pb),
            'exact_paragraph_occurrence_overlap':shared,
            'full_body_identical_in_order':full_equal,
            'captures_delta_seconds':delta_seconds,
            'same_utc_calendar_day':aa['capture_utc'][:10]==bb['capture_utc'][:10],
        })
    for a,b in STABILITY:
        if parsed[a]['raw_paragraphs']!=parsed[b]['raw_paragraphs']:
            raise AssertionError(f'Longitudinal stability check differs: {a} / {b}')
    # Bayer's 2022 original and 2023 swapped policy share no complete exact paragraphs.
    b22=parsed['Bayer_CC_2022_11_27']['normalized_paragraphs']
    b23=parsed['Bayer_20230201190237']['normalized_paragraphs']
    no_overlap=len(set(b22)&set(b23))
    if no_overlap!=0:
        raise AssertionError('Bayer before-after paragraph overlap changed')
    orig_routes=read_csv(ROOT/'data'/'exploratory_route_14.csv')
    count_by_sponsor=Counter(r['sponsor_group'] for r in orig_routes)
    expected_routes={'AstraZeneca':5,'MSD':5,'GSK':2,'Roche':1,'Lilly':1}
    if dict(count_by_sponsor)!=expected_routes or len(set(r['nct_id'] for r in orig_routes))!=14:
        raise AssertionError('14-trial exploratory route ledger disagrees with published counts')
    sponsor_verdicts=read_csv(ROOT/'data'/'exploratory_route_5_sponsors.csv')
    if len(sponsor_verdicts)!=5:
        raise AssertionError('Five-sponsor legacy ledger invalid')
    summary={
        'dataset':'CSDR selected historical policy audit',
        'original_http_warc_responses_verified':len(parsed),
        'distinct_sponsor_page_identities':len(set(x['sponsor'] for x in all_records)),
        'distinct_literal_target_urls':len(set(x['target_url'] for x in all_records)),
        'policy_source_pairs_full_ordered_match':sum(c['full_body_identical_in_order'] for c in comparisons if c['role']=='source'),
        'policy_source_pairs_tested':sum(c['role']=='source' for c in comparisons),
        'selected_other_controls_full_ordered_match':sum(c['full_body_identical_in_order'] for c in comparisons if c['role']=='other'),
        'selected_other_controls_tested':sum(c['role']=='other' for c in comparisons),
        'stable_same_sponsor_state_pairs':len(STABILITY),
        'bayer_2022_2023_normalized_paragraph_overlap':no_overlap,
        'initial_route_records_in_preserved_ledger':len(orig_routes),
        'initial_route_group_counts':expected_routes,
        'historical_19_page_corpus_raw_complete':False,
        'prior_route_http_snapshots_complete':False,
        'warning':'Case-selected examples and controls; no prevalence, accuracy, applicant impact or causal inference.',
    }
    if summary['policy_source_pairs_full_ordered_match']!=3 or summary['selected_other_controls_full_ordered_match']!=0:
        raise AssertionError('Primary outcome differs from expected')
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    write_csv(out/'comparisons.csv',comparisons)
    write_csv(out/'record_provenance.csv',provenance)
    write_csv(out/'route_sponsor_counts.csv',[{'sponsor':s,'n_trial_records':n,'audit_status':'preserved_exploratory_2026_observation_not_archived_http_reverification'} for s,n in sorted(expected_routes.items())])
    print('RESULT: 15/15 WARC PASS; original donor pairs 3/3 full identity; other controls 0/6 full identity')
    print('RESULT:',out/'summary.json')
    return summary,comparisons


def write_csv(path, rows):
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
