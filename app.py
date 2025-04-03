from flask import Flask, render_template, jsonify, request
import json
import os
from proxy_monitor_core import ResourceMonitor, SessionManager, Config

app = Flask(__name__)

# 설정 파일 경로
CONFIG_FILE = 'config.json'

# 기본 설정값
DEFAULT_CONFIG = {
    'ssh_username': Config.SSH_USERNAME,
    'ssh_password': Config.SSH_PASSWORD,
    'snmp_community': Config.SNMP_COMMUNITY,
    'cpu_threshold': Config.CPU_THRESHOLD,
    'memory_threshold': Config.MEMORY_THRESHOLD
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG
    else:
        return DEFAULT_CONFIG

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        
        # 전역 설정 업데이트
        Config.SSH_USERNAME = config.get('ssh_username', Config.SSH_USERNAME)
        Config.SSH_PASSWORD = config.get('ssh_password', Config.SSH_PASSWORD)
        Config.SNMP_COMMUNITY = config.get('snmp_community', Config.SNMP_COMMUNITY)
        Config.CPU_THRESHOLD = config.get('cpu_threshold', Config.CPU_THRESHOLD)
        Config.MEMORY_THRESHOLD = config.get('memory_threshold', Config.MEMORY_THRESHOLD)
        
        return True
    except:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/resources')
def get_resources():
    try:
        host = request.headers.get('X-Monitor-Host')
        if not host:
            return jsonify({"error": "모니터링할 호스트가 지정되지 않았습니다."}), 400
        
        resource_monitor = ResourceMonitor(host)
        data = resource_monitor.get_resource_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<host>')
def get_sessions(host):
    try:
        session_manager = SessionManager(host)
        sessions = session_manager.get_session()
        return jsonify(sessions.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    return jsonify({"status": "success", "message": "모니터링이 시작되었습니다."})

@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    return jsonify({"status": "success", "message": "모니터링이 중지되었습니다."})

@app.route('/api/config')
def get_config():
    return jsonify(load_config())

@app.route('/api/config', methods=['POST'])
def update_config():
    try:
        config = request.json
        if save_config(config):
            return jsonify({"status": "success", "message": "설정이 저장되었습니다."})
        else:
            return jsonify({"status": "error", "message": "설정 저장 중 오류가 발생했습니다."}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # 앱 시작 시 설정 로드
    current_config = load_config()
    Config.SSH_USERNAME = current_config.get('ssh_username', Config.SSH_USERNAME)
    Config.SSH_PASSWORD = current_config.get('ssh_password', Config.SSH_PASSWORD)
    Config.SNMP_COMMUNITY = current_config.get('snmp_community', Config.SNMP_COMMUNITY)
    Config.CPU_THRESHOLD = current_config.get('cpu_threshold', Config.CPU_THRESHOLD)
    Config.MEMORY_THRESHOLD = current_config.get('memory_threshold', Config.MEMORY_THRESHOLD)
    
    app.run(debug=True, host='0.0.0.0', port=5001) 