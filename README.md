# 프록시 모니터링 & 정책 관리 시스템

프록시 서버 그룹의 리소스 사용량을 모니터링하고 정책을 관리하는 웹 애플리케이션입니다.

## 주요 기능

### 프록시 관리
- 목적별 프록시 그룹 관리
  - Main Appliance: 정책 관리 주체
  - Cluster Appliances: Main과 동일 정책 적용
- 프록시 서버 정보 CRUD
- 그룹 구성 관리

### 모니터링
- 실시간 프록시 서버 리소스 모니터링
  - CPU, 메모리, 디스크, 네트워크 사용률
  - 임계치 초과 항목 강조 표시
- 세션 모니터링
  - Client IP, User Name, URL 기반 검색
  - IP/URL/Proxy 별 세션 통계

### 정책 관리
- Main Appliance 정책 관리
  - 정책 업데이트 및 동기화
  - 정책 검색 및 동적 필터링
  - 엑셀 형식 추출

## 시스템 아키텍처

### Backend
- Flask 기반 RESTful API
- 모듈식 구조:
  - `monitoring_module`: 리소스 모니터링
  - `policy_module`: 정책 관리
  - `ppat_db`: 데이터베이스 관리
- SQLite 데이터베이스

### Frontend
- 미니멀 & 반응형 웹 디자인
- 실시간 데이터 업데이트
- 대시보드 및 관리 인터페이스

## API 엔드포인트

### 프록시 관리
- `GET /api/proxies`: 프록시 목록 조회
- `POST /api/proxies`: 프록시 추가
- `PUT /api/proxies/<id>`: 프록시 정보 수정
- `DELETE /api/proxies/<id>`: 프록시 삭제
- `GET /api/proxy-groups`: 프록시 그룹 조회

### 모니터링
- `GET /api/monitoring/resources`: 자원 사용률 조회
- `GET /api/monitoring/sessions`: 세션 정보 조회
- `POST /api/monitoring/thresholds`: 임계값 설정

### 정책 관리
- `GET /api/policies`: 정책 목록 조회
- `POST /api/policies/update`: 정책 업데이트
- `GET /api/policies/search`: 정책 검색
- `GET /api/policies/export`: 정책 엑셀 추출

## 설치 방법

1. 소스 코드 다운로드
```bash
git clone <레포지토리 주소>
cd proxy_tool
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 설정
- `config.json` 파일에서 기본 설정 구성
- 프록시 서버 접속 정보 설정
- 모니터링 임계값 설정

5. 데이터베이스 초기화
```bash
flask db upgrade
```

6. 애플리케이션 실행
```bash
flask run
```

## 프로젝트 구조

```
proxy_tool/
├── api/                     # API 엔드포인트
│   ├── __init__.py
│   ├── proxy.py            # 프록시 관리 API
│   ├── monitoring.py       # 모니터링 API
│   └── policy.py           # 정책 관리 API
├── monitoring_module/      # 모니터링 모듈
│   ├── __init__.py
│   ├── config.py
│   ├── resource.py
│   └── session.py
├── policy_module/         # 정책 관리 모듈
│   ├── __init__.py
│   ├── config.py
│   └── policy_manager.py
├── ppat_db/              # 데이터베이스 모듈
│   ├── __init__.py
│   └── policy_db.py
├── static/               # 프론트엔드 리소스
├── templates/            # HTML 템플릿
├── app.py               # Flask 애플리케이션
└── config.json          # 설정 파일
```

## 설정 방법

### 프록시 그룹 설정

```json
{
    "name": "Production-Proxy",
    "description": "운영 프록시 그룹",
    "main_appliance": {
        "ip": "192.168.1.10",
        "ssh_port": 22,
        "snmp_port": 161
    },
    "cluster_appliances": [
        {
            "ip": "192.168.1.11",
            "ssh_port": 22,
            "snmp_port": 161
        },
        {
            "ip": "192.168.1.12",
            "ssh_port": 22,
            "snmp_port": 161
        }
    ]
}
```

## 사용 방법

1. 프록시 그룹 관리
   - 프록시 서버 추가/수정/삭제
   - Main/Cluster 구성 관리

2. 모니터링
   - 자원 사용률 대시보드 확인
   - 세션 정보 조회 및 검색
   - 임계값 설정

3. 정책 관리
   - Main Appliance 선택
   - 정책 업데이트
   - 정책 검색 및 필터링
   - 정책 엑셀 추출

## 문제 해결

* **프록시 연결 오류**: SSH/SNMP 설정 확인
* **정책 동기화 실패**: Main Appliance 연결 상태 확인
* **모니터링 데이터 누락**: 네트워크 연결 및 권한 설정 확인

## 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.
