"""Policy parsing results database utilities."""

import json
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from policy_module.policy_manager import PolicyManager

Base = declarative_base()


class PolicyItem(Base):
    __tablename__ = "policy_items"

    id = Column(Integer, primary_key=True)
    item_id = Column(String(100), unique=True)
    item_type = Column(String(20))  # "group" 또는 "rule"
    name = Column(String(200))
    path = Column(String(500))
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    order_number = Column(Integer)
    action = Column(String(100))
    action_options = Column(JSON)
    default_rights = Column(String(100))
    cycle_request = Column(String(100))
    cycle_response = Column(String(100))
    cycle_embedded_object = Column(String(100))
    cloud_synced = Column(String(100))
    ac_elements = Column(Text)
    raw = Column(JSON)  # 원본 데이터 전체 저장

    # 관계 설정
    conditions = relationship("PolicyCondition", back_populates="item")


class PolicyCondition(Base):
    __tablename__ = "policy_conditions"

    id = Column(Integer, primary_key=True)
    item_id = Column(String(100), ForeignKey("policy_items.item_id"))
    parent_id = Column(Integer, ForeignKey("policy_conditions.id"))
    index = Column(Integer)
    prefix = Column(String(50))
    open_bracket = Column(Integer, default=0)
    close_bracket = Column(Integer, default=0)
    property = Column(String(200))
    operator = Column(String(100))
    values = Column(JSON)  # property_values를 JSON으로 저장
    result = Column(String(100))
    raw = Column(JSON)  # 원본 데이터 전체 저장

    # 관계 설정
    item = relationship("PolicyItem", back_populates="conditions")
    parent_condition = relationship("PolicyCondition", remote_side=[id])
    list_mappings = relationship("ConditionListMap", back_populates="condition")


class ConditionListMap(Base):
    __tablename__ = "condition_list_map"

    id = Column(Integer, primary_key=True)
    condition_id = Column(Integer, ForeignKey("policy_conditions.id"))
    list_id = Column(String(100), ForeignKey("policy_lists.list_id"))

    # 관계 설정
    condition = relationship("PolicyCondition", back_populates="list_mappings")
    list = relationship("PolicyList", back_populates="condition_mappings")


class PolicyList(Base):
    __tablename__ = "policy_lists"

    id = Column(Integer, primary_key=True)
    list_id = Column(String(100), unique=True)
    entry_id = Column(String(100))
    value = Column(Text)
    name = Column(String(200))
    type_id = Column(String(100))
    classifier = Column(String(100))
    description = Column(Text)
    metadata_json = Column("metadata", JSON)  # 추가 메타데이터
    raw = Column(JSON)  # 원본 데이터 전체 저장

    # 관계 설정
    condition_mappings = relationship("ConditionListMap", back_populates="list")


class PolicyConfiguration(Base):
    __tablename__ = "policy_configurations"

    id = Column(Integer, primary_key=True)
    configuration_id = Column(String(100), unique=True)
    name = Column(String(200))
    version = Column(String(50))
    mwg_version = Column(String(50))
    template_id = Column(String(100))
    target_id = Column(String(100))
    description = Column(Text)
    metadata_json = Column("metadata", JSON)  # 추가 메타데이터
    raw = Column(JSON)  # 원본 데이터 전체 저장

    # 관계 설정
    properties = relationship("ConfigurationProperty", back_populates="configuration")


class ConfigurationProperty(Base):
    __tablename__ = "configuration_properties"

    id = Column(Integer, primary_key=True)
    configuration_id = Column(Integer, ForeignKey("policy_configurations.id"))
    key = Column(String(200))
    value = Column(Text)
    type = Column(String(100))
    encrypted = Column(Boolean, default=False)
    list_type = Column(String(100))
    metadata_json = Column("metadata", JSON)  # 추가 메타데이터
    raw = Column(JSON)  # 원본 데이터 전체 저장

    # 관계 설정
    configuration = relationship("PolicyConfiguration", back_populates="properties")


engine = create_engine("sqlite:///policy.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def save_policy_to_db(
    policy_source: Any,
    list_source: Any | None = None,
    *,
    from_xml: bool = False,
) -> None:
    """Parse policy and list data then store to the local DB."""
    manager = PolicyManager(policy_source, list_source, from_xml=from_xml)
    list_records = manager.parse_lists()
    items = manager.parse_policy()
    configs = manager.parse_configurations()

    with Session() as session:
        for l in list_records:
            rec = PolicyList(
                list_id=l.get("list_id"),
                entry_id=l.get("@id"),
                value=l.get("value"),
                name=l.get("list_name"),
                type_id=l.get("list_type_id"),
                classifier=l.get("list_classifier"),
                description=l.get("list_description"),
            )
            session.add(rec)

        current_item_id: str | None = None
        condition_index = 0
        parent_map: dict[int, int] = {}
        for rec in items:
            if rec.get("id"):
                current_item_id = rec.get("id")
                record = PolicyItem(
                    item_id=current_item_id,
                    item_type=rec.get("type"),
                    name=rec.get("name"),
                    path=rec.get("path") or rec.get("group_path"),
                    description=rec.get("description"),
                    enabled=rec.get("enabled"),
                    action=rec.get("actionContainer_raw"),
                    action_options=rec.get("immediateActions_raw"),
                    default_rights=rec.get("defaultRights"),
                    cycle_request=rec.get("cycleRequest"),
                    cycle_response=rec.get("cycleResponse"),
                    cycle_embedded_object=rec.get("cycleEmbeddedObject"),
                    cloud_synced=rec.get("cloudSynced"),
                    ac_elements=rec.get("acElements"),
                    raw=json.dumps(rec, ensure_ascii=False),
                )
                session.merge(record)
                condition_index = 0
                parent_map = {}
            if current_item_id is None:
                continue
            cond = rec.get("condition_raw") or {}
            idx = rec.get("condition_index") or (condition_index + 1)
            condition_index = idx
            cond_record = PolicyCondition(
                item_id=current_item_id,
                index=idx,
                parent_id=parent_map.get(rec.get("condition_parent_index")),
                prefix=cond.get("prefix"),
                open_bracket=int(cond.get("open_bracket", 0)),
                close_bracket=int(cond.get("close_bracket", 0)),
                property=cond.get("property"),
                operator=cond.get("operator"),
                values=json.dumps(cond.get("property_values"), ensure_ascii=False)
                if cond.get("property_values") is not None
                else None,
                result=cond.get("expression_value"),
                raw=json.dumps(cond, ensure_ascii=False),
            )
            session.add(cond_record)
            session.flush()
            parent_map[idx] = cond_record.id
            values = cond.get("property_values")
            list_ids: list[str] = []
            if isinstance(values, str) and values in manager.lists:
                list_ids.append(values)
            elif isinstance(values, (list, tuple)):
                for v in values:
                    if isinstance(v, str) and v in manager.lists:
                        list_ids.append(v)
            for lid in list_ids:
                session.add(
                    ConditionListMap(condition_id=cond_record.id, list_id=lid)
                )

        for conf in configs:
            cfg = PolicyConfiguration(
                configuration_id=conf.get("id"),
                name=conf.get("name"),
                version=conf.get("version"),
                mwg_version=conf.get("mwg_version"),
                template_id=conf.get("template_id"),
                target_id=conf.get("target_id"),
                description=conf.get("description"),
                raw=json.dumps(conf, ensure_ascii=False),
            )
            session.add(cfg)
            session.flush()
            for prop in conf.get("properties", []):
                session.add(
                    ConfigurationProperty(
                        configuration_id=cfg.id,
                        key=prop.get("key"),
                        value=prop.get("value"),
                        type=prop.get("type"),
                        encrypted=prop.get("encrypted"),
                        list_type=prop.get("list_type"),
                    )
                )

        session.commit()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: policy_db.py <policy_json> [lists_json]")
        raise SystemExit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        policy = json.load(f)

    lists = None
    if len(sys.argv) > 2:
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            lists = json.load(f)

    save_policy_to_db(policy, lists)
