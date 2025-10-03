from flask import Flask
from .routes import bp as routes_bp
from .models import WipeRequest, CertVerifyRequest
from ..src.utils import load_config

app = Flask(__name__)
config = load_config()

app.register_blueprint(routes_bp, url_prefix='/api/v1')

@app.route('/')
def home():
    return {"message": "Secure Wipe API", "version": "0.1.0"}

if __name__ == '__main__':
    host = config['api']['host']
    port = config['api']['port']
    app.run(host=host, port=port, debug=True)