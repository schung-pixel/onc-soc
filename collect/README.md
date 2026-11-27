# 수집 스크립트

매일 GitHub Actions(collect.yml)가 실행되어 `data` 브랜치에 아래 파일을 남깁니다. 앱 배포(main, Pages)에는 영향이 없습니다.

- ct_changes.json: ClinicalTrials.gov 등록 정보가 바뀐 시험 (상태, 완료예정일, 결과게시, 등록수). 월간 갱신이 처리한 뒤 비웁니다.
- fda_candidates.json: FDA 항암 승인 공지에 새로 올라온 항목 (pending)
- nccn_versions.json: NCCN 지침 판 번호 변화 (pending)
- ct_snapshot.json: 비교 기준 스냅샷

NCCN 지침 본문은 수집하지 않으며 판 번호만 읽습니다.

FDA 승인 공지 페이지는 GitHub Actions 러너 접속을 거부(404)하므로 Actions에서는 수집하지 않습니다. 월간 갱신 세션이 `python3 collect/fda_scan.py`를 직접 실행하며, 이때 data 브랜치의 fda_candidates.json을 collect/에 내려받아 사용하고 결과를 되돌려 올립니다.
