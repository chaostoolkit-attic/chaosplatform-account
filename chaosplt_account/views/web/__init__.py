# -*- coding: utf-8 -*-
import logging
from logging import StreamHandler
import os
from typing import Any, Dict, Union
from uuid import UUID

from flask import Blueprint, Flask, request, Response, after_this_request
from flask_caching import Cache
from flask_jwt_extended import JWTManager, get_jti

from chaosplt_account.auth import setup_login
from chaosplt_account.service import Services
from chaosplt_account.storage import AccountStorage

from .org import view as org_view
from .user import view as user_view
from .workspace import view as workspace_view

__all__ = ["create_app", "cleanup_app", "serve_app"]


def create_app(config: Dict[str, Any]) -> Flask:
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

    setup_login(app, from_session=True)

    return app


def cleanup_app(app: Flask):
    pass


def serve_app(app: Flask, cache: Cache, services: Services,
              storage: AccountStorage, config: Dict[str, Any],
              mount_point: str = '/account',
              log_handler: StreamHandler = None):
    # special case for generating JWT tokens
    jwt = JWTManager(app)

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        return False

    @jwt.user_claims_loader
    def add_claims(identity: Union[UUID, str]) -> Dict[str, Any]:
        return {
            'user_id': str(identity)
        }

    register_views(app, cache, services, storage, mount_point)


###############################################################################
# Internals
###############################################################################
def register_views(app: Flask, cache: Cache, services,
                   storage: AccountStorage, mount_point: str):
    patch_request(user_view, services, storage)
    patch_request(org_view, services, storage)

    app.register_blueprint(user_view, url_prefix="{}/user".format(mount_point))
    app.register_blueprint(org_view, url_prefix="{}/orgs".format(mount_point))


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
