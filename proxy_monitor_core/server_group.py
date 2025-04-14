from flask import Blueprint, jsonify, request
from .models import Session, Server, ServerGroup
from sqlalchemy.exc import IntegrityError

bp = Blueprint('server_group', __name__, url_prefix='/api')

@bp.route('/servers', methods=['GET'])
def get_servers():
    try:
        with Session() as session:
            servers = session.query(Server).all()
            return jsonify({
                'success': True,
                'servers': [{
                    'id': server.id,
                    'address': server.address,
                    'description': server.description,
                    'groups': [group.name for group in server.groups]
                } for server in servers]
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/servers', methods=['POST'])
def create_server():
    try:
        data = request.get_json()
        address = data.get('address')
        description = data.get('description', '')
        group_ids = data.get('groups', [])  # 선택사항

        if not address:
            return jsonify({'success': False, 'error': '서버 주소는 필수입니다.'}), 400

        with Session() as session:
            # 중복 주소 확인
            existing = session.query(Server).filter_by(address=address).first()
            if existing:
                return jsonify({'success': False, 'error': '이미 존재하는 서버 주소입니다.'}), 400

            # 서버 생성
            server = Server(address=address, description=description)
            
            # 그룹이 선택된 경우에만 처리
            if group_ids:
                groups = session.query(ServerGroup).filter(ServerGroup.id.in_(group_ids)).all()
                server.groups.extend(groups)

            session.add(server)
            session.commit()

            return jsonify({
                'success': True,
                'server': {
                    'id': server.id,
                    'address': server.address,
                    'description': server.description,
                    'groups': [group.name for group in server.groups]
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/server-groups', methods=['GET'])
def get_groups():
    try:
        with Session() as session:
            groups = session.query(ServerGroup).all()
            return jsonify({
                'success': True,
                'groups': [{
                    'id': group.id,
                    'name': group.name,
                    'description': group.description,
                    'servers': [server.address for server in group.servers]
                } for group in groups]
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/server-groups', methods=['POST'])
def create_group():
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        server_ids = data.get('servers', [])  # 선택사항

        if not name:
            return jsonify({'success': False, 'error': '그룹 이름은 필수입니다.'}), 400

        with Session() as session:
            # 중복 이름 확인
            existing = session.query(ServerGroup).filter_by(name=name).first()
            if existing:
                return jsonify({'success': False, 'error': '이미 존재하는 그룹 이름입니다.'}), 400

            # 그룹 생성
            group = ServerGroup(name=name, description=description)
            
            # 서버가 선택된 경우에만 처리
            if server_ids:
                servers = session.query(Server).filter(Server.id.in_(server_ids)).all()
                group.servers.extend(servers)

            session.add(group)
            session.commit()

            return jsonify({
                'success': True,
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'description': group.description,
                    'servers': [server.address for server in group.servers]
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/servers/<int:server_id>', methods=['PUT'])
def update_server(server_id):
    try:
        data = request.get_json()
        description = data.get('description')
        group_ids = data.get('groups', [])

        with Session() as session:
            server = session.query(Server).get(server_id)
            if not server:
                return jsonify({'success': False, 'error': '서버를 찾을 수 없습니다.'}), 404

            if description is not None:
                server.description = description

            if group_ids is not None:
                groups = session.query(ServerGroup).filter(ServerGroup.id.in_(group_ids)).all()
                server.groups = groups

            session.commit()

            return jsonify({
                'success': True,
                'server': {
                    'id': server.id,
                    'address': server.address,
                    'description': server.description,
                    'groups': [group.name for group in server.groups]
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/server-groups/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    try:
        data = request.get_json()
        description = data.get('description')
        server_ids = data.get('servers', [])

        with Session() as session:
            group = session.query(ServerGroup).get(group_id)
            if not group:
                return jsonify({'success': False, 'error': '그룹을 찾을 수 없습니다.'}), 404

            if description is not None:
                group.description = description

            if server_ids is not None:
                servers = session.query(Server).filter(Server.id.in_(server_ids)).all()
                group.servers = servers

            session.commit()

            return jsonify({
                'success': True,
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'description': group.description,
                    'servers': [server.address for server in group.servers]
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/servers/<int:server_id>', methods=['DELETE'])
def delete_server(server_id):
    try:
        with Session() as session:
            server = session.query(Server).get(server_id)
            if not server:
                return jsonify({'success': False, 'error': '서버를 찾을 수 없습니다.'}), 404

            session.delete(server)
            session.commit()

            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/server-groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    try:
        with Session() as session:
            group = session.query(ServerGroup).get(group_id)
            if not group:
                return jsonify({'success': False, 'error': '그룹을 찾을 수 없습니다.'}), 404

            session.delete(group)
            session.commit()

            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 