import uuid
import json
from pathlib import Path
from datetime import datetime, timedelta

from flask import Flask, request
from flasgger import Swagger
from flask_cors import CORS

from config import Config
from models.database import db
from helpers.custom_response import CustomResponse

from blueprints.commodity_blueprint import commodity_blueprint
from blueprints.storage_blueprint import storage_blueprint
from blueprints.image_blueprint import image_blueprint
from blueprints.record_blueprint import record_blueprint

from apscheduler.schedulers.background import BackgroundScheduler
from models.commodity_model import Commodity


def get_documents(doc_path='docs'):
    documents = json.load(open(f'{doc_path}/swagger_template.json', 'r'))

    for document in Path(doc_path).glob('*.json'):
        if document.stem == 'swagger_template':
            continue
        documents['definitions'].update(json.load(open(document, 'r')))

    return documents


def create_app():
    app = Flask(__name__)
    app.secret_key = uuid.uuid4().hex

    app.config.from_object(Config)
    db.init_app(app)

    Swagger(app, template=get_documents())
    CORS(
        app,
        resources={r"/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}},
        supports_credentials=True
    )

    app.register_blueprint(commodity_blueprint, url_prefix='/api/commodity')
    app.register_blueprint(storage_blueprint, url_prefix='/api/storage')
    app.register_blueprint(image_blueprint, url_prefix='/api/image')
    app.register_blueprint(record_blueprint, url_prefix='/api/record')

    with app.app_context():
        db.create_all()

    return app


app = create_app()


@app.errorhandler(Exception)
def handle_exception(e: Exception):
    ip = request.remote_addr if request else 'unknown'
    route = request.url_rule.rule if request.url_rule else 'unknown'
    return CustomResponse.internal_error(f"An exception occurred: {str(e)}", {
        "ip": ip,
        "route": route
    })


def update_commodity_status():
    with app.app_context():
        for commodity in db.session.query(Commodity).all():
            if datetime.now() > commodity.expireTime:
                commodity.status = 'expired'
                continue

            elif commodity.status == 'giving' and datetime.now() > commodity.giveExpireTime:
                commodity.status = 'giveExpired'
                continue

            if commodity.status == 'receiving' and datetime.now() > commodity.receiveExpireTime:
                commodity.status = 'pending'
                continue

        db.session.commit()


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_commodity_status, 'interval', seconds=1)
    scheduler.start()

    for folder_name in [Config.IMAGE_DIR]:
        Path(folder_name).mkdir(parents=True, exist_ok=True)

    app.run(debug=True, host=Config.HOST, port=Config.PORT)
