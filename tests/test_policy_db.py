import sys
import types
import pytest

# Patch external dependencies used in policy_module
sys.modules.setdefault("pandas", types.ModuleType("pandas")).DataFrame = lambda *a, **k: type("DF", (), {"to_excel": lambda self, *args, **kwargs: None})()
sys.modules.setdefault("xmltodict", types.ModuleType("xmltodict")).parse = lambda s: {}

sqlalchemy = pytest.importorskip("sqlalchemy")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import ppat_db.policy_db as pdb
import json
import os


def setup_function(_):
    pdb.engine = create_engine("sqlite:///:memory:")
    pdb.Session = sessionmaker(bind=pdb.engine)
    pdb.Base.metadata.create_all(pdb.engine)


def test_save_policy_with_group_conditions():
    policy = {
        "libraryContent": {
            "ruleGroup": {
                "@id": "g1",
                "@name": "Group1",
                "condition": {
                    "expressions": {
                        "conditionExpression": {
                            "@prefix": "URL",
                            "@operatorId": "equals",
                            "@openingBracketCount": "1",
                            "@closingBracketCount": "0",
                            "propertyInstance": {
                                "@propertyId": "URL.Host",
                                "parameters": {
                                    "entry": {
                                        "string": "domain",
                                        "parameter": {
                                            "@valueType": "value",
                                            "value": {"stringValue": {"@value": "example.com"}}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "rules": {
                    "rule": {
                        "@id": "r1",
                        "@name": "Rule1",
                        "condition": {
                            "expressions": {
                                "conditionExpression": {
                                    "@prefix": "URL",
                                    "@operatorId": "equals",
                                    "@openingBracketCount": "0",
                                    "@closingBracketCount": "1",
                                    "propertyInstance": {
                                        "@propertyId": "URL.Host",
                                        "parameters": {
                                            "entry": {
                                                "string": "domain",
                                                "parameter": {
                                                    "@valueType": "value",
                                                    "value": {"stringValue": {"@value": "example.net"}}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    pdb.save_policy_to_db(policy)

    with pdb.Session() as session:
        groups = session.query(pdb.PolicyGroup).all()
        rules = session.query(pdb.PolicyRule).all()
        conds = session.query(pdb.PolicyCondition).order_by(pdb.PolicyCondition.index).all()

        assert len(groups) == 1
        assert len(rules) == 1
        assert len(conds) == 2

        g_cond = conds[0]
        r_cond = conds[1]

        assert g_cond.group_id == "g1"
        assert g_cond.open_bracket == 1
        assert g_cond.close_bracket == 0

        assert r_cond.rule_id == "r1"
        assert r_cond.open_bracket == 0
        assert r_cond.close_bracket == 1


def test_save_policy_configurations():
    path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "policy_with_configurations.json")
    with open(path, "r", encoding="utf-8") as f:
        policy = json.load(f)

    pdb.save_policy_to_db(policy)

    with pdb.Session() as session:
        configs = session.query(pdb.PolicyConfiguration).all()
        assert len(configs) == 1
        conf = configs[0]
        assert conf.configuration_id == "conf1"
        assert conf.name == "Sample Config"
