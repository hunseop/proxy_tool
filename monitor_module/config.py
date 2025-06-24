class Config:
    # SSH 설정
    SSH_USERNAME = 'root'
    SSH_PASSWORD = '123456'  # 실제 운영환경에서는 환경변수나 보안저장소에서 가져와야 함
    SSH_PORT = 22
    
    # 모니터링 설정
    CPU_THRESHOLD = 10  # CPU 임계값 (%)
    MEMORY_THRESHOLD = 21  # 메모리 임계값 (%)
    DEFAULT_DELAY = 5  # 기본 딜레이 시간 (초)
    
    # SNMP 설정
    SNMP_COMMUNITY = 'public'
    SNMP_PORT = 161
    
    # SNMP OID 설정 (OS12 기준)
    SNMP_OIDS = {
        'CPU': '1.3.6.1.2.1.25.3.3.1.2.1',
        'Memory': '1.3.6.1.2.1.25.2.2.1.1',
        'CC': '1.3.6.1.2.1.25.4.2.1.2',
        'CS': '1.3.6.1.2.1.25.4.2.1.3',
        'HTTP': '1.3.6.1.2.1.25.4.2.1.2',
        'HTTPS': '1.3.6.1.2.1.25.4.2.1.3',
        'FTP': '1.3.6.1.2.1.25.4.2.1.4',
    }
    
    # 명령어
    SESSION_CMD = (
        "/opt/mwg/bin/mwg-core -S connections "
        "| awk -F ' | ' '{print $2" | "%5" | "%6" | "%6" | "%7" | "%18" | "%10" | "%11" | "%15"}'"
    )
