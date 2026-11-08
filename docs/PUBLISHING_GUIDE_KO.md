# 공개 전략: GitHub + Zenodo + RISU

## 권장 구조

**GitHub는 작업의 원본 저장소, Zenodo는 인용 가능한 특정 버전, RISU는 연구 소개 페이지**로 운영한다. 동일 ZIP을 여러 곳에서 별개 작품처럼 발행하지 않는다.

1. GitHub에서 이름이 명확한 **새 public repo**를 만든다. 예: `csdr-policy-attribution-repro` (아직 실제로 생성된 주소가 아님).
2. 이 패키지의 최상위 `README.md`, `src`, `data`, `tests`, `.github`, `docs` 등 파일을 저장소 루트에 올린다. `cache/`와 `results/`는 업로드하지 않는다. `data/captures.csv`는 포함한다.
3. 공개 저장소에서 `Actions`의 `Unit tests`가 통과하는지 확인한다.
4. `Actions` → **Reverify public archive** → `Run workflow`로 빈 GitHub 실행 환경에서 15건 실제 아카이브 다운로드와 검증을 실행한다. 성공한 요약 JSON을 확인한다. 실패하면 DOI 발행을 서두르지 않고 오류를 고친 뒤 재검증한다.
5. Zenodo에서 GitHub로 로그인하고 GitHub 저장소 연동을 켠다. 그 다음 GitHub에서 `v1.0.0` Release를 만들면, Zenodo가 그 버전의 소스 아카이브를 받아 DOI를 등록한다. 새로운 GitHub repo에 이미 적용된 Zenodo 연동인지 먼저 확인한다.
6. Zenodo record의 저자·자료 유형·버전·원본 라이선스를 검토하고 **특정 버전 DOI**를 기록한다. GitHub에서 README와 `CITATION.cff`에 그 DOI를 반영하려면 다음 소스 버전의 갱신과 Zenodo 스냅샷 시점을 구분한다. 별도 DOI로 같은 파일을 중복 등록하지 않는다.
7. RISU 사이트에는 논문 제목, 간단한 그림 없는 설명, 실제 GitHub 주소와 Zenodo DOI만 링크한다. RISU 사이트는 별도 원본 아카이브 저장소일 필요가 없다.
8. 논문 Methods에는 **검증된 실제 Zenodo 버전 DOI**만 추가한다. DOI 발급 전에는 가상의 링크나 임시 DOI를 쓰지 않는다.

## 법적 경계

- 배포 대상: 소스코드 (MIT), 연구자가 만든 원본 메타데이터/수치 표 (CC0-1.0), 실행 테스트, 좌표와 해시.
- **배포 제외:** 과거 CSDR 원문 WARC 15건 및 제약사 정책 본문 전체, 내부 로그·다운로드 원본·대화·작업 공간의 임시 파일.
- Zenodo/GitHub 라이선스 선택 시 자료 유형이 혼합돼 있음에 유의하고 `LICENSE`와 `LICENSE-DATA` 및 README에 적용 범위를 명시한다.
- Archive 원문을 재배포해야 하는 별도 연구 목적이 생기면 원 사이트 라이선스·이용약관 검토 후 별도 결정한다.

## 이 패키지가 '완전 재현'을 주장할 수 있는 범위

실제 **15개 원본 HTTP/WARC**의 무결성 검증과 3개 출처 전체 일치, 6개 정상 대조, Bayer·Roche·BI 내부 시점 비교는 데이터 접근이 가능한 한 제3자가 실행할 수 있다. 기존의 19개 브라우저 비교 원본 전체와 2026년 14개 경로의 이전 HTTP 반응은 보존되어 있지 않아 동일 강도로 독립 재현할 수 없다. 학술적으로는 이 구분을 공개하는 것이 정확하고 신뢰할 만하다.
