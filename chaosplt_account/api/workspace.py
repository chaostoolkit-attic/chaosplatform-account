# -*- coding: utf-8 -*-
from typing import Any, Dict
from uuid import UUID

from flask import abort, jsonify
from marshmallow import ValidationError

from chaosplt_account.model import User
from chaosplt_account.schemas import new_workspace_schema, workspace_schema, \
    workspaces_schema_tiny, workspace_schema_short, \
    experiments_schema, workspace_collaborators_schema, \
    workspace_collaborator_schema, experiment_schema
from chaosplt_account.service import Services

__all__ = ["list_all_workspaces", "create_workspace", "get_workspace",
           "delete_workspace", "get_workspace_experiments",
           "get_workspace_collaborators", "get_workspace_collaborator",
           "lookup_workspace_by_name"]


def list_all_workspaces(services: Services, authed_user: User):
    workspaces = services.account.workspace.list_all()
    return workspaces_schema_tiny.jsonify(workspaces)


def create_workspace(services: Services, authed_user: User,
                     payload: Dict[str, Any]):
    user_id = authed_user.id
    try:
        payload = new_workspace_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 422

    workspace_name = payload["name"]
    workspace_visibility = payload.get("visibility")
    org_id = payload["org"]
    workspace_type = payload.get("type", "public")
    workspace_svc = services.account.workspace

    org = services.account.org.get(org_id=org_id)
    if not org:
        return jsonify({
            "org": ["Unknown organization"]
        }), 422

    has_workspace = services.account.org.has_workspace_by_name(
        org_id, workspace_name)
    if has_workspace:
        return jsonify({
            "name": ["Name already used in this organization"]
        }), 409

    user_id = authed_user.id
    workspace = workspace_svc.create(
        workspace_name, org_id, user_id, workspace_visibility,
        workspace_type=workspace_type)
    services.activity.event.record(
        authenticated_user_id=user_id, user_id=user_id,
        org_id=workspace.org_id, event_type="workspace", phase="create",
        workspace_id=workspace.id)
    return workspace_schema.jsonify(workspace), 201


def get_workspace(services: Services, authed_user: User, workspace_id: UUID):
    workspace = services.account.workspace.get(workspace_id)
    if not workspace:
        return abort(404)
    return workspace_schema_short.jsonify(workspace)


def delete_workspace(services: Services, authed_user: User,
                     workspace_id: UUID):
    workspace = services.account.workspace.get(workspace_id)
    if workspace:
        user_id = authed_user.id
        services.account.workspace.delete(workspace_id)
        services.activity.event.record(
            authenticated_user_id=user_id, user_id=user_id,
            org_id=workspace.org_id, event_type="workspace", phase="delete",
            workspace_id=workspace.id)
    return "", 204


def get_workspace_experiments(services: Services, authed_user: User,
                              workspace_id: UUID):
    workspace = services.account.workspace.get(workspace_id)
    if not workspace:
        return abort(404)

    experiments = services.experiment.get_by_workspace(workspace_id)
    return experiments_schema.jsonify(experiments)


def get_workspace_experiment(services: Services, authed_user: User,
                             workspace_id: UUID, experiment_id: UUID):
    workspace = services.account.workspace.get(workspace_id)
    if not workspace:
        return abort(404)

    experiment = services.experiment.get(experiment_id)
    if experiment.workspace_id != workspace_id:
        return abort(404)

    user = services.account.user.get(experiment.user_id)
    if user:
        experiment.username = user.username
        experiment.user_org_name = user.org_name

    return experiment_schema.jsonify(experiment)


def get_workspace_collaborators(services: Services, authed_user: User,
                                workspace_id: UUID):
    workspace = services.account.workspace.get(workspace_id)
    if not workspace:
        return abort(404)
    collaborators = services.account.workspace.get_collaborators(workspace.id)
    return workspace_collaborators_schema.jsonify(collaborators)


def get_workspace_collaborator(services: Services, authed_user: User,
                               workspace_id: UUID, user_id: UUID):
    workspace = services.account.workspace.get(workspace_id)
    if not workspace:
        return abort(404)
    collaborator = services.account.workspace.get_collaborator(
        workspace.id, user_id)
    if not collaborator:
        return abort(404)
    return workspace_collaborator_schema.jsonify(collaborator)


def lookup_workspace_by_name(services: Services, authed_user: User,
                             org_name: str, workspace_name: str):
    if not org_name:
        return abort(404)

    org = services.account.org.get_by_name(org_name)
    if not org:
        return abort(404)

    workspace = services.account.workspace.get_by_name(
        org.id, workspace_name)
    if not workspace:
        return abort(404)

    return workspace_schema.jsonify(workspace)
