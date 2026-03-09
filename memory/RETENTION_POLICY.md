Retention policy (applied per 요청)

- Full transcripts (원문): 보존기간 6개월
- Summaries (요약본): 보존기간 6개월
- Session restore 대상(적극 복원/인덱싱): 최근 1개월치만 인덱스/검색 대상으로 유지
- 보안: 사용자 요청에 따라 암호화/접근 제어 미적용(현재)

(정책 적용일: 2026-03-09 12:11 KST)

Cleanup behavior
- 매일 실행되는 cleanup 스크립트가 다음을 수행:
  1) memory/sessions 및 memory/logs 등에서 6개월 초과 원문/요약 삭제
  2) 벡터 인덱스는 최근 1개월치만 유지(이전 인덱스는 제거)

파일: memory/cleanup_retention.py (자동 생성 및 크론 등록)
