# -*- coding: utf-8 -*-
from uuid import UUID

from flask import abort, Blueprint, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError

from chaosplt_account.schemas import new_user_schema, user_schema, \
    link_org_schema, link_workspace_schema, my_orgs_schema, \
    my_workspaces_schema, my_experiments_schema, my_executions_schema, \
    my_schedules_schema

__all__ = ["api"]

api = Blueprint("user", __name__)


@api.route('', methods=['POST'])
@login_required
def new():
    try:
        payload = new_user_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422
    user = request.storage.user.create(payload["username"])
    return user_schema.jsonify(user)


@api.route('<uuid:user_id>', methods=['GET'])
@login_required
def get(user_id: UUID):
    user = request.storage.user.get(user_id)
    if not user:
        return abort(404)
    return user_schema.jsonify(user)


@api.route('<uuid:user_id>', methods=['DELETE'])
@login_required
def delete(user_id: UUID):
    request.storage.user.delete(user_id)
    return "", 204


@api.route('<uuid:user_id>/organizations', methods=['GET'])
@login_required
def get_user_orgs(user_id: UUID):
    user = request.storage.user.get(user_id)
    if not user:
        return abort(404)
    return my_orgs_schema.jsonify(user.orgs)


@api.route('<uuid:user_id>/workspaces', methods=['GET'])
@login_required
def get_user_workspaces(user_id: UUID):
    user = request.storage.user.get(user_id)
    if not user:
        return abort(404)
    return my_workspaces_schema.jsonify(user.workspaces)


@api.route('<uuid:user_id>/organizations/<uuid:org_id>', methods=['PUT'])
@login_required
def link_org_to_user(user_id: UUID, org_id: UUID):
    try:
        payload = link_org_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    user = request.storage.user.get(user_id)
    if not user:
        return jsonify({
            "message": "Unknown user"
        }), 422

    org = request.storage.org.get(org_id)
    if not org:
        return jsonify({
            "message": "Unknown organization"
        }), 422

    current_user

    request.storage.user.add_org(
        user_id, org_id, owner=payload["owner"])
    return "", 204


@api.route('<uuid:user_id>/organizations/<uuid:org_id>', methods=['DELETE'])
@login_required
def unlink_org_from_user(user_id: UUID, org_id: UUID):
    user = request.services.account.user.get(user_id)
    if not user:
        return jsonify({
            "message": "Unknown user"
        }), 422

    org = request.storage.org.get(org_id)
    if not org:
        return jsonify({
            "message": "Unknown organization"
        }), 422

    request.storage.user.remove_org(user_id, org_id)
    return "", 204


@api.route('<uuid:user_id>/workspaces/<uuid:workspace_id>', methods=['PUT'])
@login_required
def link_workspace_to_user(user_id: UUID, workspace_id: UUID):
    try:
        payload = link_workspace_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    user = request.storage.user.get(user_id)
    if not user:
        return jsonify({
            "message": "Unknown user"
        }), 422

    workspace = request.storage.workspace.get(workspace_id)
    if not workspace:
        return jsonify({
            "message": "Unknown workspace"
        }), 422

    request.storage.user.add_workspace(
        user_id, workspace_id, owner=payload["owner"])
    return "", 204


@api.route('<uuid:user_id>/workspaces/<uuid:workspace_id>', methods=['DELETE'])
@login_required
def unlink_workspace_from_user(user_id: UUID, workspace_id: UUID):
    user = request.storage.user.get(user_id)
    if not user:
        return jsonify({
            "message": "Unknown user"
        }), 422

    workspace = request.storage.workspace.get(workspace_id)
    if not workspace:
        return jsonify({
            "message": "Unknown workspace"
        }), 422

    request.storage.user.remove_workspace(user_id, workspace_id)
    return "", 204


@api.route('<uuid:user_id>/experiments', methods=['GET'])
@login_required
def get_user_experiments(user_id: UUID):
    experiments = request.services.experiment.list_by_user(user_id)
    return my_experiments_schema.jsonify(experiments)


@api.route('<uuid:user_id>/executions', methods=['GET'])
@login_required
def get_user_executions(user_id: UUID):
    executions = request.services.execution.get_by_user(user_id)
    return my_executions_schema.jsonify(executions)


@api.route('<uuid:user_id>/schedules', methods=['GET'])
@login_required
def get_user_schedules(user_id: UUID):
    schedules = request.services.scheduling.get_by_user(user_id)
    return my_schedules_schema.jsonify(schedules)
