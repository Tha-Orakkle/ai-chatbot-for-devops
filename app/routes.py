from flask import Blueprint, jsonify, request
import threading
import os

from .integration_config import SPECIFICATION
from .helpers import call_request_handler_in_thread


CHANNEL_WEBHOOK_BASE_URL = "https://ping.telex.im/v1/webhooks"

bp = Blueprint('routes', __name__)


# ROUTES

# handles request to the integration specification
@bp.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "DevBot Telex Integration",
        "specification_url": "https://devbot-integration-spec.up.railway.app/api/integration.json",
        "target_url": "https://54.175.31.188/v1/webhook" 
    })


# handles request to the integration specification
@bp.route('/v1/integration.json', methods=['GET'])
def get_integration_config():
    """
    Returns json specification for Telex integration
    """
    return jsonify(SPECIFICATION)


# handles the request from telex.
@bp.route('/v1/webhook', methods=['POST'])
async def target():
    """
    creates a new thread and handles all tasks in the new thread.
    retrives payload from request and passes it to the task that will
    be executed asynchronously in new thread
    """
    json_data = request.get_json()
    channel_url = os.getenv("CHANNEL_URL")

    text = json_data.get('message').strip()
    if not text.startswith('/devbot'): # only respond to task prefixed with /devops
        return '', 204
    
    text = text[7:].strip()
    settings = {x['label']: x['default'] for x in json_data['settings']}

    #start new thread
    thread = threading.Thread(
        target=call_request_handler_in_thread,
        args=(channel_url, text, settings))
    thread.start()
    
    return jsonify({
        "status": "request processing"})
