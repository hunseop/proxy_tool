from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
from datetime import datetime
import os

# 현재 디렉토리의 절대 경로
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "instance", "ppat.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 데이터베이스 초기화
from ppat_db.database import db
from ppat_db.proxy_db import ProxyGroup, ProxyServer
from ppat_db.policy_db import PolicyItem, PolicyList, PolicyConfiguration, PolicyCondition

db.init_app(app)
socketio = SocketIO(app)

# 데이터베이스 테이블 생성
instance_dir = os.path.join(BASE_DIR, 'instance')
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """대시보드 메인 페이지"""
    return render_template('index.html')

@app.route('/api/proxy/groups', methods=['GET', 'POST'])
def proxy_groups():
    """프록시 그룹 관리 API"""
    if request.method == 'GET':
        groups = ProxyGroup.query.all()
        return jsonify([{
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'proxy_count': len(group.proxies)
        } for group in groups])
    
    elif request.method == 'POST':
        data = request.get_json()
        group = ProxyGroup(
            name=data.get('name'),
            description=data.get('description', '')
        )
        db.session.add(group)
        db.session.commit()
        return jsonify({
            'id': group.id,
            'name': group.name,
            'description': group.description
        }), 201

@app.route('/api/proxy/groups/<int:group_id>', methods=['GET', 'PUT', 'DELETE'])
def proxy_group(group_id):
    """프록시 그룹 상세 API"""
    group = ProxyGroup.query.get_or_404(group_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'proxy_count': len(group.proxies)
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        group.name = data.get('name', group.name)
        group.description = data.get('description', group.description)
        db.session.commit()
        return jsonify({
            'id': group.id,
            'name': group.name,
            'description': group.description
        })
    
    elif request.method == 'DELETE':
        db.session.delete(group)
        db.session.commit()
        return '', 204

@app.route('/api/proxy/servers', methods=['GET'])
def get_proxy_servers():
    servers = ProxyServer.query.all()
    return jsonify([{
        'id': server.id,
        'name': server.name,
        'ip_address': server.ip_address,
        'port': server.port,
        'enabled': server.enabled,
        'is_main': server.is_main,
        'group_id': server.group_id,
        'proxy_metadata': server.proxy_metadata
    } for server in servers])

@app.route('/api/proxy/main-appliances', methods=['GET'])
def get_main_appliances():
    main_servers = ProxyServer.query.filter_by(is_main=True).all()
    return jsonify([{
        'id': server.id,
        'name': server.name,
        'ip_address': server.ip_address,
        'port': server.port,
        'enabled': server.enabled,
        'last_update': server.last_update.isoformat() if server.last_update else None,
        'update_status': server.update_status
    } for server in main_servers])

@app.route('/api/proxy/update-policies', methods=['POST'])
def update_all_policies():
    try:
        main_servers = ProxyServer.query.filter_by(is_main=True).all()
        for server in main_servers:
            server.update_status = 'updating'
            server.last_update = datetime.utcnow()
        db.session.commit()

        # TODO: 실제 정책 업데이트 로직 구현
        # 예: policy_manager.update_policies()

        for server in main_servers:
            server.update_status = 'success'
        db.session.commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        for server in main_servers:
            server.update_status = 'error'
        db.session.commit()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/proxy/update-policy/<int:server_id>', methods=['POST'])
def update_single_policy(server_id):
    try:
        server = ProxyServer.query.get_or_404(server_id)
        if not server.is_main:
            return jsonify({'status': 'error', 'message': 'Not a main appliance'}), 400

        server.update_status = 'updating'
        server.last_update = datetime.utcnow()
        db.session.commit()

        # TODO: 실제 정책 업데이트 로직 구현
        # 예: policy_manager.update_single_policy(server)

        server.update_status = 'success'
        db.session.commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        server.update_status = 'error'
        db.session.commit()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 정책 관리 API
@app.route('/api/policies', methods=['GET'])
def get_policies():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')

    query = PolicyItem.query
    if search:
        query = query.filter(
            (PolicyItem.name.ilike(f'%{search}%')) |
            (PolicyItem.type.ilike(f'%{search}%')) |
            (PolicyItem.path.ilike(f'%{search}%'))
        )

    pagination = query.paginate(page=page, per_page=per_page)
    return jsonify({
        'items': [{
            'item_id': item.item_id,
            'name': item.name,
            'type': item.type,
            'path': item.path,
            'enabled': item.enabled
        } for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@app.route('/api/policy/<item_id>')
def get_policy_detail(item_id):
    """정책 상세 정보 조회 API"""
    item = PolicyItem.query.filter_by(item_id=item_id).first_or_404()
    conditions = PolicyCondition.query.filter_by(item_id=item_id).all()
    
    return jsonify({
        'id': item.id,
        'item_id': item.item_id,
        'name': item.name,
        'type': item.item_type,
        'path': item.path,
        'enabled': item.enabled,
        'description': item.description,
        'conditions': [{
            'id': cond.id,
            'prefix': cond.prefix,
            'property': cond.property,
            'operator': cond.operator,
            'values': json.loads(cond.values) if cond.values else None,
            'result': cond.result
        } for cond in conditions]
    })

@app.route('/api/lists', methods=['GET'])
def get_lists():
    lists = PolicyList.query.all()
    return jsonify([{
        'list_id': lst.list_id,
        'name': lst.name,
        'type_id': lst.type_id,
        'classifier': lst.classifier,
        'entries': lst.entries
    } for lst in lists])

@app.route('/api/configurations', methods=['GET'])
def get_configurations():
    configs = PolicyConfiguration.query.all()
    return jsonify([{
        'configuration_id': config.configuration_id,
        'name': config.name,
        'version': config.version,
        'description': config.description
    } for config in configs])

if __name__ == '__main__':
    socketio.run(app, debug=True) 