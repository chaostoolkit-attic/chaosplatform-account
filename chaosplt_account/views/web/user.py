# -*- coding: utf-8 -*-
from uuid import UUID

from flask import abort, Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user
from marshmallow import ValidationError

from chaosplt_account.api.user import create_user, get_user, delete_user, \
    get_user_orgs, get_user_workspaces, link_org_to_user, \
    unlink_org_from_user, link_workspace_to_user, unlink_workspace_from_user, \
    get_user_experiments, get_user_executions, get_user_schedules, \
    lookup_user, get_user_tokens
from chaosplt_account.api.token import create_token, list_tokens, \
    delete_token, revoke_token
from chaosplt_account.schemas import \
    user_profile_schema, profile_orgs_schema, \
    profile_new_org_schema, profile_org_schema, profile_workspaces_schema, \
    profile_new_workspace_schema, profile_workspace_schema, current_user_schema

__all__ = ["view"]

view = Blueprint("user", __name__)


@view.route('current')
def the_user():
    if current_user.is_anonymous:
        return current_user_schema.jsonify(current_user)

    user_id = current_user.id
    user = request.storage.user.get(user_id)
    if not user:
        return abort(404)

    return current_user_schema.jsonify(user)


@view.route('signout', methods=["GET"])
def signout() -> str:
    if current_user.is_authenticated:
        logout_user()
    return "", 204


@view.route('signup/local', methods=["POST"])
def local_signup() -> str:
    payload = request.json

    username = payload.get("username")
    if not username or not username.strip():
        r = jsonify({
            "field": "username",
            "message": "Please specify a username"
        })
        r.status_code = 422
        return abort(r)

    username = username.strip()
    user = request.storage.registration.has_by_username(username)
    if user:
        r = jsonify({
            "field": "username",
            "message": "Username not available"
        })
        r.status_code = 422
        return abort(r)

    password = payload.get("password")
    if not password or not password.strip():
        r = jsonify({
            "field": "password",
            "message": "Please specify a password"
        })
        r.status_code = 422
        return abort(r)

    user = request.storage.registration.create_local(username, password)
    login_user(user, remember=True)
    request.services.activity.event.record(
        user_id=user.id, event_type="registration", phase="create")

    return user_profile_schema.jsonify(user), 201


@view.route('signin/local', methods=["POST"])
def local_signin() -> str:
    payload = request.json

    username = payload.get("username")
    if not username or not username.strip():
        r = jsonify({
            "field": "username",
            "message": "Please specify a username"
        })
        r.status_code = 422
        return abort(r)

    password = payload.get("password")
    if not password or not password.strip():
        r = jsonify({
            "field": "password",
            "message": "Please specify a password"
        })
        r.status_code = 422
        return abort(r)

    password = password.strip()
    user = request.storage.registration.get_by_username(username)
    if not user:
        r = jsonify({
            "field": "username",
            "message": "Invalid username"
        })
        r.status_code = 422
        return abort(r)

    valid = request.storage.registration.validate_password(user.id, password)
    if not valid:
        r = jsonify({
            "field": "password",
            "message": "Invalid password"
        })
        r.status_code = 422
        return abort(r)

    if not (user.is_local and user.is_active) or user.is_closed:
        r = jsonify({
            "field": "username",
            "message": "User account is not active"
        })
        r.status_code = 422
        return abort(r)

    login_user(user, remember=True)

    return user_profile_schema.jsonify(user), 200


@view.route('tokens')
def view_tokens():
    if current_user.is_anonymous:
        return jsonify([])

    return list_tokens(request.services, current_user.id)


@view.route('tokens/<uuid:token_id>', methods=["DELETE"])
def view_delete_token(token_id: UUID):
    if current_user.is_authenticated:
        return delete_token(request.services, current_user, token_id)
    return "", 204


@view.route('tokens/<uuid:token_id>/revoke', methods=["POST"])
def view_revoke_token(token_id: UUID):
    if current_user.is_authenticated:
        return revoke_token(request.services, current_user, token_id)
    return "", 204


@view.route('tokens', methods=["POST"])
def view_new_token():
    if current_user.is_authenticated:
        return create_token(request.services, current_user, request.json)
    return "", 204


@view.route('orgs')
def view_orgs():
    user_id = current_user.id
    orgs = request.storage.org.get_by_user(user_id)
    return profile_orgs_schema.jsonify({
        "orgs": orgs
    })


@view.route('orgs', methods=["POST"])
def view_new_org():
    user_id = current_user.id
    try:
        payload = profile_new_org_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    org_name = payload["name"]

    has_org = request.services.account.org.has_org_by_name(user_id, org_name)
    if has_org:
        return jsonify({
            "message": "Name already used"
        }), 409

    org = request.services.account.org.create(org_name, user_id)
    return profile_org_schema.jsonify(org), 201


@view.route('workspaces')
def view_workspaces():
    user_id = current_user.id
    workspaces = request.storage.workspace.get_by_user(user_id)
    return profile_workspaces_schema.jsonify({
        "workspaces": workspaces
    })


@view.route('workspaces', methods=["POST"])
def view_new_workspace():
    user_id = current_user.id
    try:
        payload = profile_new_workspace_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    org_id = payload["org_id"]
    org = request.services.account.org.get(org_id)
    if not org:
        return jsonify({
            "message": "Invalid organization"
        }), 422

    owns_org = request.storage.org.is_owner(org.id, user_id)
    if not owns_org:
        return jsonify({
            "message": "Must be owner of the organization"
        }), 422

    workspace_name = payload["name"]
    has_workspace = request.services.account.org.has_workspace_by_name(
        org.id, workspace_name)
    if has_workspace:
        return jsonify({
            "message": "Name already used in this organization"
        }), 409

    workspace_settings = {
        "visibility": payload["visibility"]
    }
    workspace = request.services.account.workspace.create(
        workspace_name, org.id, user_id, workspace_settings)
    return profile_workspace_schema.jsonify(workspace), 201


@view.route('', methods=['POST'])
def view_new():
    return create_user(request.services, request.json)


@view.route('<uuid:user_id>', methods=['GET'])
def get(user_id: UUID):
    return get_user(request.services, current_user, user_id)


@view.route('<uuid:user_id>', methods=['DELETE'])
def view_delete(user_id: UUID):
    return delete_user(request.services, current_user, user_id)


@view.route('<uuid:user_id>/tokens', methods=['GET'])
def view_get_user_tokens(user_id: UUID):
    return get_user_tokens(request.services, current_user, user_id)


@view.route('<uuid:user_id>/organizations', methods=['GET'])
def view_get_user_orgs(user_id: UUID):
    return get_user_orgs(request.services, current_user, user_id)


@view.route('<uuid:user_id>/workspaces', methods=['GET'])
def view_get_user_workspaces(user_id: UUID):
    return get_user_workspaces(request.services, current_user, user_id)


@view.route('<uuid:user_id>/organizations/<uuid:org_id>', methods=['PUT'])
def view_link_org_to_user(user_id: UUID, org_id: UUID):
    return link_org_to_user(request.services, current_user, user_id, org_id)


@view.route('<uuid:user_id>/organizations/<uuid:org_id>', methods=['DELETE'])
def view_unlink_org_from_user(user_id: UUID, org_id: UUID):
    return unlink_org_from_user(
        request.services, current_user, user_id, org_id)


@view.route('<uuid:user_id>/workspaces/<uuid:workspace_id>', methods=['PUT'])
def view_link_workspace_to_user(user_id: UUID, workspace_id: UUID):
    return link_workspace_to_user(
        request.services, current_user, user_id, workspace_id)


@view.route('<uuid:user_id>/workspaces/<uuid:workspace_id>',
            methods=['DELETE'])
def view_unlink_workspace_from_user(user_id: UUID, workspace_id: UUID):
    return unlink_workspace_from_user(
        request.services, current_user, user_id, workspace_id)


@view.route('<uuid:user_id>/experiments', methods=['GET'])
def view_get_user_experiments(user_id: UUID):
    return get_user_experiments(request.services, current_user, user_id)


@view.route('<uuid:user_id>/executions', methods=['GET'])
def view_get_user_executions(user_id: UUID):
    return get_user_executions(request.services, current_user, user_id)


@view.route('<uuid:user_id>/schedules', methods=['GET'])
def view_get_user_schedules(user_id: UUID):
    return get_user_schedules(request.services, current_user, user_id)


@view.route('lookup', methods=['GET'])
@login_required
def view_lookup_user():
    user_name = request.args.get("user")
    if not user_name:
        return abort(404)

    return lookup_user(request.services, current_user, user_name)
