# 데이터베이스 개선 작업

프록시 관리와 모니터링 기능을 고려해 데이터베이스 구조를 일부 개선한다.

## 변경 사항
- 주요 조회 컬럼에 인덱스 추가
  - `ProxyServer.group_id`
  - `ResourceStat.proxy_id`, `ResourceStat.timestamp`
  - `SessionInfo.proxy_id`, `SessionInfo.timestamp`
- dev와 prod 모두 `instance/ppat.db` 파일을 사용하도록 기본 설정 유지
- 필요 시 마이그레이션 도구를 도입해 스키마 변경을 관리한다.

## 질문
- 마이그레이션 도구로 `Flask-Migrate`를 사용할지 결정이 필요하다.
