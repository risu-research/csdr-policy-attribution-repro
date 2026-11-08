"""Public GitHub Release + Zenodo DOI check. Read only until status JSON is saved."""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

repo = "risu-research/csdr-policy-attribution-repro"
status = {
    "repository": f"https://github.com/{repo}",
    "tag": "v1.0.0",
    "github_release": {"status": "not_checked"},
    "zenodo": {"status": "not_verified", "doi": None},
    "note": "A missing public search hit is not proof that Zenodo did not create a record.",
}

def request_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "RISU-DOI-Audit/1.0"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))

token = os.environ["GITHUB_TOKEN"]
try:
    release = request_json(
        f"https://api.github.com/repos/{repo}/releases/tags/v1.0.0",
        {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": "RISU-DOI-Audit/1.0"},
    )
    status["github_release"] = {
        "status": "published" if not release.get("draft") and release.get("published_at") else "not_published",
        "url": release.get("html_url"),
        "published_at": release.get("published_at"),
        "tag": release.get("tag_name"),
        "prerelease": release.get("prerelease"),
    }
except Exception as exc:
    status["github_release"] = {"status": "query_failed", "error": str(exc)[:220]}

searches = ['metadata.title:"When Trial Data Portals Move"', 'metadata.title:"CSDR Sponsor-Policy"','"CSDR" "Sponsor-Policy"']
hits = {}
errors = []
for query in searches:
    try:
        url = "https://zenodo.org/api/records/?" + urllib.parse.urlencode({"q":query,"size":25,"sort":"mostrecent"})
        result = request_json(url)
        for item in result.get("hits",{}).get("hits",[]):
            hits[str(item.get("id"))] = item
    except Exception as exc:
        errors.append(str(exc)[:190])

candidates = []
for item in hits.values():
    m=item.get("metadata") or {}
    title=str(m.get("title") or "")
    title_l=title.lower()
    related=m.get("related_identifiers") or []
    identifiers=" ".join(str(r.get("identifier","")) for r in related if isinstance(r,dict))
    repo_match=(repo.lower() in identifiers.lower())
    title_match=("when trial data portals move" in title_l and "csdr" in title_l)
    if not (repo_match or title_match):
        continue
    version=str(m.get("version") or "")
    if version and version not in ("1.0.0","v1.0.0"):
        continue
    doi=item.get("doi") or ((item.get("pids") or {}).get("doi") or {}).get("identifier")
    if not doi:
        continue
    candidates.append({"id":item.get("id"),"title":title,"version":version,"doi":doi,"record_url":f"https://zenodo.org/records/{item.get('id')}"})
if len(candidates)==1:
    status["zenodo"]={"status":"published_verified","doi":candidates[0]["doi"],"url":candidates[0]["record_url"],"record_id":candidates[0]["id"],"title":candidates[0]["title"],"version":candidates[0]["version"]}
elif len(candidates)>1:
    status["zenodo"]={"status":"ambiguous_multiple_records","candidates":candidates}
else:
    status["zenodo"]={"status":"not_found_in_public_search","search_errors":errors[:3],"matching_results":0}

path=Path("docs/ZENODO_RELEASE_STATUS_v1.0.0.json")
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(status,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(status,indent=2,ensure_ascii=False))
