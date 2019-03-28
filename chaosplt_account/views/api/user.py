# -*- coding: utf-8 -*-
from uuid import UUID

from flask import Blueprint, request
from flask_login import current_user, login_required

from chaosplt_account.api.user import create_user, get_user, delete_user, \
    get_user_orgs, get_user_workspaces, link_org_to_user, \
    unlink_org_from_user, link_workspace_to_user, unlink_workspace_from_user, \
    get_user_experiments, get_user_executions, get_user_schedules

__all__ = ["api"]

api = Blueprint("user", __name__)


@api.route('', methods=['POST'])
@login_required
def api_new():
    return create_user(request.services, request.json)


@api.route('<uuid:user_id>', methods=['GET'])
@login_required
def get(user_id: UUID):
    return get_user(request.services, current_user, user_id)


@api.route('<uuid:user_id>', methods=['DELETE'])
@login_required
def api_delete(user_id: UUID):
    return delete_user(request.services, current_user, user_id)


@api.route('<uuid:user_id>/organizations', methods=['GET'])
@login_required
def api_get_user_orgs(user_id: UUID):
    return get_user_orgs(request.services, current_user, user_id)


@api.route('<uuid:user_id>/workspaces', methods=['GET'])
@login_required
def api_get_user_workspaces(user_id: UUID):
    return get_user_workspaces(request.services, current_user, user_id)


@api.route('<uuid:user_id>/organizations/<uuid:org_id>', methods=['PUT'])
@login_required
def api_link_org_to_user(user_id: UUID, org_id: UUID):
    return link_org_to_user(
        request.services, current_user, user_id, org_id, request.json)


@api.route('<uuid:user_id>/organizations/<uuid:org_id>', methods=['DELETE'])
@login_required
def api_unlink_org_from_user(user_id: UUID, org_id: UUID):
    return unlink_org_from_user(
        request.services, current_user, user_id, org_id)


@api.route('<uuid:user_id>/workspaces/<uuid:workspace_id>', methods=['PUT'])
@login_required
def api_link_workspace_to_user(user_id: UUID, workspace_id: UUID):
    return link_workspace_to_user(
        request.services, current_user, user_id, workspace_id, request.json)


@api.route('<uuid:user_id>/workspaces/<uuid:workspace_id>', methods=['DELETE'])
@login_required
def api_unlink_workspace_from_user(user_id: UUID, workspace_id: UUID):
    return unlink_workspace_from_user(
        request.services, current_user, user_id, workspace_id)


@api.route('<uuid:user_id>/experiments', methods=['GET'])
@login_required
def api_get_user_experiments(user_id: UUID):
    return get_user_experiments(request.services, current_user, user_id)


@api.route('<uuid:user_id>/executions', methods=['GET'])
@login_required
def api_get_user_executions(user_id: UUID):
    return get_user_executions(request.services, current_user, user_id)


@api.route('<uuid:user_id>/schedules', methods=['GET'])
@login_required
def api_get_user_schedules(user_id: UUID):
    return get_user_schedules(request.services, current_user, user_id)
