"""Utility classes to link policy conditions with list entries.

This module keeps the original parsing logic intact. It provides helper
classes to store list entries and resolve list identifiers in policy
records parsed by :class:`PolicyParser`.
"""

from typing import Any, Dict, Iterable, List, Optional

from .lists_parser import ListsParser
from .policy_parser import PolicyParser


class ListDatabase:
    """Simple in-memory database for list entries."""

    def __init__(self) -> None:
        self.lists: Dict[str, List[Dict[str, Any]]] = {}

    def load(self, records: Iterable[Dict[str, Any]]) -> None:
        for rec in records:
            list_id = rec.get("list_id")
            if not list_id:
                continue
            self.lists.setdefault(list_id, []).append(rec)

    def get(self, list_id: str) -> Optional[List[Dict[str, Any]]]:
        return self.lists.get(list_id)


class PolicyManager:
    """Combine policy parsing with list resolution."""

    def __init__(
        self,
        policy_source: Any,
        list_source: Any | None = None,
        *,
        from_xml: bool = False,
    ) -> None:
        self.policy_source = policy_source
        self.list_source = list_source if list_source is not None else policy_source
        self.from_xml = from_xml
        self.list_db = ListDatabase()
        self.policy_parser = PolicyParser(policy_source, from_xml=from_xml)

    def parse_lists(self) -> List[Dict[str, Any]]:
        parser = ListsParser(self.list_source, from_xml=self.from_xml)
        records = parser.parse()
        self.list_db.load(records)
        return records

    def parse_policy(self) -> tuple:
        rulegroups, rules = self.policy_parser.parse()
        self._resolve(rulegroups)
        self._resolve(rules)
        return rulegroups, rules

    def _resolve(self, records: Iterable[Dict[str, Any]]) -> None:
        for rec in records:
            cond_raw = rec.get("condition_raw")
            if not isinstance(cond_raw, dict):
                continue
            values = cond_raw.get("property_values")
            if not values:
                continue
            rec["lists_resolved"] = self._resolve_values(values)

    def _resolve_values(self, values: Any) -> Any:
        if isinstance(values, str):
            return self.list_db.get(values) or values
        if isinstance(values, (list, tuple)):
            resolved = []
            for val in values:
                if isinstance(val, str) and val in self.list_db.lists:
                    resolved.append(self.list_db.get(val))
                else:
                    resolved.append(val)
            return resolved
        return values
