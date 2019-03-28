# -*- coding: utf-8 -*-
import calendar
from copy import deepcopy
from datetime import datetime, time
from typing import Any, Dict, List
from uuid import UUID

from croniter import croniter
from flask import abort, jsonify
from marshmallow import ValidationError
import simplejson as json

from chaosplt_account.model import User
from chaosplt_account.schemas import new_org_schema, org_schema, \
    link_workspace_schema, org_schema_short, orgs_schema_tiny, \
    workspaces_schema, org_members_schema, org_member_schema, \
    org_name_schema, org_settings_schema, experiments_schema, \
    schedules_schema
from chaosplt_account.service import Services
from chaosplt_account.storage.model.org import OrgType, DEFAULT_ORG_SETTINGS

__all__ = ["list_all_orgs", "create_org", "get_org", "delete_org",
           "get_org_workspaces", "link_workspace_to_org",
           "unlink_workspace_from_org", "lookup_org", "get_members",
           "get_member", "set_org_name", "set_org_infos",
           "get_schedulings"]


def list_all_orgs(services: Services, authed_user: User):
    orgs = services.account.org.list_all()
    return orgs_schema_tiny.jsonify(orgs)


def create_org(services: Services, authed_user: User, payload: Dict[str, Any]):
    try:
        payload = new_org_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 422

    org_name = payload["name"]

    has_org = services.account.org.has_org_by_name(org_name)
    if has_org:
        return jsonify({
            "name": ["Name already used"]
        }), 409

    user_id = authed_user.id
    org = services.account.org.create(org_name, user_id)
    services.activity.event.record(
        authenticated_user_id=user_id, user_id=user_id,
        org_id=org.id, event_type="organization", phase="create")
    return org_schema.jsonify(org), 201


def get_org(services: Services, authed_user: User, org_id: UUID):
    org = services.account.org.get(org_id)
    if not org:
        return abort(404)

    if authed_user.is_authenticated:
        user_id = authed_user.id
        org.owner = services.account.org.is_owner(org.id, user_id)
        for w in org.workspaces:
            w.owner = services.account.workspace.is_owner(w.id, user_id)

    return org_schema_short.jsonify(org)


def delete_org(services: Services, authed_user: User, org_id: UUID):
    org = services.account.org.get(org_id)
    if org:
        user_id = authed_user.id
        owns_org = services.account.org.is_owner(org.id, user_id)
        if not owns_org:
            return abort(404)

        # cannot delete your own org
        if org.kind == OrgType.personal.value:
            return jsonify({
                "error": "Cannot delete your personal organization"
            }), 422

        services.account.org.delete(org_id)
        services.activity.event.record(
            authenticated_user_id=user_id, user_id=user_id,
            org_id=org.id, event_type="organization", phase="delete")
    return "", 204


def get_org_workspaces(services: Services, authed_user: User, org_id: UUID):
    org = services.account.org.get(org_id)
    if not org:
        return abort(404)
    return workspaces_schema.jsonify(org.workspaces)


def link_workspace_to_org(services: Services, authed_user: User, org_id: UUID,
                          workspace_id: UUID, payload: Dict[str, Any]):
    try:
        payload = link_workspace_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 422

    org = services.account.org.get(org_id)
    if not org:
        return abort(404)

    workspace = services.account.workspace.get(workspace_id)
    if not workspace:
        return abort(404)

    services.account.org.add_workspace(
        org_id, workspace_id, owner=payload["owner"])

    user_id = authed_user.id
    services.activity.event.record(
        authenticated_user_id=user_id, user_id=user_id,
        org_id=org.id, event_type="organization", phase="link-workspace")
    return "", 204


def unlink_workspace_from_org(services: Services, authed_user: User,
                              org_id: UUID, workspace_id: UUID):
    org = services.account.org.get(org_id)
    if not org:
        return abort(404)

    workspace = services.account.workspace.get(workspace_id)
    if not workspace:
        return abort(404)

    services.account.org.remove_org(org_id, workspace_id)
    user_id = authed_user.id
    services.activity.event.record(
        authenticated_user_id=user_id, user_id=user_id,
        org_id=org.id, event_type="organization", phase="unlink-workspace")
    return "", 204


def lookup_org(services: Services, authed_user: User, org_name: str,
               workspaces: List[str] = None):
    org = services.account.org.get_by_name(org_name)
    if not org:
        return abort(404)

    org.owner = services.account.org.is_owner(org.id, authed_user.id)
    if org.owner:
        org.member = True
    else:
        org.member = services.account.org.is_member(org.id, authed_user.id)

    workspaces = workspaces or []
    for workspace_name in workspaces:
        workspace = services.account.workspace.get_by_name(
            org.id, workspace_name)
        if not workspace:
            return abort(404)

    if authed_user.is_authenticated:
        for w in org.workspaces:
            w.owner = services.account.workspace.is_owner(w.id, authed_user.id)

    return org_schema.jsonify(org)


def get_members(services: Services, authed_user: User, org_id: UUID):
    org = services.account.org.get(org_id)
    if not org:
        return abort(404)
    members = services.account.org.get_members(org.id)
    return org_members_schema.jsonify(members)


def get_member(services: Services, authed_user: User, org_id: UUID,
               user_id: UUID):
    org = services.account.org.get(org_id)
    if not org:
        return abort(404)
    member = services.account.org.get_member(org.id, user_id)
    if not member:
        return abort(404)
    return org_member_schema.jsonify(member)


def add_member(services: Services, authed_user: User, org_id: UUID,
               user_id: UUID):
    org = services.account.org.get(org_id)
    if not org:
        return abort(404)

    owns_org = services.account.org.is_owner(org.id, authed_user.id)
    if not owns_org:
        return abort(404)

    member = services.account.org.add_member(org.id, user_id)
    if not member:
        return abort(404)
    return org_member_schema.jsonify(member)


def set_org_name(services: Services, authed_user, org_id: UUID,
                 payload: Dict[str, Any]):
    org = services.account.org.get(org_id)
    if not org:
        return abort(404)

    owns_org = services.account.org.is_owner(org.id, authed_user.id)
    if not owns_org:
        return abort(404)

    try:
        payload = org_name_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 422
    old_name = org.name
    new_name = payload["name"]

    existing_org = services.account.org.get_by_name(new_name)
    if existing_org:
        return jsonify({
            1: {'name': ['Name not available']}
        }), 422

    org.name = new_name
    services.account.org.save(org)

    user_id = authed_user.id
    services.activity.event.record(
        authenticated_user_id=user_id, user_id=user_id,
        org_id=org.id, event_type="organization", phase="rename",
        payload=json.dumps({"old_name": old_name}))

    return jsonify(""), 204


def set_org_infos(services: Services, authed_user, org_id: UUID,
                  payload: Dict[str, Any]):
    org = services.account.org.get(org_id)
    if not org:
        return abort(404)

    owns_org = services.account.org.is_owner(org.id, authed_user.id)
    if not owns_org:
        return abort(404)

    try:
        payload = org_settings_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 422

    if org.settings is None:
        org.settings = deepcopy(DEFAULT_ORG_SETTINGS)
    old_settings = deepcopy(org.settings)
    org.settings["email"] = payload.get("email")
    org.settings["url"] = payload.get("url")
    org.settings["logo"] = payload.get("logo")
    org.settings["description"] = payload.get("description")
    services.account.org.save(org)

    user_id = authed_user.id
    services.activity.event.record(
        authenticated_user_id=user_id, user_id=user_id,
        org_id=org.id, event_type="organization", phase="edit",
        payload=json.dumps({"old_settings": old_settings}))

    return jsonify(""), 204


def get_org_experiments(services: Services, authed_user: User,
                        org_id: UUID):
    org = services.account.org.get(org_id)
    if not org:
        return abort(404)

    experiments = services.experiment.get_by_org(org_id)
    for experiment in experiments:
        workspace = services.account.workspace.get(experiment.workspace_id)
        experiment.org_name = org.name
        experiment.workspace_name = workspace.name

        user = services.account.user.get(experiment.user_id)
        if user:
            experiment.username = user.username
            experiment.user_org_name = user.org_name

    return experiments_schema.jsonify(experiments)


def get_schedulings(services: Services, authed_user: User,
                    org_id: UUID):
    org = services.account.org.get(org_id)
    if not org:
        return abort(404)

    schedules = services.scheduling.get_by_org(org_id)
    for schedule in schedules:
        workspace = services.account.workspace.get(schedule.workspace_id)
        schedule.org_name = org.name
        schedule.workspace_name = workspace.name

        user = services.account.user.get(schedule.user_id)
        if user:
            schedule.username = user.username
            schedule.user_org_name = user.org_name

        experiment = services.experiment.get(schedule.experiment_id)
        if experiment:
            schedule.experiment_name = experiment.payload["title"]

        if schedule.cron:
            schedule.plan = []
            candidates = list(calendar.Calendar().itermonthdates(2019, 3))
            start = max(
                schedule.active_from,
                datetime.combine(candidates[0], time.min))
            g = croniter(schedule.cron, start_time=start).all_next(datetime)
            repeat = None if not schedule.repeat else schedule.repeat - 1
            for i, d in enumerate(g):
                if repeat and i > repeat:
                    break
                if d.date() not in candidates:
                    break
                schedule.plan.append(d)

    return schedules_schema.jsonify(schedules)
