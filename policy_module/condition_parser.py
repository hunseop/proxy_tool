from typing import Any, Dict, List, Optional, Union

class ConditionParser:
    def __init__(self, condition: Optional[Dict[str, Any]]) -> None:
        self.condition = condition
        self.parsed = self.parse_condition(condition)

    @classmethod
    def ensure_list(cls, value: Union[Dict, List, None]) -> List:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def parse_condition(self, condition: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse the expressions of a condition into a list of rows.

        The resulting rows include ``index`` and ``parent_index`` to allow
        reconstruction of nested boolean logic. ``index`` starts at ``1`` for
        each condition and ``parent_index`` refers to the ``index`` of the
        expression that opened the current bracket scope.
        """

        if not condition:
            return []

        container = condition.get("expressions")
        if not isinstance(container, dict):
            return []

        raw_exprs = self.ensure_list(container.get("conditionExpression"))

        rows: List[Dict[str, Any]] = []
        stack: List[int] = []

        for raw in raw_exprs:
            if not isinstance(raw, dict):
                continue
            row = self.parse_expression(raw)
            index = len(rows) + 1
            row["index"] = index
            row["parent_index"] = stack[-1] if stack else None
            rows.append(row)

            for _ in range(row.get("open_bracket", 0)):
                stack.append(index)
            for _ in range(row.get("close_bracket", 0)):
                if stack:
                    stack.pop()

        return rows
    
    def parse_expression(self, expr: Dict[str, Any]) -> Dict[str, Any]:
        prop_instance = expr.get("propertyInstance", {})
        has_prop_parameters = "parameters" in prop_instance

        property_parameters = self.parse_property_parameters(
            prop_instance.get("parameters", {})
        ) if has_prop_parameters else []

        expression_parameter = self.parse_expression_parameter(expr, has_prop_parameters)

        if not expression_parameter and "parameter" in prop_instance:
            expression_parameter = self.parse_single_property_parameter(prop_instance["parameter"])
        
        values = [
            v.get("value") if v["value_kind"] == "string" else v.get("list_id")
            for v in property_parameters
            if v["value_kind"] in ("string", "list")
        ]

        if expression_parameter and expression_parameter.get("mode") == "value":
            if expression_parameter.get("value_kind") == "string":
                values.append(expression_parameter.get("value"))
            elif expression_parameter.get("value_kind") == "list":
                values.append(expression_parameter.get("list_id"))

        return {
            "prefix": expr.get("@prefix"),
            "open_bracket": int(expr.get("@openingBracketCount", 0)),
            "close_bracket": int(expr.get("@closingBracketCount", 0)),
            "property": prop_instance.get("@propertyId", "<unknown>"),
            "operator": expr.get("@operatorId", "equals"),
            "property_values": tuple(values) if len(values) > 1 else (values[0] if values else None),
            "expression_value": expression_parameter.get("value") if expression_parameter else None,
            "expression_mode": expression_parameter.get("mode") if expression_parameter else None
        }
    
    def parse_single_property_parameter(self, param: Dict[str, Any]) -> Dict[str, Any]:
        value_type = param.get("@valueType")
        value = param.get("value", {})

        if "stringValue" in value:
            sv = value["stringValue"]
            return {
                "mode": "value",
                "value_type": value_type,
                "value_kind": "string",
                "value": sv.get("@value"),
                "modifier": sv.get("@stringModifier"),
                "type_id": sv.get("@typeId")
            }
        elif "listValue" in value:
            lv = value["listValue"]
            return {
                "mode": "value",
                "value_type": value_type,
                "value_kind": "list",
                "list_id": lv.get("@id")
            }
        elif "propertyInstance" in value:
            nested_prop = value["propertyInstance"]
            nested_params = self.parse_property_parameters(
                nested_prop.get("parameters", {})
            )
            nested_param = (
                self.parse_single_property_parameter(nested_prop["parameter"])
                if "parameter" in nested_prop
                else None
            )
            attributes = {
                k.lstrip("@"): v
                for k, v in nested_prop.items()
                if k.startswith("@") and k not in {"@propertyId"}
            }
            return {
                "mode": "nested_property",
                "value_type": value_type,
                "property": nested_prop.get("@propertyId"),
                "attributes": attributes,
                "parameters": nested_params,
                "parameter": nested_param,
            }
        else:
            return {
                "mode": "unknown",
                "value_type": value_type,
                "raw_value": value
            }
    
    def parse_property_parameters(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        entries = self.ensure_list(parameters.get("entry"))
        results = []

        for entry in entries:
            if isinstance(entry, str):
                # bare string entry
                results.append({"key": None, "value_type": None, "value_kind": "string", "value": entry})
                continue
            if not isinstance(entry, dict):
                continue

            key = entry.get("string")
            param = entry.get("parameter", {})
            value_type = param.get("@valueType")
            value = param.get("value", {})

            if "propertyInstance" in value:
                nested_prop = value["propertyInstance"]
                nested_params = self.parse_property_parameters(
                    nested_prop.get("parameters", {})
                )
                nested_param = (
                    self.parse_single_property_parameter(nested_prop["parameter"])
                    if "parameter" in nested_prop
                    else None
                )

                attributes = {
                    k.lstrip("@"): v
                    for k, v in nested_prop.items()
                    if k.startswith("@") and k not in {"@propertyId"}
                }

                results.append({
                    "key": key,
                    "value_type": value_type,
                    "value_kind": "nested_property",
                    "property": nested_prop.get("@propertyId"),
                    "attributes": attributes,
                    "parameters": nested_params,
                    "parameter": nested_param,
                })
            elif "stringValue" in value:
                sv = value["stringValue"]
                results.append({
                    "key": key,
                    "value_type": value_type,
                    "value_kind": "string",
                    "value": sv.get("@value"),
                    "modifier": sv.get("@stringModifier"),
                    "type_id": sv.get("@typeId")
                })
            elif "listValue" in value:
                lv = value["listValue"]
                results.append({
                    "key": key,
                    "value_type": value_type,
                    "value_kind": "list",
                    "list_id": lv.get("@id")
                })
            else:
                results.append({
                    "key": key,
                    "value_type": value_type,
                    "value_kind": "unknown",
                    "raw_value": value
                })
        
        return results
    
    def parse_expression_parameter(self, expr: Dict[str, Any], has_prop_parameters: bool) -> Optional[Dict[str, Any]]:
        param = expr.get("parameter")
        if not param:
            return None
        
        value = param.get("value")

        if value:
            if "propertyInstance" in value:
                nested_prop = value["propertyInstance"]
                attributes = {
                    k.lstrip("@"): v
                    for k, v in nested_prop.items()
                    if k.startswith("@") and k not in {"@propertyId"}
                }
                return {
                    "mode": "nested_property",
                    "property": nested_prop.get("@propertyId"),
                    "attributes": attributes,
                    "parameters": self.parse_property_parameters(
                        nested_prop.get("parameters", {})
                    ),
                    "parameter": self.parse_single_property_parameter(
                        nested_prop["parameter"]
                    )
                    if "parameter" in nested_prop
                    else None,
                }
            if "stringValue" in value:
                sv = value["stringValue"]
                return {
                    "mode": "value",
                    "value_kind": "string",
                    "value": sv.get("@value"),
                    "modifier": sv.get("@stringModifier"),
                    "type_id": sv.get("@typeId")
                }
            if "listValue" in value:
                lv = value["listValue"]
                return {
                    "mode": "value",
                    "value_kind": "list",
                    "list_id": lv.get("@id")
                }
        
        return {
            "mode": "meta",
            "value_type": param.get("@valueType"),
            "value_id": param.get("@valueId"),
            "type_id": param.get("@typeId"),
            "value": param.get("@valueId")
        }
    
    def to_rows(self) -> List[Dict[str, Any]]:
        return self.parsed
