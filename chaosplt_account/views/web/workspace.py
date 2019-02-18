# -*- coding: utf-8 -*-
from uuid import UUID

from flask import abort, Blueprint, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError

from chaosplt_account.schemas import org_dashboard_schema, org_info_schema, \
    org_members_dashboard_schema, org_settings_schema, org_name_schema, \
    workspace_dashboard_schema, workspace_info_schema

from .org import view

__all__ = ["view"]


@view.route('<string:org_name>/<string:workspace_name>', methods=["GET"])
@login_required
def workspace(org_name: str, workspace_name: str):
    org = request.storage.org.get_by_name(org_name)
    if not org:
        return abort(404)

    workspace = request.storage.workspace.get_by_name(org.id, workspace_name)
    if not workspace:
        return abort(404)

    org.owner = False
    org.member = False
    user_id = current_user.id
    user = request.storage.user.get(user_id)
    if user:
        org.owner = request.storage.org.is_owner(org.id, user_id)
        org.member = request.storage.org.is_member(org.id, user_id)

    workspace.owner = False
    workspace.collaborator = False
    if user:
        workspace.owner = request.storage.workspace.is_owner(
            workspace.id, user_id)
        workspace.collaborator = request.storage.workspace.is_collaborator(
            workspace.id, user_id)

    return workspace_info_schema.jsonify(workspace)


@view.route('<string:org_name>/<string:workspace_name>/settings/general',
            methods=["GET"])
@login_required
def workspace_general_settings(org_name: str, workspace_name: str):
    user_id = current_user.id
    user = request.storage.user.get(user_id)
    if not user:
        return abort(404)

    org = request.storage.org.get_by_name(org_name)
    if not org:
        return abort(404)
    
    owns_org = request.storage.org.is_owner(org.id, user_id)
    if not owns_org:
        return abort(404)

    org.owner = True
    org.member = True

    workspace = request.storage.workspace.get_by_name(org.id, workspace_name)
    if not workspace:
        return abort(404)

    workspace.owner = request.storage.workspace.is_owner(workspace.id, user_id)
    workspace.collaborator = request.storage.workspace.is_collaborator(
        workspace.id, user_id)

    return workspace_dashboard_schema.jsonify(workspace)


@view.route('<string:org_name>/<string:workspace_name>/settings/general',
            methods=["PATCH"])
@login_required
def update_workspace_details(org_name: str, workspace_name: str):
    user_id = current_user.id
    org = request.storage.org.get_by_name(org_name)
    if not org:
        return abort(404)

    owns_org = request.storage.org.is_owner(org.id, user_id)
    if not owns_org:
        return abort(404)

    try:
        payload = org_settings_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    if org.settings is None:
        org.settings = {}
    org.settings["email"] = payload.get("email")
    org.settings["url"] = payload.get("url")
    org.settings["logo"] = payload.get("logo")
    org.settings["description"] = payload.get("description")
    request.storage.org.save(org)

    return jsonify(""), 200
