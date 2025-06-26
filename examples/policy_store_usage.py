"""PolicyStore 사용 예제

이 모듈은 PolicyStore를 사용하여 정책 데이터를 저장하는 방법을 보여줍니다.
API와 파일 소스 모두에 대한 예제를 포함합니다.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any

from policy_module.policy_store import PolicyStore


def store_from_api(proxy_config: Dict[str, str], db_url: str = 'sqlite:///policies.db') -> None:
    """API에서 정책 데이터를 가져와서 저장하는 예제
    
    Args:
        proxy_config: 프록시 설정 정보
            - host: 프록시 호스트
            - username: 사용자 이름
            - password: 비밀번호
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


def store_from_files(xml_path: str = None, json_path: str = None, db_url: str = 'sqlite:///policies.db') -> None:
    """파일에서 정책 데이터를 가져와서 저장하는 예제
    
    Args:
        xml_path: XML 파일 경로
        json_path: JSON 파일 경로
        db_url: 데이터베이스 연결 URL
    """
    
    # 1. 데이터베이스 연결 설정
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        store = PolicyStore(session)
        
        # 2. XML 파일에서 저장
        if xml_path:
            with open(xml_path, 'r') as f:
                xml_content = f.read()
            store.store_from_source(xml_content, from_xml=True)
            print(f"{xml_path}에서 정책 데이터 저장 완료")
        
        # 3. JSON 파일에서 저장
        if json_path:
            with open(json_path, 'r') as f:
                json_content = f.read()
            store.store_from_source(json_content, from_xml=False)
            print(f"{json_path}에서 정책 데이터 저장 완료")
        
    except Exception as e:
        print(f"에러 발생: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    # 사용 예시
    
    # 1. API에서 데이터 저장
    proxy_settings = {
        'host': 'proxy.example.com',
        'username': 'your_username',
        'password': 'your_password'
    }
    store_from_api(proxy_settings)
    
    # 2. 파일에서 데이터 저장
    store_from_files(
        xml_path='sample_data/policy_combined.json',
        json_path='sample_data/policy_with_configurations.json'
    ) 
