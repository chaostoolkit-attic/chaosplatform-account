# -*- coding: utf-8 -*-
from uuid import UUID

from flask import Blueprint, request
from flask_login import current_user, login_required

from chaosplt_account.api.workspace import list_all_workspaces, \
    create_workspace, get_workspace, delete_workspace, \
    get_workspace_experiments, get_workspace_collaborators, \
    get_workspace_collaborator, lookup_workspace_by_name

__all__ = ["api"]

api = Blueprint("workspace", __name__)


@api.route('', methods=['GET'])
@login_required
def api_list_all():
    return list_all_workspaces(request.services, current_user)


@api.route('', methods=['POST'])
@login_required
def api_new():
    return create_workspace(request.services, current_user, request.json)


@api.route('<uuid:workspace_id>', methods=['GET'])
@login_required
def get_one(workspace_id: UUID):
    return get_workspace(request.services, current_user, workspace_id)


@api.route('<uuid:workspace_id>', methods=['DELETE'])
@login_required
def api_delete(workspace_id: UUID):
    return delete_workspace(request.services, current_user, workspace_id)


@api.route('<uuid:workspace_id>/experiments', methods=['GET'])
@login_required
def api_get_experiments(workspace_id: UUID):
    return get_workspace_experiments(
        request.services, current_user, workspace_id)


@api.route('<uuid:workspace_id>/collaborators', methods=["GET"])
@login_required
def api_collaborator_settings(workspace_id: UUID):
    return get_workspace_collaborators(
        request.services, current_user, workspace_id)


@api.route('<uuid:workspace_id>/collaborators/<uuid:user_id>', methods=["GET"])
@login_required
def api_get_collaborator(workspace_id: UUID, user_id: UUID):
    return get_workspace_collaborator(
        request.services, current_user, workspace_id, user_id)


@api.route('lookup/<string:workspace_name>', methods=['GET'])
@login_required
def api_lookup_workspace(workspace_name: str):
    org_name = request.args.get("org")
    return lookup_workspace_by_name(
        request.services, current_user, org_name, workspace_name)
