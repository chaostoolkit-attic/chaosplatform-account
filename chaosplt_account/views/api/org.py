# -*- coding: utf-8 -*-
from uuid import UUID

from flask import Blueprint, request
from flask_login import current_user, login_required

from chaosplt_account.api.org import list_all_orgs, create_org, get_org, \
    delete_org, get_org_workspaces, link_workspace_to_org, add_member, \
    unlink_workspace_from_org, lookup_org, get_members, get_member, \
    set_org_name

__all__ = ["api"]

api = Blueprint("org", __name__)


@api.route('', methods=['GET'])
@login_required
def api_list_all():
    return list_all_orgs(request.services, current_user)


@api.route('', methods=['POST'])
@login_required
def api_new():
    return create_org(request.services, current_user, request.json)


@api.route('', methods=['POST'])
@login_required
def update():
    return create_org(request.services, current_user, request.json)


@api.route('<uuid:org_id>', methods=['GET'])
@login_required
def get_one(org_id: UUID):
    return get_org(request.services, current_user, org_id)


@api.route('<uuid:org_id>', methods=['DELETE'])
@login_required
def api_delete(org_id: UUID):
    return delete_org(request.services, current_user, org_id)


@api.route('<uuid:org_id>/workspaces', methods=['GET'])
@login_required
def api_get_org_workspaces(org_id: UUID):
    return get_org_workspaces(request.services, current_user, org_id)


@api.route('<uuid:org_id>/workspaces/<uuid:workspace_id>', methods=['PUT'])
@login_required
def api_link_workspace_to_org(org_id: UUID, workspace_id: UUID):
    return link_workspace_to_org(
        request.services, current_user, org_id, workspace_id)


@api.route('<uuid:org_id>/organizations/<uuid:workspace_id>',
           methods=['DELETE'])
@login_required
def api_unlink_workspace_from_org(org_id: UUID, workspace_id: UUID):
    return unlink_workspace_from_org(
        request.services, current_user, org_id, workspace_id)


@api.route('lookup/<string:org_name>', methods=['GET'])
@login_required
def api_lookup_org(org_name: str):
    workspaces = request.args.get("workspaces")
    return lookup_org(request.services, current_user, org_name, workspaces)


@api.route('<uuid:org_id>/members', methods=["GET"])
@login_required
def api_get_members(org_id: UUID):
    return get_members(request.services, current_user, org_id)


@api.route('<uuid:org_id>/members/<uuid:user_id>', methods=["GET"])
@login_required
def api_get_member(org_id: UUID, user_id: UUID):
    return get_member(request.services, current_user, org_id, user_id)


@api.route('<uuid:org_id>/name', methods=["PATCH"])
@login_required
def update_org_name(org_id: UUID):
    return set_org_name(request.services, current_user, org_id, request.json)


@api.route('<uuid:org_id>/members/<uuid:user_id>', methods=["PUT"])
@login_required
def api_add_member(org_id: UUID, user_id: UUID):
    return add_member(request.services, current_user, org_id, user_id)
