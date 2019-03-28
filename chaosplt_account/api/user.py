# -*- coding: utf-8 -*-
from typing import Any, Dict
from uuid import UUID

from flask import abort, jsonify
from marshmallow import ValidationError

from chaosplt_account.model import Experiment, User
from chaosplt_account.schemas import new_user_schema, user_schema, \
    link_org_schema, link_workspace_schema, my_orgs_schema, \
    my_workspaces_schema, my_experiments_schema, my_executions_schema, \
    my_schedules_schema, light_access_tokens_schema
from chaosplt_account.service import Services

__all__ = ["create_user", "get_user", "delete_user", "get_user_orgs",
           "get_user_workspaces", "link_org_to_user", "unlink_org_from_user",
           "link_workspace_to_user", "unlink_workspace_from_user",
           "get_user_experiments", "get_user_executions", "get_user_schedules",
           "lookup_user", "get_user_tokens"]


def create_user(services: Services, payload: Dict[str, Any]):
    try:
        payload = new_user_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 422
    user = services.account.user.create(
        payload["username"], payload.get('name'), payload.get('email'))
    services.activity.event.record(
        user_id=user.id, event_type="user", phase="create",
        payload={
            "username": payload["username"],
            "name": payload.get('name'),
            "email": payload.get('email')
        })
    return user_schema.jsonify(user), 201


def get_user(services: Services, authed_user: User, user_id: UUID):
    user = services.account.user.get(user_id)
    if not user:
        return abort(404)
    return user_schema.jsonify(user)


def delete_user(services: Services, authed_user: User, user_id: UUID):
    if str(authed_user.id) == str(user_id):
        return "", 204

    user = services.account.user.get(user_id)
    if not user:
        return "", 204

    services.account.user.delete(user_id)
    services.activity.event.record(
        authenticated_user_id=authed_user.id, user_id=user_id,
        event_type="user", phase="delete")
    return "", 204


def get_user_orgs(services: Services, authed_user: User, user_id: UUID):
    user = services.account.user.get(user_id)
    if not user:
        return abort(404)
    return my_orgs_schema.jsonify(user.orgs)


def get_user_tokens(services: Services, authed_user: User, user_id: UUID):
    if user_id != authed_user.id:
        # TODO: should we allow this?
        return []

    tokens = services.auth.access_token.get_by_user(user_id)
    if isinstance(tokens, dict):
        tokens = tokens.values()
    return light_access_tokens_schema.jsonify(tokens)


def get_user_workspaces(services: Services, authed_user: User, user_id: UUID):
    user = services.account.user.get(user_id)
    if not user:
        return abort(404)
    return my_workspaces_schema.jsonify(user.workspaces)


def link_org_to_user(services: Services, authed_user: User, user_id: UUID,
                     org_id: UUID, payload: Dict[str, Any]):
    try:
        payload = link_org_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 422

    user = services.account.user.get(user_id)
    if not user:
        return jsonify({
            "message": "Unknown user"
        }), 422

    org = services.account.org.get(org_id)
    if not org:
        return jsonify({
            "message": "Unknown organization"
        }), 422

    services.account.user.add_org(
        user_id, org_id, owner=payload["owner"])
    services.activity.event.record(
        authenticated_user_id=authed_user.id, user_id=user_id,
        org_id=org_id, event_type="user", phase="link-organization")
    return "", 204


def unlink_org_from_user(services: Services, authed_user: User, user_id: UUID,
                         org_id: UUID):
    user = services.account.user.get(user_id)
    if not user:
        return jsonify({
            "message": "Unknown user"
        }), 422

    org = services.account.org.get(org_id)
    if not org:
        return jsonify({
            "message": "Unknown organization"
        }), 422

    services.account.user.remove_org(user_id, org_id)
    services.activity.event.record(
        authenticated_user_id=authed_user.id, user_id=user_id,
        org_id=org_id, event_type="user", phase="unlink-organization")
    return "", 204


def link_workspace_to_user(services: Services, authed_user: User,
                           user_id: UUID, workspace_id: UUID,
                           payload: Dict[str, Any]):
    try:
        payload = link_workspace_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 422

    user = services.account.user.get(user_id)
    if not user:
        return jsonify({
            "message": "Unknown user"
        }), 422

    workspace = services.account.workspace.get(workspace_id)
    if not workspace:
        return jsonify({
            "message": "Unknown workspace"
        }), 422

    services.account.user.add_workspace(
        user_id, workspace_id, owner=payload["owner"])
    services.activity.event.record(
        authenticated_user_id=authed_user.id, user_id=user_id,
        org_id=workspace.org_id, event_type="user",
        phase="link-workspace", workspace_id=workspace_id)
    return "", 204


def unlink_workspace_from_user(services: Services, authed_user: User,
                               user_id: UUID, workspace_id: UUID):
    user = services.account.user.get(user_id)
    if not user:
        return jsonify({
            "message": "Unknown user"
        }), 422

    workspace = services.account.workspace.get(workspace_id)
    if not workspace:
        return jsonify({
            "message": "Unknown workspace"
        }), 422

    services.account.user.remove_workspace(user_id, workspace_id)
    services.activity.event.record(
        authenticated_user_id=authed_user.id, user_id=user_id,
        org_id=workspace.org_id, event_type="user",
        phase="unlink-workspace", workspace_id=workspace_id)
    return "", 204


def get_user_experiments(services: Services, authed_user: User, user_id: UUID):
    experiments = services.experiment.list_by_user(user_id)
    result = []
    for experiment in experiments:
        o = services.account.org.get(experiment.org_id)
        w = services.account.workspace.get(experiment.workspace_id)
        result.append(
            Experiment(
                id=experiment.id,
                user_id=experiment.user_id,
                org_id=experiment.org_id,
                org_name=o.name,
                workspace_name=w.name,
                workspace_id=experiment.workspace_id,
                created_date=experiment.created_date,
                updated_date=experiment.updated_date,
                payload=experiment.payload,
                executions=experiment.executions
            )
        )
    return my_experiments_schema.jsonify(result)


def get_user_executions(services: Services, authed_user: User, user_id: UUID):
    executions = services.execution.get_by_user(user_id)
    return my_executions_schema.jsonify(executions)


def get_user_schedules(services: Services, authed_user: User, user_id: UUID):
    schedules = services.scheduling.get_by_user(user_id)
    return my_schedules_schema.jsonify(schedules)


def lookup_user(services: Services, authed_user: User, user_name: str):
    user = services.account.registration.get_by_username(user_name)
    if not user:
        return abort(404)

    if not user.is_active:
        return abort(404)

    return user_schema.jsonify(user)
