import sys, types
sys.modules.setdefault("pandas", types.ModuleType("pandas")).DataFrame = lambda *a, **k: type("DF", (), {"to_excel": lambda self, *args, **kwargs: None})()
sys.modules.setdefault("xmltodict", types.ModuleType("xmltodict")).parse = lambda s: {}

import json
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from policy_module.policy_manager import PolicyManager

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "sample_data", "policy_combined_extended.json")


def load_data():
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_parse_extended_policy():
    data = load_data()
    pm = PolicyManager(data, from_xml=False)
    lists = pm.parse_lists()
    groups, rules = pm.parse_policy()

    assert len(lists) == 4
    assert len(groups) == 0
    assert len([r for r in rules if r.get("id")]) == 3
    r3_conditions = [r for r in rules if r.get("id") == "r3"]
    assert len(r3_conditions) == 1
    assert isinstance(r3_conditions[0]["lists_resolved"], list)
    values = r3_conditions[0]["lists_resolved"][0]
    assert isinstance(values, list)
    assert values and values[0]["list_id"] == "list3"
