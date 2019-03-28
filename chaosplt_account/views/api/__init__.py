# -*- coding: utf-8 -*-
import logging
from logging import StreamHandler
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
    app.debug = config.get("debug", False)

    logger = logging.getLogger('flask.app')
    logger.propagate = False

    app.config["SECRET_KEY"] = config["http"]["secret_key"]
    app.secret_key = config["http"]["secret_key"]
    app.config["JWT_SECRET_KEY"] = config["jwt"]["secret_key"]
    app.config["SQLALCHEMY_DATABASE_URI"] = config["db"]["uri"]

    app.config["CACHE_TYPE"] = config["cache"].get("type", "simple")
    if app.config["CACHE_TYPE"] == "redis":
        redis_config = config["cache"]["redis"]
        app.config["CACHE_REDIS_HOST"] = redis_config.get("host")
        app.config["CACHE_REDIS_PORT"] = redis_config.get("port", 6379)
        app.config["CACHE_REDIS_DB"] = redis_config.get("db", 0)
        app.config["CACHE_REDIS_PASSWORD"] = redis_config.get("password")

    setup_jwt(app)
    setup_schemas(app)
    setup_login(app, from_jwt=True, from_session=False)

    return app


def cleanup_api(app: Flask):
    pass


def serve_api(app: Flask, cache: Cache, services: Services,
              storage: AccountStorage, config: Dict[str, Any],
              mount_point: str = '', log_handler: StreamHandler = None):
    register_api(app, cache, services, storage, mount_point)


###############################################################################
# Internals
###############################################################################
def register_api(app: Flask, cache: Cache, services, storage: AccountStorage,
                 mount_point: str):
    patch_request(user_api, services, storage)
    patch_request(org_api, services, storage)
    patch_request(workspace_api, services, storage)

    app.register_blueprint(user_api, url_prefix="{}/users".format(mount_point))
    app.register_blueprint(
        org_api, url_prefix="{}/organizations".format(mount_point))
    app.register_blueprint(
        workspace_api, url_prefix="{}/workspaces".format(mount_point))


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
