# -*- coding: utf-8 -*-
from uuid import UUID

from flask import abort, Blueprint, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError

from chaosplt_account.schemas import org_dashboard_schema, org_info_schema, \
    org_members_dashboard_schema, org_settings_schema, org_name_schema

__all__ = ["view"]

view = Blueprint("web_app_org", __name__)


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


@view.route('<string:org_name>', methods=["DELETE"])
@login_required
def delete_org(org_name: str):
    user_id = current_user.id
    user = request.storage.user.get(user_id)
    if not user:
        return abort(404)
    
    org = request.storage.org.get_by_name(org_name)
    if not org:
        return abort(404)

    owns_org = request.storage.org.is_owner(org.id, user_id)
    if not owns_org:
        return abort(401)

    request.storage.org.delete(org.id)
    return jsonify(""), 204


@view.route('<string:org_name>/settings/general', methods=["GET"])
@login_required
def general_settings(org_name: str):
    user_id = current_user.id
    org = request.storage.org.get_by_name(org_name)
    if not org:
        return abort(404)
    
    owns_org = request.storage.org.is_owner(org.id, user_id)
    if not owns_org:
        return abort(404)

    org.owner = True
    org.member = True

    return org_dashboard_schema.jsonify(org)


@view.route('<string:org_name>/settings/general/details', methods=["PATCH"])
@login_required
def update_org_details(org_name: str):
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



@view.route('<string:org_name>/settings/general/name', methods=["PATCH"])
@login_required
def update_org_name(org_name: str):
    user_id = current_user.id
    org = request.storage.org.get_by_name(org_name)
    if not org:
        return abort(404)

    owns_org = request.storage.org.is_owner(org.id, user_id)
    if not owns_org:
        return abort(404)

    try:
        payload = org_name_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422
    org.name = payload["name"]
    request.storage.org.save(org)

    return jsonify(""), 200


@view.route('<string:org_name>/settings/members', methods=["GET"])
@login_required
def member_settings(org_name: str):
    user_id = current_user.id
    org = request.storage.org.get_by_name(org_name)
    if not org:
        return abort(404)
    members = request.storage.org.get_members(org.id)
    return org_members_dashboard_schema.jsonify({
        "users": members
    })
