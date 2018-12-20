# -*- coding: utf-8 -*-
import logging
from logging import StreamHandler
import os
from typing import Any, Dict

from flask import Blueprint, Flask, after_this_request, request, Response
from flask_caching import Cache

from chaosplt_account.auth import setup_jwt, setup_login
from chaosplt_account.schemas import setup_schemas
from chaosplt_account.service import Services
from chaosplt_account.storage import AccountStorage

from .org import api as org_api
from .user import api as user_api
from .workspace import api as workspace_api

__all__ = ["create_api", "cleanup_api", "serve_api"]


def create_api(config: Dict[str, Any]) -> Flask:
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

    setup_jwt(app)
    setup_schemas(app)
    setup_login(app, from_jwt=True)

    return app


def cleanup_api(app: Flask):
    pass


def serve_api(app: Flask, cache: Cache, services: Services,
              storage: AccountStorage, config: Dict[str, Any],
              mount_point: str = '', log_handler: StreamHandler = None):
    register_api(app, cache, services, storage)


###############################################################################
# Internals
###############################################################################
def register_api(app: Flask, cache: Cache, services, storage: AccountStorage):
    patch_request(user_api, services, storage)
    patch_request(org_api, services, storage)
    patch_request(workspace_api, services, storage)

    app.register_blueprint(user_api, url_prefix="/users")
    app.register_blueprint(org_api, url_prefix="/organizations")
    app.register_blueprint(workspace_api, url_prefix="/workspaces")


def patch_request(bp: Blueprint, services, storage: AccountStorage):
    @bp.before_request
    def prepare_request():
        request.services = services
        request.storage = storage

        @after_this_request
        def clean_request(response: Response):
            request.services = None
            request.storage = None
            return response
