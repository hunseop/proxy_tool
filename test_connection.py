"""프록시 연결 테스트

SSH와 SNMP 연결을 테스트하고 기본 정보를 조회합니다.
"""

import logging
from monitoring_module.clients.ssh import SSHClient
from monitoring_module.config import Config
from monitoring_module.resource import ResourceMonitor
from monitoring_module.session import SessionMonitor

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_proxy(host: str):
    """단일 프록시 테스트
    
    Args:
        host (str): 프록시 서버 IP
    """
    try:
        # SSH 연결 테스트
        logger.info(f"SSH 연결 테스트 시작: {host}")
        ssh = SSHClient(
            host=host,
            username=Config.SSH_USERNAME,
            password=Config.SSH_PASSWORD,
            port=Config.SSH_PORT
        )
        
        # 기본 시스템 정보 조회
        logger.info("시스템 정보 조회 중...")
        system_info = ssh.execute_command("uname -a")
        logger.info(f"시스템 정보: {system_info}")
        
        # 리소스 모니터링 테스트
        logger.info("리소스 모니터링 테스트 중...")
        resource_monitor = ResourceMonitor(ssh)
        resources = resource_monitor.get_resource_usage()
        logger.info(f"리소스 사용량: {resources}")
        
        # 세션 모니터링 테스트
        logger.info("세션 모니터링 테스트 중...")
        session_monitor = SessionMonitor(ssh)
        sessions = session_monitor.get_active_sessions()
        logger.info(f"활성 세션 수: {len(sessions)}")
        
        logger.info("모든 테스트 완료")
        return True
        
    except Exception as e:
        logger.error(f"테스트 실패: {str(e)}")
        return False
    finally:
        if 'ssh' in locals():
            ssh.close()

if __name__ == "__main__":
    # 테스트할 프록시 서버 정보
    TEST_PROXY = "192.168.1.10"  # 실제 프록시 IP로 변경
    
    success = test_single_proxy(TEST_PROXY)
    if success:
        print("✅ 테스트 성공")
    else:
        print("❌ 테스트 실패") 