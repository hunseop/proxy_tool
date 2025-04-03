import time
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('proxy_monitor')

def interruptible_sleep(seconds, is_running):
    """중단 가능한 sleep 함수"""
    end_time = time.time() + seconds
    while time.time() < end_time and is_running():
        time.sleep(0.1)

def split_line(lst: str) -> list:
    """파이프로 구분된 문자열을 리스트로 분리"""
    return [item.strip().rstrip('\n') for item in lst.split(' | ')]

def get_current_timestamp():
    """현재 시간을 반환"""
    return {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S')
    }

def validate_resource_data(data: dict) -> bool:
    """리소스 데이터 유효성 검사
    
    Args:
        data (dict): 검사할 데이터
        
    Returns:
        bool: 유효성 검사 통과 여부
    """
    required_fields = ['cpu', 'memory', 'uc', 'cc', 'cs', 'http', 'https', 'ftp']
    
    try:
        # 필수 필드 존재 확인
        for field in required_fields:
            if field not in data:
                logger.error(f"필수 필드 누락: {field}")
                return False
        
        # CPU 값 검증
        if data['cpu'] != 'error' and not (-1 <= float(data['cpu']) <= 100):
            logger.error(f"잘못된 CPU 값: {data['cpu']}")
            return False
            
        # 메모리 값 검증
        if data['memory'] != 'error' and not (-1 <= float(data['memory']) <= 100):
            logger.error(f"잘못된 메모리 값: {data['memory']}")
            return False
            
        return True
    except ValueError as e:
        logger.error(f"데이터 검증 중 형식 오류: {e}")
        return False
    except Exception as e:
        logger.error(f"데이터 검증 중 오류 발생: {e}")
        return False 