# -*- coding: utf-8 -*-
import logging
from logging import StreamHandler
import os
from typing import Any, Dict

from flask import Flask
from flask_caching import Cache

from chaosplt_account.auth import setup_login
from chaosplt_account.service import Services
from chaosplt_account.storage import AccountStorage

__all__ = ["create_app", "cleanup_app", "serve_app"]


def create_app(config: Dict[str, Any]) -> Flask:
    app = Flask(__name__)

    app.url_map.strict_slashes = False
    app.debug = True if os.getenv('CHAOSHUB_DEBUG') else False

    logger = logging.getLogger('flask.app')
    logger.propagate = False

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.secret_key = app.config["SECRET_KEY"]

    app.config["GRPC_ADDR"] = "{}:{}".format(
        os.getenv("GRPC_LISTEN_ADDR"), os.getenv("GRPC_LISTEN_PORT"))

    app.config["CACHE_TYPE"] = os.getenv("CACHE_TYPE", "simple")
    if app.config["CACHE_TYPE"] == "redis":
        app.config["CACHE_REDIS_HOST"] = os.getenv("CACHE_REDIS_HOST")
        app.config["CACHE_REDIS_PORT"] = os.getenv("CACHE_REDIS_PORT", 6379)

    setup_login(app, from_session=True)

    return app


def cleanup_app(app: Flask):
    pass


def serve_app(app: Flask, cache: Cache, services: Services,
              storage: AccountStorage, config: Dict[str, Any],
              mount_point: str = '/account',
              log_handler: StreamHandler = None):
    pass
