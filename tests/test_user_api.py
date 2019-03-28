import json
from unittest.mock import MagicMock
from uuid import uuid4, UUID

from chaosplt_account.api.org import get_org
from chaosplt_account.api.user import create_user, get_user, get_user_orgs, \
    get_user_tokens, get_user_workspaces, lookup_user, link_org_to_user, \
    unlink_org_from_user, delete_user
from chaosplt_account.api.workspace import get_workspace
from chaosplt_account.model import Organization, User
from chaosplt_account.service import Services
from flask import Flask
import pytest
from werkzeug.exceptions import NotFound


def test_create_user_requires_username(app: Flask, services: Services):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {}
        response, status_code = create_user(services, payload)
        assert status_code == 422

        error = response.json
        assert "username" in error
        assert error['username'] == ['Missing data for required field.']


def test_create_user_requires_string_username(app: Flask, services: Services):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "username": 54
        }
        response, status_code = create_user(services, payload)
        assert status_code == 422

        error = response.json
        assert "username" in error
        assert error['username'] == ['Not a valid string.']


def test_create_user_with_invalid_payload(app: Flask, services: Services):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "username": "jane",
            "whatever": "blah"
        }
        response, status_code = create_user(services, payload)
        assert status_code == 422

        error = response.json
        assert "whatever" in error
        assert error['whatever'] == ['Unknown field.']


def test_create_user(app: Flask, services: Services):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "username": "jane"
        }
        response, status_code = create_user(services, payload)
        assert status_code == 201

        user = response.json
        assert 'id' in user
        assert user['username'] == 'jane'

        orgs = user['orgs']
        assert len(orgs) == 1

        org = orgs[0]
        assert 'id' in org
        assert 'created_on' in org
        assert org['name'] == 'jane'
        assert org['type'] == 'personal'
        assert org['owner'] is True
        assert org['member'] is True
        assert org['settings'] is None
        org_workspaces = org['workspaces']
        assert len(org_workspaces) == 1

        workspace = org_workspaces[0]
        assert 'id' in workspace
        assert 'created_on' in workspace
        assert workspace['name'] == 'jane'
        assert workspace['type'] == 'personal'
        assert workspace['org_id'] == org['id']
        assert workspace['owner'] is True
        assert workspace['member'] is True
        assert workspace['visibility'] is not None

        workspaces = user['workspaces']
        assert len(workspaces) == 1

        workspace = workspaces[0]
        assert 'id' in workspace
        assert 'created_on' in workspace
        assert workspace['name'] == 'jane'
        assert workspace['type'] == 'personal'
        assert workspace['org_id'] == org['id']
        assert workspace['owner'] is True
        assert workspace['member'] is True
        assert workspace['visibility'] is not None


def test_create_user_must_record_an_event(app: Flask, services: Services):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "username": "jane"
        }
        response, status_code = create_user(services, payload)
        assert status_code == 201

        user = response.json
        event.record.assert_called_once_with(
            user_id=UUID(user["id"]), event_type="user", phase="create",
            payload={
                "username": "jane",
                "email": None,
                "name": None
            }
        )


def test_get_user(app: Flask, services: Services, authed_user: User,
                  user1: User):
    with app.app_context():
        response = get_user(services, authed_user, user1.id)
        assert response.status_code == 200

        user = response.json
        assert user["id"] == str(user1.id)


def test_get_unknown_user(app: Flask, services: Services, authed_user: User):
    with app.app_context():
        with pytest.raises(NotFound):
            get_user(services, authed_user, uuid4())


def test_get_user_orgs(app: Flask, services: Services, authed_user: User):
    with app.app_context():
        response = get_user_orgs(services, authed_user, authed_user.id)
        assert response.status_code == 200

        orgs = response.json
        assert len(orgs) == 3


def test_get_other_user_orgs(app: Flask, services: Services,
                             authed_user: User, user1: User):
    with app.app_context():
        response = get_user_orgs(services, authed_user, user1.id)
        assert response.status_code == 200

        orgs = response.json
        assert len(orgs) == 2


def test_get_orgs_for_unknown_user(app: Flask, services: Services,
                                   authed_user: User):
    with app.app_context():
        with pytest.raises(NotFound):
            get_user_orgs(services, authed_user, uuid4())


def test_get_user_tokens(app: Flask, services: Services, authed_user: User):
    access_token = MagicMock()
    services.auth.access_token = access_token

    with app.app_context():
        response = get_user_tokens(services, authed_user, authed_user.id)
        assert response.status_code == 200

        access_token.get_by_user.assert_called_with(authed_user.id)

        tokens = response.json

def test_get_user_workspaces(app: Flask, services: Services,
                             authed_user: User):
    with app.app_context():
        response = get_user_workspaces(services, authed_user, authed_user.id)
        assert response.status_code == 200

        workspaces = response.json
        assert len(workspaces) == 3


def test_get_user_workspaces_for_unknown_user(app: Flask, services: Services,
                                              authed_user: User):
    with app.app_context():
        with pytest.raises(NotFound):
            get_user_workspaces(services, authed_user, uuid4())


def test_lookup_user(app: Flask, services: Services, authed_user: User):
    with app.app_context():
        response = lookup_user(services, authed_user, "myuser")
        assert response.status_code == 200


def test_lookup_user_not_found(app: Flask, services: Services,
                               authed_user: User):
    with app.app_context():
        with pytest.raises(NotFound):
            lookup_user(services, authed_user, "DrWho")


def test_lookup_user_not_active(app: Flask, services: Services,
                                authed_user: User):
    with app.app_context():
        with pytest.raises(NotFound):
            lookup_user(services, authed_user, "inactive-user")


def test_link_org_to_user(app: Flask, services: Services, authed_user: User,
                          user_with_no_orgs: User,
                          collaborative_org2: Organization):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        response = get_user_orgs(services, authed_user, user_with_no_orgs.id)
        assert response.status_code == 200
        orgs = response.json
        assert len(orgs) == 0

        payload = {
            "owner": False
        }
        response, status_code = link_org_to_user(
            services, authed_user, user_with_no_orgs.id,
            collaborative_org2.id, payload)
        assert status_code == 204

        event.record.assert_called_once_with(
            authenticated_user_id=authed_user.id, org_id=collaborative_org2.id,
            user_id=user_with_no_orgs.id, event_type="user",
            phase="link-organization")
        event.reset_mock()

        response = get_user_orgs(services, authed_user, user_with_no_orgs.id)
        assert response.status_code == 200
        orgs = response.json
        assert len(orgs) == 1

        response, status_code = unlink_org_from_user(
            services, authed_user, user_with_no_orgs.id, collaborative_org2.id)
        assert status_code == 204

        response = get_user_orgs(services, authed_user, user_with_no_orgs.id)
        assert response.status_code == 200
        orgs = response.json
        assert len(orgs) == 0

        event.record.assert_called_once_with(
            authenticated_user_id=authed_user.id, org_id=collaborative_org2.id,
            user_id=user_with_no_orgs.id, event_type="user",
            phase="unlink-organization")


def test_link_org_to_unknown_user(app: Flask, services: Services,
                                  authed_user: User,
                                  collaborative_org2: Organization):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "owner": False
        }
        response, status_code = link_org_to_user(
            services, authed_user, uuid4(),
            collaborative_org2.id, payload)
        assert status_code == 422


def test_link_org_to_unknown_org(app: Flask, services: Services,
                                 authed_user: User, user1: User):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "owner": False
        }
        response, status_code = link_org_to_user(
            services, authed_user, user1.id, uuid4(), payload)
        assert status_code == 422


def test_link_org_owner_must_be_boolean(app: Flask, services: Services,
                                        authed_user: User, user2: User,
                                        collaborative_org2: Organization):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "owner": "hello"
        }
        response, status_code = link_org_to_user(
            services, authed_user, user2.id,
            collaborative_org2.id, payload)
        assert status_code == 422

        error = response.json
        assert "owner" in error
        assert error['owner'] == ['Not a valid boolean.']


def test_unlink_org_from_unknown_org(app: Flask, services: Services,
                                     authed_user: User, user1: User):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        response, status_code = unlink_org_from_user(
            services, authed_user, user1.id, uuid4())
        assert status_code == 422


def test_unlink_org_to_unknown_user(app: Flask, services: Services,
                                    authed_user: User,
                                    collaborative_org2: Organization):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        response, status_code = unlink_org_from_user(
            services, authed_user, uuid4(), collaborative_org2.id)
        assert status_code == 422


def test_delete_user(app: Flask, services: Services, authed_user: User,
                     user_to_delete: User):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        response, status_code = delete_user(
            services, authed_user, user_to_delete.id)
        assert status_code == 204

        event.record.assert_called_once_with(
            authenticated_user_id=authed_user.id,
            user_id=user_to_delete.id, event_type="user", phase="delete")


def test_delete_user_deletes_personal_org_and_workspace(app: Flask,
                                                        services: Services,
                                                        authed_user: User,
                                                        user_to_delete: User,
                                                        collaborative_org2: Organization):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        org = None
        for o in user_to_delete.orgs:
            if o.kind == "personal":
                org = o
                break
        workspace = user_to_delete.workspaces[0]

        response, status_code = delete_user(
            services, authed_user, user_to_delete.id)
        assert status_code == 204

        with pytest.raises(NotFound):
            get_org(services, authed_user, org.id)

        with pytest.raises(NotFound):
            get_workspace(services, authed_user, workspace.id)

        # we only deleted the personal org, not a collaborative one
        response = get_org(services, authed_user, collaborative_org2.id)
        assert response.status_code == 200
