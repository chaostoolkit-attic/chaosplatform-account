# -*- coding: utf-8 -*-
from uuid import UUID

from flask import abort, Blueprint, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError

from chaosplt_account.schemas import new_org_schema, org_schema, \
    link_workspace_schema, org_schema_short, orgs_schema_tiny, \
    workspaces_schema

__all__ = ["api"]

api = Blueprint("org", __name__)


@api.route('', methods=['GET'])
@login_required
def list_all():
    orgs = request.services.account.org.list_all()
    return orgs_schema_tiny.jsonify(orgs)


@api.route('', methods=['POST'])
@login_required
def new():
    user_id = current_user.id
    try:
        payload = new_org_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    org_name = payload["name"]

    has_org = request.services.account.org.has_org_by_name(org_name)
    if has_org:
        return jsonify({
            "message": "Name already used"
        }), 409

    org = request.services.account.org.create(org_name, user_id)
    return org_schema.jsonify(org), 201


@api.route('<uuid:org_id>', methods=['GET'])
@login_required
def get(org_id: UUID):
    org = request.services.account.org.get(org_id)
    if not org:
        return abort(404)
    return org_schema_short.jsonify(org)


@api.route('<uuid:org_id>', methods=['DELETE'])
@login_required
def delete(org_id: UUID):
    request.services.account.org.delete(org_id)
    return "", 204


@api.route('<uuid:user_id>/workspaces', methods=['GET'])
@login_required
def get_user_workspaces(org_id: UUID):
    org = request.services.account.org.get(org_id)
    if not org:
        return abort(404)
    return workspaces_schema.jsonify(org.workspaces)


@api.route('<uuid:org_id>/workspaces/<uuid:workspace_id>', methods=['PUT'])
@login_required
def link_workspace_to_org(org_id: UUID, workspace_id: UUID):
    try:
        payload = link_workspace_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    org = request.services.account.org.get(org_id)
    if not org:
        return abort(404)

    workspace = request.services.account.workspace.get(workspace_id)
    if not workspace:
        return abort(404)

    request.services.account.org.add_workspace(
        org_id, workspace_id, owner=payload["owner"])
    return "", 204


@api.route('<uuid:org_id>/organizations/<uuid:workspace_id>',
           methods=['DELETE'])
@login_required
def unlink_workspace_from_org(org_id: UUID, workspace_id: UUID):
    org = request.services.account.org.get(org_id)
    if not org:
        return abort(404)

    workspace = request.services.account.workspace.get(workspace_id)
    if not workspace:
        return abort(404)

    request.services.account.org.remove_org(org_id, workspace_id)
    return "", 204
