from app import app
from app.routes import bp


app.register_blueprint(bp)
