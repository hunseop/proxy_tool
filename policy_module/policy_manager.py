"""Utility classes to link policy conditions with list entries.

This module keeps the original parsing logic intact. It provides helper
classes to store list entries and resolve list identifiers in policy
records parsed by :class:`PolicyParser`.
"""

from typing import Any, Dict, Iterable, List, Optional

from .parsers.lists_parser import ListsParser
from .parsers.policy_parser import PolicyParser
from .parsers.configurations_parser import ConfigurationsParser


class PolicyManager:
    """Combine policy parsing with list resolution."""

    def __init__(
        self,
        source: Any,
        *,
        from_xml: bool = False,
    ) -> None:
        """Initialize PolicyManager.
        
        Args:
            source: The source data (XML or JSON) containing policy, lists and configurations
            from_xml: Whether the source is in XML format
        """
        self.source = source
        self.from_xml = from_xml
        self.lists = {}  # Dictionary to store list entries
        self.policy_parser = PolicyParser(source, from_xml=from_xml)

    def parse_lists(self) -> List[Dict[str, Any]]:
        """Parse and store list entries from source.
        
        Returns:
            List of parsed list records
        """
        parser = ListsParser(self.source, from_xml=self.from_xml)
        records = parser.parse()
        # Store list entries in dictionary for quick lookup
        for rec in records:
            list_id = rec.get("list_id")
            if list_id:
                self.lists.setdefault(list_id, []).append(rec)
        return records

    def parse_configurations(self) -> List[Dict[str, Any]]:
        """Parse configuration entries from source.
        
        Returns:
            List of parsed configuration records
        """
        parser = ConfigurationsParser(self.source, from_xml=self.from_xml)
        return parser.parse()

    def parse_policy(self) -> tuple:
        """Parse policy entries and resolve list references.
        
        Returns:
            Tuple of (rulegroups, rules) with resolved list references
        """
        rulegroups, rules = self.policy_parser.parse()
        self._resolve(rulegroups)
        self._resolve(rules)
        return rulegroups, rules

    def _resolve(self, records: Iterable[Dict[str, Any]]) -> None:
        """Resolve list references in policy records.
        
        Args:
            records: Policy records to resolve list references in
        """
        for rec in records:
            cond_raw = rec.get("condition_raw")
            if not isinstance(cond_raw, dict):
                continue
            values = cond_raw.get("property_values")
            if not values:
                continue
            rec["lists_resolved"] = self._resolve_values(values)

    def _resolve_values(self, values: Any) -> Any:
        """Resolve list references to actual list entries.
        
        Args:
            values: List reference(s) to resolve
            
        Returns:
            Resolved list entries or original value if not a list reference
        """
        if isinstance(values, str):
            return self.lists.get(values, values)
        if isinstance(values, (list, tuple)):
            return [
                self.lists.get(val, val) if isinstance(val, str) else val
                for val in values
            ]
        return values
