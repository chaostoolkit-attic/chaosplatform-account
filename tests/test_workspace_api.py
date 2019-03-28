from copy import deepcopy
import json
from unittest.mock import MagicMock
from uuid import uuid4, UUID

from chaosplt_account.api.org import get_org
from chaosplt_account.api.workspace import create_workspace, get_workspace
from chaosplt_account.model import Organization, User
from chaosplt_account.service import Services
from chaosplt_account.storage.model.workspace import DEFAULT_WORKSPACE_SETTINGS
from flask import Flask
import pytest
from werkzeug.exceptions import NotFound


def test_create_workspace_missing_payload(app: Flask, services: Services,
                                          authed_user: User):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {}
        response, status_code = create_workspace(
            services, authed_user, payload)
        assert status_code == 422

        error = response.json
        assert "name" in error
        assert error['name'] == ['Missing data for required field.']
        assert "org" in error
        assert error['org'] == ['Missing data for required field.']


def test_create_workspace_unknown_org(app: Flask, services: Services,
                                      authed_user: User):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "name": "my new workspace",
            "org": str(uuid4())
        }
        response, status_code = create_workspace(
            services, authed_user, payload)
        assert status_code == 422

        error = response.json
        assert "org" in error
        assert error['org'] == ['Unknown organization']


def test_create_workspace_already_exists(app: Flask, services: Services,
                                         authed_user: User,
                                         user_org: Organization,
                                         myworkspace_name: str):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "name": myworkspace_name,
            "org": str(user_org.id),
        }
        response, status_code = create_workspace(
            services, authed_user, payload)
        assert status_code == 409

        error = response.json
        assert "name" in error
        assert error['name'] == ['Name already used in this organization']


def test_create_workspace(app: Flask, services: Services, authed_user: User,
                          collaborative_org2: Organization):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "name": "new project",
            "org": str(collaborative_org2.id),
            "visibility": deepcopy(DEFAULT_WORKSPACE_SETTINGS)["visibility"]
        }
        response, status_code = create_workspace(
            services, authed_user, payload)
        assert status_code == 201

        workspace = response.json
        assert 'id' in workspace
        assert 'created_on' in workspace
        assert workspace['name'] == 'new project'
        assert workspace['type'] == 'public'
        assert workspace['org_id'] == str(collaborative_org2.id)
        assert workspace['owner'] is True
        assert workspace['member'] is True
        assert workspace['visibility'] is not None

        event.record.assert_called_once_with(
            authenticated_user_id=authed_user.id, org_id=collaborative_org2.id,
            user_id=authed_user.id, event_type="workspace",
            workspace_id=UUID(workspace['id']), phase="create")


def test_create_personal_workspace(app: Flask, services: Services,
                                   authed_user: User,
                                   collaborative_org2: Organization):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "name": "new personal project",
            "org": str(collaborative_org2.id),
            "type": "personal",
            "visibility": deepcopy(DEFAULT_WORKSPACE_SETTINGS)["visibility"]
        }
        response, status_code = create_workspace(
            services, authed_user, payload)
        assert status_code == 201

        workspace = response.json
        assert 'id' in workspace
        assert 'created_on' in workspace
        assert workspace['name'] == 'new personal project'
        assert workspace['type'] == 'personal'
        assert workspace['org_id'] == str(collaborative_org2.id)
        assert workspace['owner'] is True
        assert workspace['member'] is True
        assert workspace['visibility'] is not None

        event.record.assert_called_once_with(
            authenticated_user_id=authed_user.id, org_id=collaborative_org2.id,
            user_id=authed_user.id, event_type="workspace",
            workspace_id=UUID(workspace['id']), phase="create")
