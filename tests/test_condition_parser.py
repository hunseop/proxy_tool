import sys, types
sys.modules.setdefault("pandas", types.ModuleType("pandas")).DataFrame = lambda *a, **k: None
sys.modules.setdefault("xmltodict", types.ModuleType("xmltodict")).parse = lambda s: {}
import os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from policy_module.parsers.condition_parser import ConditionParser


def test_nested_parent_indexes():
    cond = {
        "expressions": {
            "conditionExpression": [
                {
                    "@openingBracketCount": "1",
                    "@operatorId": "equals",
                    "propertyInstance": {"@propertyId": "A"}
                },
                {
                    "@closingBracketCount": "1",
                    "@operatorId": "equals",
                    "propertyInstance": {"@propertyId": "B"}
                }
            ]
        }
    }
    rows = ConditionParser(cond).to_rows()
    assert rows[0]["index"] == 1
    assert rows[0]["parent_index"] is None
    assert rows[1]["index"] == 2
    assert rows[1]["parent_index"] == 1


def test_expression_parameter_value_capture():
    cond = {
        "expressions": {
            "conditionExpression": {
                "@operatorId": "equals",
                "propertyInstance": {"@propertyId": "URL.Host"},
                "parameter": {
                    "@valueType": "value",
                    "value": {"listValue": {"@id": "list1"}}
                },
            }
        }
    }
    rows = ConditionParser(cond).to_rows()
    assert rows[0]["property_values"] == "list1"


def test_expression_parameter_string_capture():
    cond = {
        "expressions": {
            "conditionExpression": {
                "@operatorId": "equals",
                "propertyInstance": {"@propertyId": "URL.Host"},
                "parameter": {
                    "@valueType": "value",
                    "value": {"stringValue": {"@value": "example.com"}}
                },
            }
        }
    }
    rows = ConditionParser(cond).to_rows()
    assert rows[0]["property_values"] == "example.com"
