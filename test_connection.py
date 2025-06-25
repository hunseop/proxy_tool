"""프록시 연결 테스트

실제 프록시 장비에 접속해 리소스와 세션 정보를 조회한다. 환경에 따라
의존 모듈이 없거나 테스트 대상이 없을 수 있으므로 조건부로 실행한다.
"""

import logging
import os
import pytest

pytest.importorskip("paramiko")
pytest.importorskip("pysnmp")
pytest.importorskip("pandas")

from monitoring_module.config import Config, ProxyConfig, MonitoringConfig
from monitoring_module.resource import ResourceMonitor
from monitoring_module.session import SessionManager
from monitoring_module.clients.ssh import SSHClient

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_proxy(host: str, username: str = 'root', password: str = '123456', port: int = 22) -> bool:
    """단일 프록시 테스트"""
    try:
        # 프록시 설정 생성
        proxy_config = ProxyConfig(
            host=host,
            username=username,
            password=password,
            port=port,
            is_main=True
        )
        monitoring_config = MonitoringConfig()  # 기본 모니터링 설정 사용
        config = Config(proxies=[proxy_config])
        
        # SSH 연결 테스트
        logger.info(f"SSH 연결 테스트 시작: {host}")
        ssh = SSHClient(proxy_config)
        
        with ssh:
            # 기본 시스템 정보 조회
            logger.info("시스템 정보 조회 중...")
            stdin, stdout, stderr = ssh.execute_command("uname -a")
            system_info = stdout.read().decode().strip()
            logger.info(f"시스템 정보: {system_info}")
            
            # 리소스 모니터링 테스트
            logger.info("리소스 모니터링 테스트 중...")
            resource_monitor = ResourceMonitor(host, username, password)
            resources = resource_monitor.get_resource_data()
            logger.info(f"리소스 사용량: {resources}")
            
            # 세션 모니터링 테스트
            logger.info("세션 모니터링 테스트 중...")
            session_monitor = SessionManager(
                host,
                username,
                password,
            )
            sessions = session_monitor.get_session()
            logger.info(f"활성 세션 수: {len(sessions)}")
            
            logger.info("모든 테스트 완료")
            return True
            
    except Exception as e:
        logger.error(f"테스트 실패: {str(e)}")
        return False


def test_connection():
    """환경 변수에 지정된 프록시에 실제 연결을 시도한다."""
    host = os.getenv("TEST_PROXY")
    if not host:
        pytest.skip("TEST_PROXY not set")
    username = os.getenv("TEST_USERNAME", "root")
    password = os.getenv("TEST_PASSWORD", "123456")
    port = int(os.getenv("TEST_PORT", "22"))
    assert test_single_proxy(host, username, password, port)

if __name__ == "__main__":
    # 테스트할 프록시 서버 정보
    TEST_PROXY = "192.168.1.10"  # 실제 프록시 IP로 변경
    TEST_USERNAME = "root"  # 기본값 사용
    TEST_PASSWORD = "123456"  # 기본값 사용
    TEST_PORT = 22  # 기본값 사용
    
    success = test_single_proxy(
        host=TEST_PROXY,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        port=TEST_PORT
    )
    if success:
        print("✅ 테스트 성공")
    else:
        print("❌ 테스트 실패") 