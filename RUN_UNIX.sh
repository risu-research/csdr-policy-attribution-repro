#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 reproduce.py all
python3 check_outputs.py
printf 'PASS: output saved to results/summary.json\n'
