import xmltodict

class ConfigurationsParser:
    def __init__(self, source, from_xml: bool = False) -> None:
        if from_xml:
            self.data = xmltodict.parse(source)
        elif isinstance(source, dict):
            self.data = source
        else:
            raise ValueError("Invalid data source provided. Must be dict or XML string.")
        self.records = []

    @staticmethod
    def parse_properties(conf: dict) -> list[dict]:
        props = conf.get("configurationProperties", {}).get("configurationProperty")
        result = []
        if props is None:
            return result
        if not isinstance(props, list):
            props = [props]
        for p in props:
            if not isinstance(p, dict):
                continue
            result.append(
                {
                    "key": p.get("@key"),
                    "value": p.get("@value"),
                    "type": p.get("@type"),
                    "encrypted": p.get("@encrypted"),
                    "list_type": p.get("@listType"),
                }
            )
        return result

    @staticmethod
    def ensure_list(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def parse(self):
        configs = self.data.get("libraryContent", {}).get("configurations", {}).get("configuration")
        for conf in self.ensure_list(configs):
            if not isinstance(conf, dict):
                continue
            record = {
                "id": conf.get("@id"),
                "name": conf.get("@name"),
                "version": conf.get("@version"),
                "mwg_version": conf.get("@mwg-version"),
                "template_id": conf.get("@templateId"),
                "target_id": conf.get("@targetId"),
                "description": conf.get("description"),
                "properties": self.parse_properties(conf),
                "raw": conf,
            }
            self.records.append(record)
        return self.records
