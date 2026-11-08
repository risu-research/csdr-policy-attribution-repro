# 누구나 독립적으로 실행하는 방법

## 공개 저장소에 포함할 것

공개 ZIP에는 9개 기관 페이지 식별자(실제 URL 변형 11개)를 포괄하는 15건의 원본 URL·UTC·Common Crawl 아카이브 위치·바이트 오프셋·길이·SHA-256·단락 SHA-256, 수집 및 검증 코드, 단위 테스트, 초기 탐색 기록의 공개용 축약 표만 포함된다. CSDR 원문 WARC는 저장소에 동봉하지 않는다.

1. GitHub의 공개 저장소에서 이 파일들을 내려받거나 ZIP을 푼다.
2. Python 3.10+ 설치 후 `python -m pip install -r requirements.txt`를 실행한다.
3. `python -m unittest discover -s tests -v`를 실행한다. 여기는 외부 인터넷이 필요 없다.
4. `python reproduce.py all`로 실제 공개 Common Crawl 원본 15건을 바이트 범위별로 내려받는다. **일반적인 HTML 링크 탐색을 다시 수행하지 않는다.** 정확한 원본 위치가 이미 메타데이터에 고정돼 있다.
5. 정상일 때 `results/summary.json`, `results/comparisons.csv`, `results/record_provenance.csv`가 생성된다. 전체 정책은 결과 파일에 복제하지 않는다.
6. Windows에서는 압축을 풀고 PowerShell에서 `powershell -ExecutionPolicy Bypass -File .\RUN_WINDOWS.ps1` 한 줄로 위 단계를 실행할 수 있다.

인터넷 접근이 불가능하면 다른 컴퓨터나 GitHub Actions의 수동 `Reverify public archive` 작업을 사용한다. 실패한 실행은 성공으로 간주하지 않는다. 결과 해시가 다르면 당일 웹사이트의 새 HTML을 대신 쓰면 안 된다.

## 예상 결과

- 실제 WARC 15/15 건 무결성 검증
- Lilly–BI: 원본 정책 27/27 단락 같은 순서
- Bayer–Sanofi: 25/25, 동일 날짜 647초 간격
- ONO–UCB: 21/21, **31일 차이**
- 선정한 별도 비교 6개: 전체 본문 일치 0/6
- Roche 2019/2023/2024와 BI 2019/2023의 정책 동일성
- Bayer 2020·2022 원래 본문 16개 단락; 2023년 다른 본문과 정확히 같은 단락 0개

## 정밀한 연구 경계

이 패키지는 **핵심 15건 WARC 실험**을 원본까지 독립 재현하도록 설계했다. 그러나 과거 14건의 경로 판단과 19개 HTML 페이지(171쌍)는 해당 시기의 모든 원본 HTTP가 보존되지 않았다. 초기 관찰 CSV를 배포해도 2026년의 실제 서버 상태까지 재현했다는 뜻은 아니다. Wayback의 Lilly/ONO 이전 상태도 원본 WARC 검증 완료 자료와 구별했다.

## 안전·저작권

공개 코드는 자체 작성한 것이며, 원래 제약사 페이지 전체를 저장소에 재배포하지 않는다. 수집된 웹페이지 원문 저작권은 원저작자에게 있을 수 있다. 원본 자료 자체를 제3자가 내려받아 검사하는 방식이며, 데이터의 라이선스 및 이용약관을 따라야 한다.
