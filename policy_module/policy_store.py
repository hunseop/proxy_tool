"""정책 데이터 저장소

정책 데이터를 데이터베이스에 저장하는 기능을 제공합니다.
API나 파일 소스로부터 데이터를 가져와 파싱하고 저장합니다.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from .clients.skyhigh_client import SkyhighSWGClient
from .policy_manager import PolicyManager
from ppat_db.policy_db import (
    PolicyList, PolicyConfiguration,
    PolicyItem, PolicyCondition, ConditionListMap
)


@dataclass
class PolicyData:
    """정책 데이터 컨테이너"""
    lists: List[Dict[str, Any]]
    configurations: List[Dict[str, Any]]
    items: List[Dict[str, Any]]


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
            items=manager.parse_policy(),
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
        
        # 리스트 데이터를 list_id로 그룹화하여 저장
        list_groups: Dict[str, List[Dict[str, Any]]] = {}
        for list_item in data.lists:
            list_id = list_item.get("list_id")
            if list_id:
                list_groups.setdefault(list_id, []).append(list_item)
        
        # 각 리스트 그룹을 저장
        for list_id, items in list_groups.items():
            # 첫 번째 항목의 메타데이터 사용
            first_item = items[0]
            list_record = PolicyList(
                list_id=list_id,
                entry_id=first_item.get("@id"),
                value=first_item.get("value"),
                name=first_item.get("list_name"),
                type_id=first_item.get("list_type_id"),
                classifier=first_item.get("list_classifier"),
                description=first_item.get("list_description"),
                raw={"entries": items}  # 모든 엔트리를 raw 필드에 저장
            )
            self.session.add(list_record)
            
        # 설정 데이터 저장
        for config in data.configurations:
            config_record = PolicyConfiguration(
                configuration_id=config.get("id"),
                name=config.get("name"),
                version=config.get("version"),
                mwg_version=config.get("mwg_version"),
                template_id=config.get("template_id"),
                target_id=config.get("target_id"),
                description=config.get("description"),
                raw=config  # 원본 데이터 저장
            )
            self.session.add(config_record)
            
        # 정책 아이템 데이터 저장
        for item in data.items:
            if not item.get("id"):  # 조건 데이터는 건너뛰기
                continue
                
            item_record = PolicyItem(
                item_id=item.get("id"),
                item_type=item.get("type"),
                name=item.get("name"),
                path=item.get("path") or item.get("group_path"),
                description=item.get("description"),
                enabled=item.get("enabled"),
                action=item.get("actionContainer_raw"),
                action_options=item.get("immediateActions_raw"),
                default_rights=item.get("defaultRights"),
                cycle_request=item.get("cycleRequest"),
                cycle_response=item.get("cycleResponse"),
                cycle_embedded_object=item.get("cycleEmbeddedObject"),
                cloud_synced=item.get("cloudSynced"),
                ac_elements=item.get("acElements"),
                raw=item  # 원본 데이터 저장
            )
            self.session.add(item_record)

    def _clear_existing_data(self) -> None:
        """기존 데이터 삭제"""
        for table in [PolicyList, PolicyConfiguration, PolicyItem]:
            self.session.query(table).delete()
