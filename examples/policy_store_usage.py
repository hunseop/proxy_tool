"""PolicyStore 사용 예제

이 모듈은 PolicyStore를 사용하여 정책 데이터를 저장하는 방법을 보여줍니다.
API와 파일 소스 모두에 대한 예제를 포함합니다.
"""

import os
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# 로컬 모듈 임포트를 위한 경로 설정
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
while ROOT_DIR and not os.path.isdir(os.path.join(ROOT_DIR, "policy_module")):
    parent = os.path.dirname(ROOT_DIR)
    if parent == ROOT_DIR:
        break
    ROOT_DIR = parent
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


from policy_module.policy_store import PolicyStore
from policy_module.config import ProxyConfig
from ppat_db.policy_db import Base


# 데이터베이스 파일 경로 설정
DB_FILE = os.path.join(ROOT_DIR, "policy.db")
DB_URL = f"sqlite:///{DB_FILE}"


def init_database(db_url: str = DB_URL) -> None:
    """데이터베이스 초기화
    
    Args:
        db_url: 데이터베이스 연결 URL
    """
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)


def store_from_api(proxy_config: ProxyConfig, db_url: str = DB_URL) -> None:
    """API에서 정책 데이터를 가져와서 저장하는 예제

    Args:
        proxy_config: 프록시 설정
        db_url: 데이터베이스 연결 URL
    """
    
    # 1. 데이터베이스 연결 설정
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 2. PolicyStore 초기화 및 데이터 저장
        store = PolicyStore(session)
        store.store_from_api(proxy_config)
        print("API에서 정책 데이터 저장 완료")
        
    except Exception as e:
        print(f"에러 발생: {e}")
        session.rollback()
        raise
    finally:
        session.close()


DEFAULT_JSON_PATH1 = os.path.join(ROOT_DIR, 'sample_data', 'policy_combined.json')
DEFAULT_JSON_PATH2 = os.path.join(
    ROOT_DIR, 'sample_data', 'policy_with_configurations.json'
)


def store_from_files(
    json_path1: str | None = DEFAULT_JSON_PATH1,
    json_path2: str | None = DEFAULT_JSON_PATH2,
    db_url: str = DB_URL,
) -> None:
    """파일에서 정책 데이터를 가져와서 저장하는 예제
    
    Args:
        json_path1: 첫 번째 JSON 파일 경로
        json_path2: 두 번째 JSON 파일 경로
        db_url: 데이터베이스 연결 URL
    """
    
    # 1. 데이터베이스 연결 설정
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        store = PolicyStore(session)
        
        # 2. 첫 번째 JSON 파일에서 저장
        if json_path1:
            with open(json_path1, 'r') as f:
                json_data = json.load(f)  # JSON 문자열을 dict로 변환
            store.store_from_source(json_data, from_xml=False)
            print(f"{json_path1}에서 정책 데이터 저장 완료")
        
        # 3. 두 번째 JSON 파일에서 저장
        if json_path2:
            with open(json_path2, 'r') as f:
                json_data = json.load(f)  # JSON 문자열을 dict로 변환
            store.store_from_source(json_data, from_xml=False)
            print(f"{json_path2}에서 정책 데이터 저장 완료")
        
    except Exception as e:
        print(f"에러 발생: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    # 데이터베이스 초기화
    init_database()
    
    # 1. API에서 데이터 저장
    proxy_settings = ProxyConfig(
        base_url='proxy.example.com',
        username='your_username',
        password='your_password'
    )
    # store_from_api(proxy_settings)
    
    # 2. 파일에서 데이터 저장
    store_from_files()
