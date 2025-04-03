# 프록시 모니터링 시스템

프록시 서버의 리소스 사용량과 세션 정보를 모니터링하는 웹 애플리케이션입니다.

## 주요 기능

- 실시간 프록시 서버 리소스 모니터링 (CPU, 메모리, 세션 등)
- 세션 정보 조회 및 검색
- 다중 서버 모니터링 지원
- 설정 관리 (SSH 계정, SNMP, 임계값 등)

## 시스템 요구사항

- Python 3.6 이상
- 모니터링할 프록시 서버에 SSH 접속 가능해야 함
- 프록시 서버에 SNMP 설정 필요

## 설치 방법

1. 소스 코드 다운로드
```bash
git clone https://github.com/yourusername/proxy-monitoring-system.git
cd proxy-monitoring-system
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. 애플리케이션 실행
```bash
python app.py
```

4. 웹 브라우저에서 접속
```
http://localhost:5000
```

## 설정 방법

### SSH 설정

프록시 서버에 연결하기 위한 SSH 계정 정보를 설정합니다.

1. 웹 UI의 '설정' 메뉴에서 SSH 계정과 비밀번호 설정
2. 또는 `config.json` 파일 직접 수정:
```json
{
    "ssh_username": "your_ssh_username",
    "ssh_password": "your_ssh_password",
    "snmp_community": "public",
    "cpu_threshold": 80,
    "memory_threshold": 75
}
```

### SNMP 설정

모니터링할 프록시 서버에서 SNMP가 활성화되어 있어야 합니다.

1. 프록시 서버에 SNMP 설치 (예: snmpd)
2. SNMP 커뮤니티 문자열 설정
3. 웹 UI의 '설정' 메뉴에서 SNMP 커뮤니티 설정

## 사용 방법

1. 서버 추가
   - 대시보드 화면에서 '서버 추가' 버튼 클릭
   - 프록시 서버 IP 또는 도메인 입력

2. 모니터링 시작
   - SSH 계정 정보 입력
   - 조회 간격 선택
   - '모니터링 시작' 버튼 클릭

3. 세션 관리
   - 상단 메뉴에서 '세션 관리' 클릭
   - 서버 선택
   - 필요한 경우 검색어 입력 후 '검색' 버튼 클릭

4. 설정 변경
   - 상단 메뉴에서 '설정' 클릭
   - 필요한 설정 변경 후 '설정 저장' 버튼 클릭

## 프로젝트 구조

```
proxy-monitoring-system/
├── app.py                    # Flask 애플리케이션
├── config.json               # 설정 파일
├── proxy_monitor_core/       # 핵심 모니터링 모듈
│   ├── __init__.py
│   ├── config.py             # 기본 설정
│   ├── resource.py           # 리소스 모니터링
│   ├── session.py            # 세션 관리
│   ├── ssh.py                # SSH 클라이언트
│   └── utils.py              # 유틸리티 함수
├── static/                   # 정적 파일
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── main.js
├── templates/                # HTML 템플릿
│   └── index.html
└── requirements.txt          # 의존성 패키지
```

## 문제 해결

* **SSH 연결 오류**: SSH 계정, 비밀번호, 포트가 올바른지 확인
* **SNMP 오류**: SNMP 커뮤니티 문자열이 올바른지, SNMP가 활성화되어 있는지 확인
* **데이터가 표시되지 않음**: 방화벽 설정 확인, SSH와 SNMP 포트가 개방되어 있는지 확인

## 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 