# -*- coding: utf-8 -*-
from uuid import UUID

from flask import Blueprint, request
from flask_login import current_user, login_required

from chaosplt_account.api.workspace import \
    create_workspace, get_workspace, get_workspace_experiments, \
    get_workspace_collaborators, get_workspace_collaborator, \
    lookup_workspace_by_name, get_workspace_experiment

view = Blueprint("workspace", __name__)


__all__ = ["view"]


@view.route('<uuid:workspace_id>', methods=['GET'])
@login_required
def get_one(workspace_id: UUID):
    return get_workspace(request.services, workspace_id)


@view.route('', methods=['POST'])
@login_required
def view_new():
    return create_workspace(request.services, current_user, request.json)


@view.route('<uuid:workspace_id>/collaborators', methods=["GET"])
@login_required
def view_collaborator_settings(workspace_id: UUID):
    return get_workspace_collaborators(
        request.services, current_user, workspace_id)


@view.route('<uuid:workspace_id>/collaborators/<uuid:user_id>',
            methods=["GET"])
@login_required
def view_get_collaborator(workspace_id: UUID, user_id: UUID):
    return get_workspace_collaborator(
        request.services, current_user, workspace_id, user_id)


@view.route('lookup/<string:workspace_name>', methods=['GET'])
@login_required
def view_lookup_workspace(workspace_name: str):
    org_name = request.args.get("org")
    return lookup_workspace_by_name(
        request.services, current_user, org_name, workspace_name)


@view.route('<uuid:workspace_id>/experiments', methods=['GET'])
def view_get_user_experiments(workspace_id: UUID):
    return get_workspace_experiments(
        request.services, current_user, workspace_id)


@view.route('<uuid:workspace_id>/experiments/<uuid:experiment_id>',
            methods=['GET'])
def view_get_user_experiment(workspace_id: UUID, experiment_id: UUID):
    return get_workspace_experiment(
        request.services, current_user, workspace_id, experiment_id)
