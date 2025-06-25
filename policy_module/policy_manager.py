"""Policy parsing helper utilities."""

from typing import Any, Dict, Iterable, List, Optional

from .parsers.lists_parser import ListsParser
from .parsers.policy_parser import PolicyParser
from .parsers.configurations_parser import ConfigurationsParser


class ListDatabase:
    """간단한 메모리 리스트 저장소."""

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
    """단일 XML/JSON 소스로부터 정책 데이터를 추출한다."""

    def __init__(self, source: Any, *, from_xml: bool = False) -> None:
        self.source = source
        self.from_xml = from_xml
        self.list_db = ListDatabase()
        self.policy_parser = PolicyParser(source, from_xml=from_xml)

    def parse_lists(self) -> List[Dict[str, Any]]:
        parser = ListsParser(self.source, from_xml=self.from_xml)
        records = parser.parse()
        self.list_db.load(records)
        return records

    def parse_configurations(self) -> List[Dict[str, Any]]:
        parser = ConfigurationsParser(self.source, from_xml=self.from_xml)
        return parser.parse()

    def parse_policy(self) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        records = self.policy_parser.parse()
        groups = [r for r in records if r.get("type") == "group"]
        rules = [r for r in records if r.get("type") == "rule"]
        self._resolve(groups)
        self._resolve(rules)
        return groups, rules

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
