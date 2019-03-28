from datetime import datetime
from logging import StreamHandler
import os
from typing import Any, Dict, List
import uuid
from uuid import UUID

import cherrypy
from flask import Flask
from flask_caching import Cache
import pytest

from chaosplt_account.cache import setup_cache
from chaosplt_account.log import http_requests_logger
from chaosplt_account.model import Organization, User, anonymous_user as anon
from chaosplt_account.views.web import create_app, serve_app
from chaosplt_account.views.api import create_api, serve_api
from chaosplt_account.service import Services, initialize_services
from chaosplt_account.settings import load_settings
from chaosplt_account.storage import AccountStorage, initialize_storage
from chaosplt_account.storage.model.user import UserInfo
from chaosplt_relational_storage.db import orm_session

from fixtures.data import create_orgs, create_users, create_workspaces, \
    create_user_to_be_deleted, reset_dataset


cur_dir = os.path.abspath(os.path.dirname(__file__))
fixtures_dir = os.path.join(cur_dir, "fixtures")
config_path = os.path.join(fixtures_dir, 'config.toml')


@pytest.fixture
def config() -> Dict[str, Any]:
    return load_settings(config_path)


@pytest.fixture
def account_storage(config: Dict[str, Any]) -> AccountStorage:
    return initialize_storage(config)


@pytest.fixture
def stream_handler() -> StreamHandler:
    return StreamHandler()


@pytest.fixture
def services(account_storage: AccountStorage,
             config: Dict[str, Any]) -> Services:
    services = Services()
    services.account = account_storage
    initialize_services(services, config)
    return services


@pytest.fixture
def app(config: Dict[str, Any], services: Services,
        account_storage: AccountStorage,
        stream_handler: StreamHandler) -> Flask:
    application = create_app(config)
    application.config["SERVER_NAME"] = "chaosplatform-testing"
    cache = setup_cache(application)
    serve_app(
        application, cache, services, account_storage, config,
        "/", log_handler=stream_handler)
    create_users(application)
    create_orgs(application)
    create_workspaces(application)
    yield application
    reset_dataset(application)


@pytest.fixture
def api(app: Flask, config: Dict[str, Any], services: Services,
        account_storage: AccountStorage,
        stream_handler: StreamHandler) -> Flask:
    application = create_api(config)
    cache = setup_cache(application)
    wsgiapp = http_requests_logger(application, stream_handler)
    cherrypy.tree.graft(wsgiapp, "/api/v1")
    serve_api(
        application, cache, services, account_storage, config,
        "/api/v1", log_handler=stream_handler)
    return application


@pytest.fixture
def app_cache(app: Flask) -> Cache:
    return Cache(app, config=app.config)


@pytest.fixture
def api_cache(api: Flask) -> Cache:
    return Cache(api, config=api.config)


@pytest.fixture
def user_id() -> UUID:
    return uuid.uuid4()


@pytest.fixture
def org_id() -> UUID:
    return uuid.uuid4()


@pytest.fixture
def org_name() -> str:
    return "myorg"


@pytest.fixture
def workspace_id() -> UUID:
    return uuid.uuid4()


@pytest.fixture
def experiment_id() -> UUID:
    return uuid.uuid4()


@pytest.fixture
def username() -> str:
    return "myuser"


@pytest.fixture
def username1() -> str:
    return "user1"


@pytest.fixture
def username2() -> str:
    return "user2"


@pytest.fixture
def noorgs_username() -> str:
    return "user-no-orgs"


@pytest.fixture
def user_to_delete_username() -> str:
    return "user-to-delete"


@pytest.fixture
def myworkspace_name() -> str:
    return "myworkspace"


@pytest.fixture
def authed_user(app: Flask, account_storage: AccountStorage,
                username: str) -> User:
    with app.app_context():
        with orm_session() as session:
            info = session.query(UserInfo).filter_by(
                username=username).first()
            return account_storage.user.get(info.user_id)


@pytest.fixture
def user_org(app: Flask, account_storage: AccountStorage) -> Organization:
    with app.app_context():
        with orm_session() as session:
            info = session.query(UserInfo).filter_by(
                username="myuser").first()
            orgs = account_storage.org.get_by_user(info.user_id)
            for org in orgs:
                if org.kind == "personal":
                    return org


@pytest.fixture
def collaborative_org1(app: Flask,
                       account_storage: AccountStorage) -> Organization:
    with app.app_context():
        org = account_storage.org.get_by_name("org1")
        return org


@pytest.fixture
def collaborative_org2(app: Flask,
                       account_storage: AccountStorage) -> Organization:
    with app.app_context():
        org = account_storage.org.get_by_name("org2")
        return org


@pytest.fixture
def orgs(user_org: Organization) -> List[Organization]:
    return [
        user_org
    ]


@pytest.fixture
def user1(app: Flask, account_storage: AccountStorage,
          username1: str) -> User:
    with app.app_context():
        with orm_session() as session:
            info = session.query(UserInfo).filter_by(
                username=username1).first()
            return account_storage.user.get(info.user_id)


@pytest.fixture
def user2(app: Flask, account_storage: AccountStorage,
          username2: str) -> User:
    with app.app_context():
        with orm_session() as session:
            info = session.query(UserInfo).filter_by(
                username=username2).first()
            return account_storage.user.get(info.user_id)


@pytest.fixture
def user_to_delete(app: Flask, account_storage: AccountStorage) -> User:
    user_id = create_user_to_be_deleted(app)
    with app.app_context():
        return account_storage.user.get(user_id)


@pytest.fixture
def user_with_no_orgs(app: Flask, account_storage: AccountStorage,
                      noorgs_username: str) -> User:
    with app.app_context():
        with orm_session() as session:
            info = session.query(UserInfo).filter_by(
                username=noorgs_username).first()
            return account_storage.user.get(info.user_id)


@pytest.fixture
def anonymous_user() -> User:
    return anon
