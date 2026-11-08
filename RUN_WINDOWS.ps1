$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (Get-Command py -ErrorAction SilentlyContinue) { $PY = 'py' ; $PYARG = @('-3') }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $PY = 'python' ; $PYARG = @() }
else { throw 'Python 3 is required (https://www.python.org/downloads/)' }
& $PY @PYARG -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
& $PY @PYARG -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Offline unit tests failed' }
& $PY @PYARG reproduce.py all
if ($LASTEXITCODE -ne 0) { throw 'Source re-verification failed; see error, do not cite a successful run' }
& $PY @PYARG check_outputs.py
if ($LASTEXITCODE -ne 0) { throw 'Frozen output comparison failed' }
Write-Host 'PASS: verified 15 Common Crawl originals. See results/summary.json'
