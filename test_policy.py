"""정책 모듈 테스트

정책 조회 및 파싱 기능을 테스트합니다.
"""

import logging
import json
from policy_module.clients.skyhigh_client import SkyhighSWGClient
from policy_module.policy_manager import PolicyManager
from ppat_db.policy_db import PolicyDB, save_policy_to_db

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_policy_fetch(host: str):
    """정책 조회 테스트
    
    Args:
        host (str): 프록시 서버 IP
    """
    try:
        # Skyhigh SWG 클라이언트 연결
        logger.info(f"정책 서버 연결 테스트 시작: {host}")
        client = SkyhighSWGClient(host)
        
        # 정책 조회
        logger.info("정책 조회 중...")
        policy_data = client.get_policies()
        
        # 정책 데이터 검증
        if not policy_data:
            logger.error("정책 데이터가 비어있습니다")
            return False
            
        # 정책 저장 테스트
        logger.info("정책 저장 테스트 중...")
        save_policy_to_db(policy_data)
        
        # 정책 검색 테스트
        logger.info("정책 검색 테스트 중...")
        with PolicyDB() as db:
            policies = db.list_policies()
            logger.info(f"저장된 정책 수: {len(policies)}")
            
            # 샘플 정책 출력
            if policies:
                sample = policies[0]
                logger.info(f"샘플 정책: {json.dumps(sample, indent=2, ensure_ascii=False)}")
        
        logger.info("모든 테스트 완료")
        return True
        
    except Exception as e:
        logger.error(f"테스트 실패: {str(e)}")
        return False

if __name__ == "__main__":
    # 테스트할 프록시 서버 정보
    TEST_PROXY = "192.168.1.10"  # 실제 프록시 IP로 변경
    
    success = test_policy_fetch(TEST_PROXY)
    if success:
        print("✅ 테스트 성공")
    else:
        print("❌ 테스트 실패") 