import json
from unittest.mock import MagicMock
from uuid import uuid4, UUID

from chaosplt_account.api.org import list_all_orgs, create_org, delete_org, \
    get_org, get_org_workspaces, lookup_org, get_members, get_member, \
    set_org_name, set_org_infos, delete_org
from chaosplt_account.api.workspace import create_workspace, get_workspace
from chaosplt_account.model import Organization, User
from chaosplt_account.service import Services
from chaosplt_account.storage.model.org import DEFAULT_ORG_SETTINGS
from flask import Flask
import pytest
from werkzeug.exceptions import NotFound


def test_list_all_orgs(app: Flask, services: Services, authed_user: User):
    with app.app_context():
        response = list_all_orgs(services, authed_user)
        orgs = response.json
        assert len(orgs) == 3


def test_create_org_name_is_mandatory(app: Flask, services: Services,
                                      authed_user: User):
    services.activity.event = MagicMock()
    with app.app_context():
        payload = {}
        response, status_code = create_org(services, authed_user, payload)
        assert status_code == 422

        error = response.json
        assert "name" in error
        assert error['name'] == ['Missing data for required field.']


def test_create_org_name_must_be_a_string(app: Flask, services: Services,
                                          authed_user: User):
    services.activity.event = MagicMock()
    with app.app_context():
        payload = {
            "name": 89
        }
        response, status_code = create_org(services, authed_user, payload)
        assert status_code == 422

        error = response.json
        assert "name" in error
        assert error['name'] == ['Not a valid string.']


def test_create_org_fail_on_unknown_fields(app: Flask, services: Services,
                                           authed_user: User):
    services.activity.event = MagicMock()
    with app.app_context():
        payload = {
            "name": "my name",
            "message": "woo ooh!"
        }
        response, status_code = create_org(services, authed_user, payload)
        assert status_code == 422

        error = response.json
        assert "message" in error
        assert error["message"] == ['Unknown field.']


def test_create_org(app: Flask, services: Services, authed_user: User):
    services.activity.event = MagicMock()
    with app.app_context():
        payload = {
            "name": "a new org"
        }
        response, status_code = create_org(services, authed_user, payload)
        assert status_code == 201

        org = response.json
        assert org['name'] == "a new org"
        assert 'id' in org
        org_id = org['id']

        try:
            assert 'created_on' in org
            assert 'workspaces' in org
            assert org['workspaces'] == []
            assert org['owner'] is True
            assert org['type'] == 'collaborative'

            url = 'http://chaosplatform-testing/organizations/{}'.format(
                org_id
            )
            assert org['url'] == url
            assert org['links']['self'] == url
        finally:
            delete_org(services, authed_user, org_id)


def test_create_org_cannot_use_an_existing_name(app: Flask, services: Services,
                                                authed_user: User):
    services.activity.event = MagicMock()
    with app.app_context():
        payload = {
            "name": "a new org"
        }
        response, status_code = create_org(services, authed_user, payload)
        assert status_code == 201
        org = response.json
        org_id = org['id']

        try:
            response, status_code = create_org(services, authed_user, payload)
            assert status_code == 409

            error = response.json
            assert "name" in error
        finally:
            delete_org(services, authed_user, org_id)


def test_create_org_must_record_event(app: Flask, services: Services,
                                      authed_user: User):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "name": "a new org"
        }
        response, status_code = create_org(services, authed_user, payload)
        assert status_code == 201

        org = response.json
        org_id = org['id']

        try:
            event.record.assert_called_once_with(
                authenticated_user_id=authed_user.id, user_id=authed_user.id,
                org_id=UUID(org_id), event_type="organization", phase="create"
            )
        finally:
            delete_org(services, authed_user, org_id)


def test_get_my_org(app: Flask, services: Services, authed_user: User,
                    user_org: Organization):
    with app.app_context():
        response = get_org(services, authed_user, user_org.id)
        assert response.status_code == 200

        org = response.json
        assert org['name'] == "myorg"
        assert 'id' in org
        org_id = org['id']

        assert 'owner' not in org
        assert 'created_on' in org
        assert 'workspaces' in org
        assert len(org['workspaces']) == 2
        assert org['workspaces'][0]['owner'] is True
        assert org['workspaces'][1]['owner'] is False
        assert org['type'] == 'personal'
        assert 'settings' in org
        assert org['settings'] == DEFAULT_ORG_SETTINGS

        url = 'http://chaosplatform-testing/organizations/{}'.format(
            org_id
        )
        assert org['url'] == url
        assert org['links']['self'] == url


def test_get_org_anonymous_user(app: Flask, services: Services,
                                anonymous_user: User, user_org: Organization):
    with app.app_context():
        response = get_org(services, anonymous_user, user_org.id)

        assert response.status_code == 200

        org = response.json
        print(org)
        assert org['name'] == "myorg"
        assert 'id' in org
        org_id = org['id']

        assert 'owner' not in org
        assert 'created_on' in org
        assert 'workspaces' in org
        assert len(org['workspaces']) == 2
        assert org['workspaces'][0]['owner'] is False
        assert org['workspaces'][1]['owner'] is False
        assert org['type'] == 'personal'
        assert 'settings' in org
        assert org['settings'] == DEFAULT_ORG_SETTINGS

        url = 'http://chaosplatform-testing/organizations/{}'.format(
            org_id
        )
        assert org['url'] == url
        assert org['links']['self'] == url


def test_get_my_org_workspaces(app: Flask, services: Services,
                               authed_user: User, user_org: Organization):
    with app.app_context():
        response = get_org_workspaces(services, authed_user, user_org.id)
        assert response.status_code == 200

        workspaces = response.json
        assert len(workspaces) == 2


def test_get_org_workspaces_org_not_found(app: Flask, services: Services,
                                          authed_user: User):
    with app.app_context():
        with pytest.raises(NotFound):
            get_org_workspaces(services, authed_user, uuid4())


def test_lookup_myorg(app: Flask, services: Services, authed_user: User,
                      user_org: Organization):
    with app.app_context():
        response = lookup_org(services, authed_user, "myorg")
        assert response.status_code == 200

        org = response.json
        assert org['id'] == str(user_org.id)
        assert org['member'] is True
        assert org['owner'] is True
        assert len(org['workspaces']) == 2
        assert org['workspaces'][0]['owner'] is True
        assert org['workspaces'][1]['owner'] is False


def test_lookup_another_org(app: Flask, services: Services, user1: User):
    with app.app_context():
        response = lookup_org(services, user1, "myorg")
        assert response.status_code == 200

        org = response.json
        assert org['member'] is False
        assert org['owner'] is False
        assert len(org['workspaces']) == 2
        assert org['workspaces'][0]['owner'] is False
        assert org['workspaces'][1]['owner'] is False


def test_lookup_org_anonymously(app: Flask, services: Services,
                                anonymous_user: User):
    with app.app_context():
        response = lookup_org(services, anonymous_user, "myorg")
        assert response.status_code == 200

        org = response.json
        assert org['member'] is False
        assert org['owner'] is False
        assert len(org['workspaces']) == 2
        assert org['workspaces'][0]['owner'] is False
        assert org['workspaces'][1]['owner'] is False


def test_lookup_org_not_found(app: Flask, services: Services,
                              anonymous_user: User):
    with app.app_context():
        with pytest.raises(NotFound):
            lookup_org(services, anonymous_user, "zorg")


def test_there_should_be_one_member_in_personal_org(app: Flask,
                                                    services: Services,
                                                    authed_user: User,
                                                    user_org: Organization):
    with app.app_context():
        response = get_members(services, authed_user, user_org.id)
        assert response.status_code == 200

        members = response.json
        assert len(members) == 1
        member = members[0]
        assert member['id'] == str(authed_user.id)


def test_get_collaborative_org_members(app: Flask, services: Services,
                                       authed_user: User, user1: User,
                                       collaborative_org1: Organization):
    with app.app_context():
        response = get_members(services, authed_user, collaborative_org1.id)
        assert response.status_code == 200

        members = response.json
        assert len(members) == 2
        member_ids = list(map(lambda m: m['id'], members))
        assert str(authed_user.id) in member_ids
        assert str(user1.id) in member_ids


def test_get_org_members_unknown_org(app: Flask, services: Services,
                                     authed_user: User):
    with app.app_context():
        with pytest.raises(NotFound):
            get_members(services, authed_user, uuid4())


def test_get_org_member_unknown_org(app: Flask, services: Services,
                                    authed_user: User, user1: User):
    with app.app_context():
        with pytest.raises(NotFound):
            get_member(services, authed_user, uuid4(), user1.id)


def test_get_org_unknown_member(app: Flask, services: Services,
                                authed_user: User, user_org: Organization):
    with app.app_context():
        with pytest.raises(NotFound):
            get_member(services, authed_user, user_org.id, uuid4())


def test_get_org_not_member(app: Flask, services: Services,
                            authed_user: User, user_org: Organization,
                            user2: User):
    with app.app_context():
        with pytest.raises(NotFound):
            get_member(services, authed_user, user_org.id, user2.id)


def test_get_org_member(app: Flask, services: Services,
                        authed_user: User, user_org: Organization):
    with app.app_context():
        response = get_member(
            services, authed_user, user_org.id, authed_user.id)
        assert response.status_code == 200

        member = response.json
        assert member['id'] == str(authed_user.id)


def test_set_org_name(app: Flask, services: Services, authed_user: User,
                      user_org: Organization):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        try:
            response, status_code = set_org_name(
                services, authed_user, user_org.id, {"name": "newname"})
            assert status_code == 204

            with pytest.raises(NotFound):
                lookup_org(services, authed_user, user_org.name)

            response = lookup_org(services, authed_user, "newname")
            assert response.status_code == 200

            event.record.assert_called_once_with(
                authenticated_user_id=authed_user.id, user_id=authed_user.id,
                org_id=user_org.id, event_type="organization", phase="rename",
                payload=json.dumps({"old_name": user_org.name})
            )
        finally:
            response, status_code = set_org_name(
                services, authed_user, user_org.id, {"name": user_org.name})
            assert status_code == 204


def test_set_org_name_missing_name_in_payload(app: Flask, services: Services,
                                              authed_user: User,
                                              user_org: Organization):
    with app.app_context():
        response, status_code = set_org_name(
            services, authed_user, user_org.id, {})
        assert status_code == 422


def test_set_org_invalid_payload(app: Flask, services: Services,
                                 authed_user: User, user_org: Organization):
    with app.app_context():
        response, status_code = set_org_name(
            services, authed_user, user_org.id,
            {"name": "newname", "toomuch": "blah"})
        assert status_code == 422


def test_set_org_name_must_be_a_string(app: Flask, services: Services,
                                       authed_user: User,
                                       user_org: Organization):
    with app.app_context():
        response, status_code = set_org_name(
            services, authed_user, user_org.id, {"name": 12})
        assert status_code == 422


def test_set_org_invalid_organization(app: Flask, services: Services,
                                      authed_user: User):
    with app.app_context():
        with pytest.raises(NotFound):
            set_org_name(services, authed_user, uuid4(), {"name": "newname"})


def test_set_org_not_an_org_owner(app: Flask, services: Services,
                                  user1: User, user_org: Organization):
    with app.app_context():
        with pytest.raises(NotFound):
            set_org_name(services, user1, user_org.id, {"name": "newname"})


def test_set_org_infos(app: Flask, services: Services, authed_user: User,
                       user_org: Organization):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        try:
            response, status_code = set_org_infos(
                services, authed_user, user_org.id,
                {
                    "email": "newemail@example.com",
                    "url": "https://example.com/blah",
                    "logo": "https://myimage.com",
                    "description": "bwah ah ah"
                }
            )
            assert status_code == 204

            event.record.assert_called_once_with(
                authenticated_user_id=authed_user.id, user_id=authed_user.id,
                org_id=user_org.id, event_type="organization", phase="edit",
                payload=json.dumps({"old_settings": DEFAULT_ORG_SETTINGS}))
        finally:
            response, status_code = set_org_infos(
                services, authed_user, user_org.id, DEFAULT_ORG_SETTINGS)
            assert status_code == 204


def test_set_org_infos_invalid_payload(app: Flask, services: Services,
                                       authed_user: User,
                                       user_org: Organization):
    with app.app_context():
        response, status_code = set_org_infos(
            services, authed_user, user_org.id,
            {
                "email": "newemail@example.com",
                "url": "https://example.com/blah",
                "logo": "https://myimage.com",
                "description": "bwah ah ah",
                "unexpected": "invalid"
            }
        )
        assert status_code == 422


def test_set_org_infos_invalid_organization(app: Flask, services: Services,
                                            authed_user: User):
    with app.app_context():
        with pytest.raises(NotFound):
            set_org_infos(
                services, authed_user, uuid4(),
                {
                    "email": "newemail@example.com",
                    "url": "https://example.com/blah",
                    "logo": "https://myimage.com",
                    "description": "bwah ah ah"
                }
            )


def test_set_org_infos_not_an_org_owner(app: Flask, services: Services,
                                        user1: User, user_org: Organization):
    with app.app_context():
        with pytest.raises(NotFound):
            set_org_infos(
                services, user1, user_org.id,
                {
                    "email": "newemail@example.com",
                    "url": "https://example.com/blah",
                    "logo": "https://myimage.com",
                    "description": "bwah ah ah"
                }
            )


def test_delete_org_you_own(app: Flask, services: Services, authed_user: User):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "name": "a new org"
        }
        response, status_code = create_org(services, authed_user, payload)
        assert status_code == 201

        org = response.json
        response, status_code = delete_org(services, authed_user, org['id'])
        assert status_code == 204

        with pytest.raises(NotFound):
            get_org(services, authed_user, org['id'])


def test_delete_org_should_delete_workspaces_too(app: Flask,
                                                 services: Services,
                                                 authed_user: User):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "name": "a new org"
        }
        response, status_code = create_org(services, authed_user, payload)
        assert status_code == 201

        org = response.json

        payload = {
            "name": "a new workspace",
            "visibility": {
                "execution": "status",
                "experiment": "public"
            },
            "org": org['id']
        }
        response, status_code = create_workspace(
            services, authed_user, payload)
        assert status_code == 201

        workspace = response.json

        response, status_code = delete_org(services, authed_user, org['id'])
        assert status_code == 204

        with pytest.raises(NotFound):
            get_workspace(services, authed_user, workspace['id'])

        with pytest.raises(NotFound):
            get_org(services, authed_user, org['id'])


def test_cannot_delete_personal_org(app: Flask, services: Services,
                                    authed_user: User, user_org: Organization):
    with app.app_context():
        response, status_code = delete_org(services, authed_user, user_org.id)
        assert status_code == 422


def test_delete_org_you_own_must_record_event(app: Flask, services: Services,
                                              authed_user: User):
    event = MagicMock()
    services.activity.event = event
    with app.app_context():
        payload = {
            "name": "a new org"
        }
        response, status_code = create_org(services, authed_user, payload)
        assert status_code == 201

        org = response.json
        response, status_code = delete_org(services, authed_user, org['id'])
        assert status_code == 204

        event.record.assert_called_with(
            authenticated_user_id=authed_user.id, user_id=authed_user.id,
            org_id=UUID(org['id']), event_type="organization", phase="delete"
        )


def test_cannot_delete_org_you_dont_own(app: Flask, services: Services,
                                        user1: User, user_org: Organization):
    with app.app_context():
        with pytest.raises(NotFound):
            delete_org(services, user1, user_org.id)


def test_cannot_delete_missing_org(app: Flask, services: Services,
                                   authed_user: User):
    with app.app_context():
        response, status_code = delete_org(services, authed_user, uuid4())
        assert status_code == 204
