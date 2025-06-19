"""정책 데이터를 DB에 저장하는 도구 모듈."""

import json
from typing import Any

from proxy_monitor_core.models import Session, PolicyGroup, PolicyRule
from .policy_manager import PolicyManager


def save_policy_to_db(policy_source: Any, list_source: Any, *, from_xml: bool = False) -> None:
    """PolicyManager를 사용해 정책을 파싱하고 DB에 저장한다."""
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
    import json
    import sys
    if len(sys.argv) < 3:
        print("Usage: policy_db.py <policy_json> <lists_json>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        policy = json.load(f)
    with open(sys.argv[2], "r", encoding="utf-8") as f:
        lists = json.load(f)
    save_policy_to_db(policy, lists)

