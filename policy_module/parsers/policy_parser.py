import json
import pandas as pd
import xmltodict
from .condition_parser import ConditionParser

class PolicyParser:
    def __init__(self, source, from_xml: bool = False):
        if from_xml:
            parsed = xmltodict.parse(source)
            self.data = parsed.get("libraryContent", {}).get("ruleGroup", {})
        elif isinstance(source, dict):
            self.data = source.get("libraryContent", {}).get("ruleGroup", {})
        else:
            raise ValueError("Invalid data source provided. Must be dict or XML string.")
        
        self.rulegroup_records = []
        self.rule_records = []

    def parse_condition(self, condition_dict: dict):
        try:
            return ConditionParser(condition_dict).to_rows()   # List[Dict]
        except Exception as e:
            return [{"error": str(e)}]
    
    def parse(self):
        def walk(obj, stack=None):
            if stack is None:
                stack = []
            
            if isinstance(obj, dict):
                is_group = "@name" in obj and ("rules" in obj or "ruleGroups" in obj)
                current_name = obj.get("@name")
            
                # group 또는 rule 여부와 관계없이 condition이 있으면 파싱
                if is_group or "@name" in obj:
                    parsed_conditions = self.parse_condition(obj.get("condition", {}))
                    if not isinstance(parsed_conditions, list):
                        parsed_conditions = [parsed_conditions]
                    if not parsed_conditions:
                        parsed_conditions = [None]

                    for cond in parsed_conditions:
                        cond = cond or {}
                        first = cond.get("index", 1) == 1
                        values = cond.get("property_values")
                        if isinstance(values, (list, tuple)):
                            condition_values = ", ".join(values)
                        elif values is not None:
                            condition_values = str(values)
                        else:
                            condition_values = None
                        
                        record = {
                            "id": obj.get("@id") if first else None,
                            "name": obj.get("@name") if first else None,
                            "enabled": obj.get("@enabled") if first else None,
                            "description": obj.get("description") if first else None,
                            "condition_raw": cond,  # 전체 반환 데이터를 저장
                            "condition_prefix": cond.get("prefix"),
                            "condition_property": cond.get("property"),
                            "condition_operator": cond.get("operator"),
                            "condition_values": condition_values,
                            "condition_result": cond.get("expression_value"),
                            "condition_index": cond.get("index"),
                            "condition_parent_index": cond.get("parent_index"),
                            "path": " > ".join(stack + [current_name] if current_name else stack)
                        }
                        if is_group:
                            record.update({
                                "defaultRights": obj.get("@defaultRights") if first else None,
                                "cycleRequest": obj.get("@cycleRequest") if first else None,
                                "cycleResponse": obj.get("@cycleResponse") if first else None,
                                "cycleEmbeddedObject": obj.get("@cycleEmbeddedObject") if first else None,
                                "cloudSynced": obj.get("@cloudSynced") if first else None,
                                "acElements": str(obj.get("acElements")) if first else None,
                                "type": "group"
                            })
                            self.rule_records.append(record)
                        else:
                            record.update({
                                "actionContainer_raw": str(obj.get("actionContainer")) if first else None,
                                "immediateActions_raw": str(obj.get("immediateActionContainers")) if first else None,
                                "group_path": " > ".join(stack) if first else None,
                                "type": "rule"
                            })
                            self.rule_records.append(record)
                
                if is_group and current_name:
                    stack.append(current_name)
                
                for k, v in obj.items():
                    walk(v, stack)
                
                if is_group and current_name:
                    stack.pop()
                
            elif isinstance(obj, list):
                for item in obj:
                    walk(item, stack)
        
        walk(self.data)
        return self.rule_records
    
    def to_excel(self, rule_path: str):
        df_rules = pd.DataFrame(self.rule_records)
        df_rules.to_excel(rule_path, index=False, engine="openpyxl")
