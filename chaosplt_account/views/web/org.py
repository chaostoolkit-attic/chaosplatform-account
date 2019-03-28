# -*- coding: utf-8 -*-
from uuid import UUID

from flask import abort, Blueprint, request
from flask_login import current_user, login_required

from chaosplt_account.api.org import create_org, get_org, \
    lookup_org, get_members, get_member, set_org_name, delete_org, \
    set_org_infos, add_member, get_org_experiments, get_schedulings
from chaosplt_account.api.token import list_org_tokens
from chaosplt_account.schemas import org_info_schema, workspace_info_schema

__all__ = ["view"]

view = Blueprint("org", __name__)


@view.route('<string:org_name>', methods=["GET"])
@login_required
def org(org_name: str):
    org = request.storage.org.get_by_name(org_name)
    if not org:
        return abort(404)

    org.owner = False
    org.member = False
    user_id = current_user.id
    user = request.storage.user.get(user_id)
    if user:
        org.owner = request.storage.org.is_owner(org.id, user_id)
        org.member = request.storage.org.is_member(org.id, user_id)

    return org_info_schema.jsonify(org)


@view.route('<uuid:org_id>', methods=['GET'])
@login_required
def get_one(org_id: UUID):
    return get_org(request.services, org_id)


@view.route('<uuid:org_id>', methods=["DELETE"])
@login_required
def view_delete_org(org_id: UUID):
    return delete_org(request.services, current_user, org_id)


@view.route('<uuid:org_id>/infos', methods=["PATCH"])
@login_required
def update_org_infos(org_id: UUID):
    return set_org_infos(request.services, current_user, org_id, request.json)


@view.route('<uuid:org_id>/name', methods=["PATCH"])
@login_required
def update_org_name(org_id: UUID):
    return set_org_name(request.services, current_user, org_id, request.json)


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


@view.route('', methods=['POST'])
@login_required
def view_new():
    return create_org(request.services, current_user, request.json)


@view.route('lookup/<string:org_name>', methods=['GET'])
@login_required
def view_lookup_org(org_name: str):
    workspaces = request.args.get("workspaces")
    return lookup_org(request.services, current_user, org_name, workspaces)


@view.route('<uuid:org_id>/members', methods=["GET"])
@login_required
def view_get_members(org_id: UUID):
    return get_members(request.services, current_user, org_id)


@view.route('<uuid:org_id>/members/<uuid:user_id>', methods=["GET"])
@login_required
def view_get_member(org_id: UUID, user_id: UUID):
    return get_member(request.services, current_user, org_id, user_id)


@view.route('<uuid:org_id>/members/<uuid:user_id>', methods=["PUT"])
@login_required
def view_add_member(org_id: UUID, user_id: UUID):
    return add_member(request.services, current_user, org_id, user_id)


@view.route('<uuid:org_id>/experiments', methods=['GET'])
def view_get_org_experiments(org_id: UUID):
    return get_org_experiments(
        request.services, current_user, org_id)


@view.route('<uuid:org_id>/schedules', methods=["GET"])
@login_required
def view_get_schedules(org_id: UUID):
    return get_schedulings(request.services, current_user, org_id)


@view.route('<uuid:org_id>/tokens', methods=["GET"])
@login_required
def view_get_tokens(org_id: UUID):
    return list_org_tokens(request.services, current_user, org_id)
