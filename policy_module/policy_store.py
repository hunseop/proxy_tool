"""정책 데이터 저장소

정책 데이터를 데이터베이스에 저장하는 기능을 제공합니다.
API나 파일 소스로부터 데이터를 가져와 파싱하고 저장합니다.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from .clients.skyhigh_client import SkyhighSWGClient
from .policy_manager import PolicyManager
from ppat_db.policy_db import (
    PolicyList, PolicyConfiguration, 
    PolicyGroup, PolicyRule
)


@dataclass
class PolicyData:
    """정책 데이터 컨테이너"""
    lists: List[Dict[str, Any]]
    configurations: List[Dict[str, Any]]
    rules: List[Dict[str, Any]]
    groups: List[Dict[str, Any]]


class PolicyStore:
    """정책 데이터 저장소
    
    API나 파일 소스로부터 정책 데이터를 가져와서 데이터베이스에 저장합니다.
    단일 트랜잭션으로 처리하여 데이터 일관성을 보장합니다.
    """
    
    def __init__(self, session: Session):
        """초기화
        
        Args:
            session: SQLAlchemy 세션
        """
        self.session = session

    def store_from_api(self, proxy_config) -> None:
        """API에서 데이터를 가져와서 저장
        
        Args:
            proxy_config: 프록시 설정
            
        Raises:
            Exception: API 연결 또는 데이터 처리 실패시
        """
        with SkyhighSWGClient(proxy_config) as client:
            # 메인 룰셋만 가져오기
            ruleset = client.list_rulesets(top_level_only=True)[0]
            content = client.export_ruleset(ruleset['id'], ruleset['title'])
            self.store_from_source(content, from_xml=True)

    def store_from_source(self, source: Any, *, from_xml: bool = False) -> None:
        """소스 데이터에서 파싱하여 저장
        
        Args:
            source: 소스 데이터 (XML 또는 JSON)
            from_xml: XML 형식 여부
            
        Raises:
            Exception: 파싱 또는 저장 실패시
        """
        # 1. 데이터 파싱
        manager = PolicyManager(source, from_xml=from_xml)
        data = PolicyData(
            lists=manager.parse_lists(),
            configurations=manager.parse_configurations(),
            groups=manager.parse_policy()[0],
            rules=manager.parse_policy()[1]
        )
        
        # 2. 단일 트랜잭션으로 저장
        try:
            self._store_all(data)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise Exception(f"정책 데이터 저장 실패: {e}")

    def _store_all(self, data: PolicyData) -> None:
        """단일 메서드로 모든 데이터 저장
        
        Args:
            data: 저장할 정책 데이터
        """
        # 기존 데이터 삭제
        self._clear_existing_data()
        
        # 새 데이터 저장
        for list_item in data.lists:
            self.session.add(PolicyList(**list_item))
            
        for config in data.configurations:
            self.session.add(PolicyConfiguration(**config))
            
        for group in data.groups:
            self.session.add(PolicyGroup(**group))
            
        for rule in data.rules:
            self.session.add(PolicyRule(**rule))

    def _clear_existing_data(self) -> None:
        """기존 데이터 삭제"""
        for table in [PolicyList, PolicyConfiguration, PolicyGroup, PolicyRule]:
            self.session.query(table).delete() 