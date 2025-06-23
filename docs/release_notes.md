# Release Notes

## v0.2.0 (2025-06-23)

### 개선 사항
- `ConditionParser`가 중첩된 `propertyInstance` 구조를 재귀적으로 처리하도록 로직을 확장했습니다.
- `propertyInstance` 내부 속성(`@useMostRecentConfiguration` 등)을 `attributes` 키로 반환하도록 개선했습니다.
- 일부 소스 파일 끝에 누락된 줄바꿈을 추가하고 터미널 출력이 남아 있던 부분을 정리했습니다.

### 버그 수정
- 그룹 및 룰 조건에서 리스트 값을 저장할 때 발생할 수 있던 오류를 해결했습니다.

