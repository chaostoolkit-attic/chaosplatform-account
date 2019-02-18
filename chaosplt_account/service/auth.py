from typing import Any, Dict
from uuid import UUID

import attr
from chaosplt_grpc import remote_channel
from chaosplt_grpc.auth.client import create_access_token, \
    remove_access_token, get_access_token, get_access_token_by_name, \
    get_access_tokens_by_user

from ..model import AccessToken

__all__ = ["AuthService"]


class AccessTokenService:
    def __init__(self, config: Dict[str, Any]):
        self.auth_addr = config["grpc"]["auth"]["address"]

    def release(self):
        pass

    def create(self, name: str, user_id: UUID) -> AccessToken:
        with remote_channel(self.exp_addr) as channel:
            token = create_access_token(channel, str(user_id), name)
            return AccessToken(
                token.id, token.user_id, token.access_token,
                token.refresh_token, token.revoked, token.issued_on,
                token.last_used_on)

    def delete(self, user_id: UUID, token_id: UUID) -> AccessToken:
        with remote_channel(self.exp_addr) as channel:
            remove_access_token(channel, str(user_id), token_id)

    def get(self, token_id: UUID) -> AccessToken:
        with remote_channel(self.exp_addr) as channel:
            token = get_access_token(channel, str(token_id))
            if not token:
                return

            return AccessToken(
                token.id, token.user_id, token.access_token,
                token.refresh_token, token.revoked, token.issued_on,
                token.last_used_on)

    def get_by_name(self, user_id: UUID, name: str) -> AccessToken:
        with remote_channel(self.exp_addr) as channel:
            token = get_access_token_by_name(channel, str(user_id), name)
            if not token:
                return

            return AccessToken(
                token.id, token.user_id, token.access_token,
                token.refresh_token, token.revoked, token.issued_on,
                token.last_used_on)

    def get_by_user(self, user_id: UUID) -> AccessToken:
        with remote_channel(self.exp_addr) as channel:
            tokens = get_access_tokens_by_user(channel, str(user_id))
            result = []
            for token in tokens:
                tokens.append(AccessToken(
                    token.id, token.user_id, token.access_token,
                    token.refresh_token, token.revoked, token.issued_on,
                    token.last_used_on))
            return result


@attr.s
class AuthService:
    access_token: AccessTokenService = attr.ib()
