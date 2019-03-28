# -*- coding: utf-8 -*-
from typing import Any, Dict
from uuid import UUID

from flask import abort, jsonify
from marshmallow import ValidationError

from chaosplt_account.model import User
from chaosplt_account.schemas import access_tokens_schema, \
    new_access_token_schema, created_access_token_schema, \
    light_access_tokens_schema
from chaosplt_account.service import Services

__all__ = ["create_token", "list_tokens", "delete_token", "revoke_token",
           "list_org_tokens", "list_workspace_tokens"]


def list_tokens(services: Services, authed_user: User):
    tokens = services.auth.access_token.get_by_user(authed_user.id)
    if isinstance(tokens, dict):
        tokens = tokens.values()
    return access_tokens_schema.jsonify(tokens)


def delete_token(services: Services, authed_user: User, token_id: UUID):
    services.auth.access_token.delete(authed_user.id, token_id)
    return jsonify(""), 204


def revoke_token(services: Services, authed_user: User, token_id: UUID):
    token = services.auth.access_token.get(token_id)
    if not token or token.user_id != authed_user.id:
        return abort(404)

    if token.revoked:
        return jsonify(""), 204

    services.auth.access_token.revoke(authed_user.id, token_id)
    return jsonify(""), 200


def create_token(services: Services, authed_user: User,
                 payload: Dict[str, Any]):
    try:
        payload = new_access_token_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 422

    name = payload["name"]

    token = services.auth.access_token.get_by_name(authed_user.id, name)
    if token:
        return jsonify({'name': ['"{}" is already used.'.format(name)]}), 422

    token = services.auth.access_token.create(name, authed_user.id)
    return created_access_token_schema.jsonify(token)


def list_org_tokens(services: Services, authed_user: User, org_id: UUID):
    tokens = services.auth.access_token.get_by_org(org_id)
    return light_access_tokens_schema.jsonify(tokens)


def list_workspace_tokens(services: Services, authed_user: User,
                          workspace_id: UUID):
    tokens = services.auth.access_token.get_by_workspace(workspace_id)
    return light_access_tokens_schema.jsonify(tokens)
