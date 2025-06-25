"""Policy parsing results database utilities."""

import json
from typing import Any

from sqlalchemy import Column, Integer, String, Text, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from policy_module.policy_manager import PolicyManager

Base = declarative_base()


class PolicyGroup(Base):
    __tablename__ = "policy_groups"

    id = Column(Integer, primary_key=True)
    group_id = Column(String(100), unique=True)
    name = Column(String(200))
    path = Column(String(500))
    raw = Column(Text)


class PolicyRule(Base):
    __tablename__ = "policy_rules"

    id = Column(Integer, primary_key=True)
    rule_id = Column(String(100), unique=True)
    name = Column(String(200))
    group_path = Column(String(500))
    raw = Column(Text)


class PolicyCondition(Base):
    __tablename__ = "policy_conditions"

    id = Column(Integer, primary_key=True)
    rule_id = Column(String(100))
    group_id = Column(String(100))
    parent_id = Column(Integer, ForeignKey("policy_conditions.id"), nullable=True)
    index = Column(Integer)
    prefix = Column(String(50))
    open_bracket = Column(Integer, default=0)
    close_bracket = Column(Integer, default=0)
    property = Column(String(200))
    operator = Column(String(100))
    values = Column(Text)
    result = Column(String(100))
    raw = Column(Text)


class ConditionListMap(Base):
    __tablename__ = "condition_list_map"

    id = Column(Integer, primary_key=True)
    condition_id = Column(Integer, ForeignKey("policy_conditions.id"))
    list_id = Column(String(100))


class PolicyList(Base):
    __tablename__ = "policy_lists"

    id = Column(Integer, primary_key=True)
    list_id = Column(String(100))
    entry_id = Column(String(100))
    value = Column(Text)
    name = Column(String(200))
    type_id = Column(String(100))
    classifier = Column(String(100))
    description = Column(Text)


class PolicyConfiguration(Base):
    __tablename__ = "policy_configurations"

    id = Column(Integer, primary_key=True)
    configuration_id = Column(String(100))
    name = Column(String(200))
    version = Column(String(50))
    mwg_version = Column(String(50))
    template_id = Column(String(100))
    target_id = Column(String(100))
    description = Column(Text)
    raw = Column(Text)


class ConfigurationProperty(Base):
    __tablename__ = "configuration_properties"

    id = Column(Integer, primary_key=True)
    configuration_id = Column(Integer, ForeignKey("policy_configurations.id"))
    key = Column(String(200))
    value = Column(Text)
    type = Column(String(100))
    encrypted = Column(String(10))
    list_type = Column(String(100))


engine = create_engine("sqlite:///policy.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def save_policy_to_db(source: Any, *, from_xml: bool = False) -> None:
    """Parse policy XML/JSON and store records in the local DB."""
    manager = PolicyManager(source, from_xml=from_xml)
    list_records = manager.parse_lists()
    groups, rules = manager.parse_policy()
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

        current_group_id: str | None = None
        group_condition_index = 0
        group_parent_map: dict[int, int] = {}
        for g in groups:
            if g.get("id"):
                current_group_id = g.get("id")
                record = PolicyGroup(
                    group_id=current_group_id,
                    name=g.get("name"),
                    path=g.get("path"),
                    raw=json.dumps(g, ensure_ascii=False),
                )
                session.merge(record)
                group_condition_index = 0
                group_parent_map = {}
            if current_group_id is None:
                continue
            cond = g.get("condition_raw") or {}
            idx = g.get("condition_index") or (group_condition_index + 1)
            group_condition_index = idx
            cond_record = PolicyCondition(
                rule_id=None,
                group_id=current_group_id,
                index=idx,
                parent_id=group_parent_map.get(g.get("condition_parent_index")),
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
            group_parent_map[idx] = cond_record.id
            values = cond.get("property_values")
            list_ids: list[str] = []
            if isinstance(values, str) and values in manager.list_db.lists:
                list_ids.append(values)
            elif isinstance(values, (list, tuple)):
                for v in values:
                    if isinstance(v, str) and v in manager.list_db.lists:
                        list_ids.append(v)
            for lid in list_ids:
                session.add(
                    ConditionListMap(condition_id=cond_record.id, list_id=lid)
                )

        current_rule_id: str | None = None
        condition_index = 0
        rule_parent_map: dict[int, int] = {}
        for r in rules:
            if r.get("id"):
                current_rule_id = r.get("id")
                record = PolicyRule(
                    rule_id=current_rule_id,
                    name=r.get("name"),
                    group_path=r.get("group_path"),
                    raw=json.dumps(r, ensure_ascii=False),
                )
                session.merge(record)
                condition_index = 0
                rule_parent_map = {}
            if current_rule_id is None:
                continue
            cond = r.get("condition_raw") or {}
            idx = r.get("condition_index") or (condition_index + 1)
            condition_index = idx
            cond_record = PolicyCondition(
                rule_id=current_rule_id,
                group_id=None,
                index=idx,
                parent_id=rule_parent_map.get(r.get("condition_parent_index")),
                prefix=cond.get("prefix"),
                open_bracket=int(cond.get("open_bracket", 0)),
                close_bracket=int(cond.get("close_bracket", 0)),
                property=cond.get("property"),
                operator=cond.get("operator"),
                values=json.dumps(cond.get("property_values"), ensure_ascii=False) if cond.get("property_values") is not None else None,
                result=cond.get("expression_value"),
                raw=json.dumps(cond, ensure_ascii=False),
            )
            session.add(cond_record)
            session.flush()
            rule_parent_map[idx] = cond_record.id
            values = cond.get("property_values")
            list_ids: list[str] = []
            if isinstance(values, str) and values in manager.list_db.lists:
                list_ids.append(values)
            elif isinstance(values, (list, tuple)):
                for v in values:
                    if isinstance(v, str) and v in manager.list_db.lists:
                        list_ids.append(v)
            for lid in list_ids:
                session.add(ConditionListMap(condition_id=cond_record.id, list_id=lid))

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
        print("Usage: policy_db.py <policy_xml>")
        raise SystemExit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        xml_data = f.read()

    save_policy_to_db(xml_data, from_xml=True)
