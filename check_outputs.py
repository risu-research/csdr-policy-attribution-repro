#!/usr/bin/env python3
"""Compare regenerated summary/comparisons to the frozen public expected outputs."""
from pathlib import Path
import csv
import json
import sys

BASE=Path(__file__).resolve().parent

def load_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def main():
    out=BASE/'results'
    want=json.loads((BASE/'expected/summary.json').read_text(encoding='utf-8'))
    got=json.loads((out/'summary.json').read_text(encoding='utf-8'))
    if want != got:raise AssertionError('Summary differs from public expected result')
    if load_csv(BASE/'expected/comparisons.csv')!=load_csv(out/'comparisons.csv'):
        raise AssertionError('Comparison rows differ from expected original policy results')
    print('PASS: independently regenerated results match frozen public reference output')

if __name__=='__main__':main()
