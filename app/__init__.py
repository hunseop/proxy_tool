from flask import Flask, jsonify, render_template
import os
from .extensions import db, socketio
from config import Config


def create_app(config_object=None):
    if config_object is None:
        config_object = Config
    instance_path = Config.INSTANCE_PATH
    os.makedirs(instance_path, exist_ok=True)

    app = Flask(__name__, template_folder='../templates', instance_path=instance_path)
    app.config.from_object(config_object)

    db.init_app(app)
    socketio.init_app(app)

    # 애플리케이션이 시작될 때 테이블을 생성한다
    with app.app_context():
        db.create_all()

    from .proxy import bp as proxy_bp
    from .monitoring import bp as monitoring_bp
    app.register_blueprint(proxy_bp, url_prefix='/api/proxy')
    app.register_blueprint(monitoring_bp, url_prefix='/api/monitoring')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api')
    def api_index():
        return jsonify({'message': 'PPAT API running'})

    return app
