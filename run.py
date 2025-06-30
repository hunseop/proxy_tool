import warnings
from app import create_app
from app.extensions import socketio

warnings.filterwarnings('ignore', message='.*TripleDES.*')

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)
