from flask import Blueprint, jsonify, request
import aiohttp, asyncio

from .integration_config import integration_config
from .helpers import request_handler

CHANNEL_WEBHOOK_BASE_URL = "https://ping.telex.im/v1/webhooks"

bp = Blueprint('routes', __name__)

# ROUTES

# handles request to the integration specification
@bp.route('/integration.json', methods=['GET'])
def get_integration_config():
    return jsonify(integration_config)


# handles the request from telex
@bp.route('/webhook', methods=['POST'])
async def target():
    json_data = request.get_json()
    channel_url =  f"{CHANNEL_WEBHOOK_BASE_URL}/{json_data.get("channel_id")}"

    text = json_data.get('message').strip()
    if text[:7] != '/devops': return '', 204

    text = text[7:].strip()
    settings = {x['label']: x['default'] for x in json_data['settings']}

    asyncio.create_task(request_handler(channel_url, text, settings))

    return jsonify({
        "status": "request processing"
    })