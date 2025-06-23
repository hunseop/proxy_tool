import sys, types
sys.modules.setdefault("pandas", types.ModuleType("pandas")).DataFrame = lambda *a, **k: type("DF", (), {"to_excel": lambda self, *args, **kwargs: None})()
sys.modules.setdefault("xmltodict", types.ModuleType("xmltodict")).parse = lambda s: {}

import json
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from policy_module.policy_manager import PolicyManager

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "sample_data", "policy_with_configurations.json")


def load_data():
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_parse_configurations():
    data = load_data()
    pm = PolicyManager(data, from_xml=False)
    configs = pm.parse_configurations()
    assert len(configs) == 1
    conf = configs[0]
    assert conf["id"] == "conf1"
    assert conf["name"] == "Sample Config"
    assert conf["template_id"] == "tmpl"
    assert len(conf["properties"]) == 1
    prop = conf["properties"][0]
    assert prop["key"] == "prop1"
    assert prop["value"] == "val1"


