"""정책 모듈 기본 동작 테스트 스크립트

네트워크나 데이터베이스 연결 없이 PolicyManager가 정상적으로 동작하는지 확인한다.
"""

import sys
import types
import json
import logging
from pathlib import Path

# 외부 패키지가 없을 수 있으므로 더미 모듈을 준비한다.
if "pandas" not in sys.modules:
    mod = types.ModuleType("pandas")
    mod.DataFrame = lambda *a, **k: None
    sys.modules["pandas"] = mod

if "xmltodict" not in sys.modules:
    mod = types.ModuleType("xmltodict")
    mod.parse = lambda s: {}
    sys.modules["xmltodict"] = mod

from policy_module.policy_manager import PolicyManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_policy_parse(sample_path: Path) -> bool:
    """샘플 정책 파일을 읽어 PolicyManager 동작을 확인한다."""
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pm = PolicyManager(data, from_xml=False)
        lists = pm.parse_lists()
        groups, rules = pm.parse_policy()
        logger.info("리스트 개수 %s", len(lists))
        logger.info("RuleGroup 개수 %s", len(groups))
        logger.info("Rule 개수 %s", len(rules))
        return True
    except Exception as exc:
        logger.error("테스트 실패: %s", exc)
        return False


if __name__ == "__main__":
    SAMPLE = Path("sample_data/policy_combined.json")
    success = run_policy_parse(SAMPLE)
    print("✅ 테스트 성공" if success else "❌ 테스트 실패")
