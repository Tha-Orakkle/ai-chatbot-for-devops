from flask import jsonify
from flask_cors import CORS

from app import app
from app.routes import bp


CORS(
    app,
    resources={r'/*': {'origins': "/*"}},
    supports_credentials=False
)

app.register_blueprint(bp)

# handles 404 errors 
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'message': 'Not Found',
        'status': 404,
        "specification_url": "https://devbot-integration-spec.up.railway.app/api/integration.json",
        "target_url": "https://54.175.31.188/v1/webhook"
    }), 404
