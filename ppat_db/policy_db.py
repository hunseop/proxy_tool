"""Policy parsing results database utilities."""

import json
from typing import Any

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from proxy_module.policy_manager import PolicyManager

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
    lists_resolved = Column(Text)


engine = create_engine("sqlite:///policy.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def save_policy_to_db(policy_source: Any, list_source: Any, *, from_xml: bool = False) -> None:
    """Parse policy and list data then store to the local DB."""
    manager = PolicyManager(policy_source, list_source, from_xml=from_xml)
    manager.parse_lists()
    groups, rules = manager.parse_policy()

    with Session() as session:
        for g in groups:
            record = PolicyGroup(
                group_id=g.get("id"),
                name=g.get("name"),
                path=g.get("path"),
                raw=json.dumps(g, ensure_ascii=False),
            )
            session.merge(record)

        for r in rules:
            record = PolicyRule(
                rule_id=r.get("id"),
                name=r.get("name"),
                group_path=r.get("group_path"),
                raw=json.dumps(r, ensure_ascii=False),
                lists_resolved=json.dumps(r.get("lists_resolved"), ensure_ascii=False),
            )
            session.merge(record)

        session.commit()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: policy_db.py <policy_json> <lists_json>")
        raise SystemExit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        policy = json.load(f)
    with open(sys.argv[2], "r", encoding="utf-8") as f:
        lists = json.load(f)

    save_policy_to_db(policy, lists)
