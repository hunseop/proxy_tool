"""프록시 연결 테스트용 스크립트

실제 네트워크 연결 없이 모듈 임포트가 정상적으로 이루어지는지 확인한다.
"""

import sys
import types
import logging

# 테스트 환경에서는 외부 패키지가 없을 수 있으므로 간단한 더미 모듈을 준비한다.
if "paramiko" not in sys.modules:
    dummy = types.ModuleType("paramiko")
    class _SSHClient:
        def set_missing_host_key_policy(self, *a, **k):
            pass
        def connect(self, *a, **k):
            pass
        def exec_command(self, *a, **k):
            from io import StringIO
            return None, StringIO(""), StringIO("")
        def close(self):
            pass
    dummy.SSHClient = _SSHClient
    dummy.AutoAddPolicy = lambda: None
    sys.modules["paramiko"] = dummy

if "pandas" not in sys.modules:
    mod = types.ModuleType("pandas")
    mod.DataFrame = lambda *a, **k: None
    sys.modules["pandas"] = mod

if "pysnmp.hlapi" not in sys.modules:
    hlapi = types.ModuleType("pysnmp.hlapi")
    def _dummy(*a, **k):
        class _Iter:
            def __iter__(self):
                return iter([(None, None, None, [])])
        return _Iter()
    for name in [
        "SnmpEngine",
        "CommunityData",
        "UdpTransportTarget",
        "ContextData",
        "ObjectType",
        "ObjectIdentity",
        "getCmd",
    ]:
        setattr(hlapi, name, _dummy)
    sys.modules["pysnmp.hlapi"] = hlapi

from monitoring_module.resource import ResourceMonitor
from monitoring_module.session import SessionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_single_proxy(host: str, username: str = "root", password: str = "123456", port: int = 22) -> bool:
    """단일 프록시 테스트를 간단히 수행한다."""
    try:
        rm = ResourceMonitor(host, username, password)
        sm = SessionManager(host, username, password)
        logger.info("모듈 임포트 및 객체 생성 성공")
        rm.get_memory_and_uniq_clients()
        sm.get_session()
        return True
    except Exception as exc:
        logger.error(f"테스트 실패: {exc}")
        return False


if __name__ == "__main__":
    TEST_PROXY = "127.0.0.1"
    success = run_single_proxy(TEST_PROXY)
    print("✅ 테스트 성공" if success else "❌ 테스트 실패")
