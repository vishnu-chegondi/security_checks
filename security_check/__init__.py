import os
import logging

from flask import Flask

from security_check.aws_security_checks import aws_bp
from security_check.profile import profile_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    try:
        os.mkdir(app.instance_path)
    except OSError:
        logging.info(f"{app.instance_path} is already available")

    logging.basicConfig(level=logging.INFO)

    app.register_blueprint(aws_bp)
    app.register_blueprint(profile_bp)
    return app
