import paramiko
import time
import logging
from monitor_module.config import Config
from monitor_module.utils import logger

class SSHClient:
    def __init__(self, host, username=None, password=None, port=None, max_retries=3, retry_delay=5):
        self.host = host
        self.username = username or Config.SSH_USERNAME
        self.password = password or Config.SSH_PASSWORD
        self.port = port or Config.SSH_PORT
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client = None
        
        # paramiko 로깅 비활성화
        logging.getLogger('paramiko').setLevel(logging.CRITICAL)

    def connect(self):
        """SSH 연결 수행 (재시도 로직 포함)"""
        if self._client is not None:
            return self._client

        retries = 0
        last_exception = None

        while retries < self.max_retries:
            try:
                self._client = paramiko.SSHClient()
                self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self._client.connect(
                    self.host,
                    username=self.username,
                    password=self.password,
                    port=self.port,
                    timeout=30  # 연결 타임아웃 30초
                )
                logger.info(f"SSH 연결 성공: {self.host}")
                return self._client
            except Exception as e:
                last_exception = e
                retries += 1
                if retries < self.max_retries:
                    logger.warning(f"SSH 연결 실패 ({retries}/{self.max_retries}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"SSH 연결 최대 재시도 횟수 초과: {e}")

        raise ConnectionError(f"SSH 연결 실패: {last_exception}")

    def execute_command(self, command, timeout=60):
        """명령어 실행 (타임아웃 처리 포함)"""
        client = self.connect()
        try:
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            return stdin, stdout, stderr
        except Exception as e:
            logger.error(f"명령어 실행 실패: {e}")
            raise

    def close(self):
        """SSH 연결 종료"""
        if self._client:
            try:
                self._client.close()
                logger.info(f"SSH 연결 종료: {self.host}")
            except Exception as e:
                logger.error(f"SSH 연결 종료 중 오류: {e}")
            finally:
                self._client = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 
