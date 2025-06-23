# 데이터베이스 스키마

다음 표는 정책 관련 데이터를 저장하기 위해 사용되는 주요 테이블입니다.

| 테이블 | 설명 |
| ------ | ---- |
| `policy_groups` | 정책 그룹 정보. 그룹 ID와 경로, 원본 JSON이 저장됩니다. |
| `policy_rules` | 개별 룰 정보. 룰 ID와 소속 그룹 경로를 포함합니다. |
| `policy_conditions` | 그룹과 룰의 조건을 저장합니다. `rule_id` 또는 `group_id` 를 통해 어느 객체의 조건인지 구분하며, 괄호 개수(`open_bracket`, `close_bracket`)와 비교 연산자 등이 기록됩니다. |
| `policy_lists` | 정책에서 참조하는 객체 리스트 항목을 저장합니다. |
| `condition_list_map` | 조건이 참조하는 리스트 ID를 매핑합니다. |
| `policy_configurations` | configuration 정보를 별도로 저장합니다. |

각 테이블의 컬럼은 `ppat_db/policy_db.py`의 SQLAlchemy 모델 정의에서 확인할 수 있습니다.
