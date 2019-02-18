# -*- coding: utf-8 -*-
from uuid import UUID

from flask import abort, Blueprint, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError

from chaosplt_account.schemas import access_tokens_schema, \
    access_token_schema, user_profile_schema, new_access_token_schema, \
    created_access_token_schema, profile_orgs_schema, new_org_schema, \
    profile_new_org_schema, profile_org_schema, profile_workspaces_schema, \
    profile_new_workspace_schema, profile_workspace_schema

__all__ = ["view"]

view = Blueprint("web_app_user", __name__)


@view.route('signed')
@login_required
def signed():
    return "", 200


@view.route('profile')
@login_required
def profile():
    user_id = current_user.id
    user = request.storage.user.get(user_id)
    if not user:
        return abort(404)
    
    return user_profile_schema.jsonify(user)


@view.route('tokens')
@login_required
def tokens():
    user_id = current_user.id
    tokens = request.services.auth.access_token.get_by_user(user_id)
    if isinstance(tokens, dict):
        tokens = tokens.values()
    return access_tokens_schema.jsonify(tokens)


@view.route('tokens/<uuid:token_id>', methods=["DELETE"])
@login_required
def delete_token(token_id: UUID):
    user_id = current_user.id
    request.services.auth.access_token.delete(user_id, token_id)
    return jsonify(""), 204


@view.route('tokens/<uuid:token_id>/revoke', methods=["POST"])
@login_required
def revoke_token(token_id: UUID):
    user_id = current_user.id
    token = request.services.auth.access_token.get(token_id)
    if not token or token.user_id != user_id:
        return abort(404)

    if token.revoked:
        return jsonify(""), 204

    request.services.auth.access_token.revoke(user_id, token_id)
    return jsonify(""), 200


@view.route('tokens', methods=["POST"])
@login_required
def new_token():
    user_id = current_user.id
    try:
        payload = new_access_token_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422
    
    name = payload["name"]

    token = request.services.auth.access_token.get_by_name(user_id, name)
    if token:
        return jsonify({'name': ['"{}" is already used.'.format(name)]}), 422

    token = request.services.auth.access_token.create(name, user_id)
    return created_access_token_schema.jsonify(token)


@view.route('orgs')
@login_required
def orgs():
    user_id = current_user.id
    orgs = request.storage.org.get_by_user(user_id)
    return profile_orgs_schema.jsonify({
        "orgs": orgs
    })


@view.route('orgs', methods=["POST"])
@login_required
def new_org():
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
@login_required
def workspaces():
    user_id = current_user.id
    workspaces = request.storage.workspace.get_by_user(user_id)
    return profile_workspaces_schema.jsonify({
        "workspaces": workspaces
    })


@view.route('workspaces', methods=["POST"])
@login_required
def new_workspace():
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
