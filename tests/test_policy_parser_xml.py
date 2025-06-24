import sys, types
sys.modules.setdefault("pandas", types.ModuleType("pandas")).DataFrame = lambda *a, **k: type("DF", (), {"to_excel": lambda self, *args, **kwargs: None})()

_called = {}

def fake_parse(xml_str):
    _called["xml"] = xml_str
    return combined_data

xmltodict = types.ModuleType("xmltodict")
xmltodict.parse = fake_parse
sys.modules["xmltodict"] = xmltodict

import importlib

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import policy_module.policy_parser as pp
pp = importlib.reload(pp)
from policy_module.policy_parser import PolicyParser

combined_data = {
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
                                                "value": {"listValue": {"@id": "list1"}}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
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
                                {"@id": "entry2", "value": "example.org"}
                            ]
                        }
                    }
                }
            ]
        }
    }
}

XML_INPUT = "<policy/>"

def test_parse_policy_from_xml():
    parser = PolicyParser(XML_INPUT, from_xml=True)
    groups, rules = parser.parse()
    assert _called.get("xml") == XML_INPUT
    assert len(groups) == 1
    assert groups[0]["id"] == "g1"
    assert len(rules) == 1
    assert rules[0]["name"] == "Rule1"
