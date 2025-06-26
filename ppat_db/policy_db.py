"""정책 관리 데이터베이스 모델"""

from .database import db
import json

class PolicyItem(db.Model):
    """정책 아이템 모델"""
    __tablename__ = "policy_items"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    path = db.Column(db.String(500))
    enabled = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(500))
    raw_data = db.Column(db.JSON)

    # 관계 설정
    conditions = db.relationship("PolicyCondition", backref="item", lazy=True)

    def __repr__(self):
        return f'<PolicyItem {self.name}>'

class PolicyCondition(db.Model):
    """정책 조건식 모델"""
    __tablename__ = "policy_conditions"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(100), db.ForeignKey('policy_items.item_id'), nullable=False)
    prefix = db.Column(db.String(50))
    property = db.Column(db.String(100))
    operator = db.Column(db.String(50))
    values = db.Column(db.Text)  # JSON 문자열로 저장
    result = db.Column(db.String(50))

    def __repr__(self):
        return f'<PolicyCondition {self.property} {self.operator}>'

class PolicyList(db.Model):
    """정책 리스트 모델"""
    __tablename__ = "policy_lists"

    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    type_id = db.Column(db.String(50), nullable=False)
    classifier = db.Column(db.String(100))
    entries = db.Column(db.JSON)

    def __repr__(self):
        return f'<PolicyList {self.name}>'

class PolicyConfiguration(db.Model):
    """정책 설정 모델"""
    __tablename__ = "policy_configurations"

    id = db.Column(db.Integer, primary_key=True)
    configuration_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(50))
    description = db.Column(db.String(500))
    settings = db.Column(db.JSON)

    def __repr__(self):
        return f'<PolicyConfiguration {self.name}>'

def save_policy_to_db(policy_source, list_source=None, *, from_xml=False):
    """정책과 리스트 데이터를 파싱하여 로컬 DB에 저장합니다."""
    from policy_module.policy_manager import PolicyManager
    
    manager = PolicyManager(policy_source, list_source, from_xml=from_xml)
    list_records = manager.parse_lists()
    items = manager.parse_policy()
    configs = manager.parse_configurations()

    # 리스트 저장
    for l in list_records:
        rec = PolicyList(
            list_id=l.get("list_id"),
            name=l.get("list_name"),
            type_id=l.get("list_type_id"),
            classifier=l.get("list_classifier"),
            description=l.get("list_description"),
            raw=json.dumps(l, ensure_ascii=False)
        )
        db.session.merge(rec)

    # 정책 아이템 저장
    for item in items:
        if item.get("id"):
            record = PolicyItem(
                item_id=item.get("id"),
                name=item.get("name"),
                type=item.get("type"),
                path=item.get("path") or item.get("group_path"),
                enabled=item.get("enabled"),
                description=item.get("description"),
                raw_data=json.dumps(item, ensure_ascii=False)
            )
            db.session.merge(record)

            # 조건식 저장
            cond = item.get("condition_raw") or {}
            if cond:
                cond_record = PolicyCondition(
                    item_id=item.get("id"),
                    prefix=cond.get("prefix"),
                    property=cond.get("property"),
                    operator=cond.get("operator"),
                    values=json.dumps(cond.get("property_values"), ensure_ascii=False)
                    if cond.get("property_values") is not None
                    else None,
                    result=cond.get("expression_value")
                )
                db.session.add(cond_record)

    # 설정 저장
    for conf in configs:
        cfg = PolicyConfiguration(
            configuration_id=conf.get("id"),
            name=conf.get("name"),
            version=conf.get("version"),
            description=conf.get("description"),
            settings=json.dumps(conf, ensure_ascii=False)
        )
        db.session.merge(cfg)

    db.session.commit()
