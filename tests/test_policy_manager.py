import sys, types
sys.modules.setdefault("pandas", types.ModuleType("pandas")).DataFrame = lambda *a, **k: type("DF", (), {"to_excel": lambda self, *args, **kwargs: None})()
sys.modules.setdefault("xmltodict", types.ModuleType("xmltodict")).parse = lambda s: {}

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from policy_module.policy_manager import PolicyManager

lists_data = {
    "libraryContent": {
        "lists": {
            "entry": [
                {
                    "list": {
                        "@name": "Test List",
                        "@id": "list1",
                        "@typeId": "A",
                        "@classifier": "string",
                        "description": "desc",
                        "content": {
                            "listEntry": [
                                {"@id": "entry1", "value": "example.com"},
                                {"@id": "entry2", "value": "example.org"},
                            ]
                        },
                    }
                }
            ]
        }
    }
}

policy_data = {
    "libraryContent": {
        "ruleGroup": {
            "@id": "g1",
            "@name": "Group1",
            "rules": {
                "rule": {
                    "@id": "r1",
                    "@name": "Rule1",
                    "condition": {
                        "expressions": {
                            "conditionExpression": {
                                "@prefix": "URL",
                                "@operatorId": "equals",
                                "propertyInstance": {
                                    "@propertyId": "URL.Host",
                                    "parameters": {
                                        "entry": {
                                            "string": "domain",
                                            "parameter": {
                                                "@valueType": "value",
                                                "value": {
                                                    "listValue": {"@id": "list1"}
                                                },
                                            },
                                        }
                                    },
                                },
                            }
                        }
                    },
                }
            },
        }
    }
}

combined_data = {
    "libraryContent": {
        "ruleGroup": policy_data["libraryContent"]["ruleGroup"],
        "lists": lists_data["libraryContent"]["lists"],
    }
}

lists_data_empty = {
    "libraryContent": {
        "lists": {
            "entry": [
                {
                    "list": {
                        "@name": "Test List",
                        "@id": "list1",
                        "@typeId": "A",
                        "@classifier": "string",
                        "description": "desc",
                        "content": {"listEntry": []},
                    }
                }
            ]
        }
    }
}

def test_resolve_lists():
    data = {
        "libraryContent": {
            "ruleGroup": policy_data["libraryContent"]["ruleGroup"],
            "lists": lists_data["libraryContent"]["lists"],
        }
    }
    pm = PolicyManager(data, from_xml=False)
    pm.parse_lists()
    groups, rules = pm.parse_policy()
    assert rules and isinstance(rules[0].get("lists_resolved"), list)
    values = [entry.get("value") for entry in rules[0]["lists_resolved"]]
    assert values == ["example.com", "example.org"]


def test_resolve_lists_from_combined():
    pm = PolicyManager(combined_data, from_xml=False)
    pm.parse_lists()
    groups, rules = pm.parse_policy()
    assert rules and isinstance(rules[0]["lists_resolved"], list)
    values = [e.get("value") for e in rules[0]["lists_resolved"]]
    assert values == ["example.com", "example.org"]

def test_empty_list_entries():
    data = {
        "libraryContent": {
            "ruleGroup": policy_data["libraryContent"]["ruleGroup"],
            "lists": lists_data_empty["libraryContent"]["lists"],
        }
    }
    pm = PolicyManager(data, from_xml=False)
    records = pm.parse_lists()
    assert len(records) == 1
    assert records[0]["list_id"] == "list1"
    groups, rules = pm.parse_policy()
    assert rules[0]["lists_resolved"][0]["list_id"] == "list1"
