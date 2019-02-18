# -*- coding: utf-8 -*-
from uuid import UUID

from flask import abort, Blueprint, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError

from chaosplt_account.schemas import new_workspace_schema, workspace_schema, \
    workspaces_schema_tiny, workspace_schema_short, \
    experiments_schema, workspace_collaborators_schema

__all__ = ["api"]

api = Blueprint("workspace", __name__)


@api.route('', methods=['GET'])
@login_required
def list_all():
    workspaces = request.services.account.workspace.list_all()
    return workspaces_schema_tiny.jsonify(workspaces)


@api.route('', methods=['POST'])
@login_required
def new():
    user_id = current_user.id
    try:
        payload = new_workspace_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    workspace_name = payload["name"]
    workspace_type = payload["kind"]
    workspace_visibility = payload["visibility"]
    org_id = payload["org"]
    workspace_svc = request.services.account.workspace

    has_org = request.services.account.org.has_org_by_id(org_id=org_id)
    if not has_org:
        return jsonify({
            "org": ["Unknown organization"]
        }), 422

    has_workspace = request.services.account.org.has_workspace_by_name(
        org_id, workspace_name)
    if has_workspace:
        return jsonify({
            "name": ["Name already used in this organization"]
        }), 409

    workspace = workspace_svc.create(
        workspace_name, org_id, user_id, workspace_visibility)
    return workspace_schema.jsonify(workspace), 201


@api.route('<uuid:workspace_id>', methods=['GET'])
@login_required
def get(workspace_id: UUID):
    workspace = request.services.account.workspace.get(workspace_id)
    if not workspace:
        return abort(404)
    return workspace_schema_short.jsonify(workspace)


@api.route('<uuid:workspace_id>', methods=['DELETE'])
@login_required
def delete(workspace_id: UUID):
    request.services.account.workspace.delete(workspace_id)
    return "", 204


@api.route('<uuid:workspace_id>/experiments', methods=['GET'])
@login_required
def get_experiments(workspace_id: UUID):
    workspace = request.services.account.workspace.get(workspace_id)
    if not workspace:
        return abort(404)

    experiments = request.services.experiment.get_by_workspace(workspace_id)
    return experiments_schema.jsonify(experiments)


@api.route('<string:workspace_id>/collaborators', methods=["GET"])
@login_required
def collaborator_settings(workspace_id: UUID):
    user_id = current_user.id
    workspace = request.services.account.workspace.get(workspace_id)
    if not workspace:
        return abort(404)
    collaborators = request.storage.workspace.get_collaborators(workspace.id)
    return workspace_collaborators_schema.jsonify(collaborators)


@api.route('lookup/<string:workspace_name>', methods=['GET'])
@login_required
def lookup_workspace(workspace_name: str):
    org_name = request.args.get("org")
    if not org_name:
        return abort(404)

    org = request.services.account.workspace.get_by_name(org_name)
    if not org:
        return abort(404)

    workspace = request.services.account.workspace.get_by_name(
        org.id, workspace_name)
    if not workspace:
        return abort(404)

    return workspace_schema.jsonify(workspace)
