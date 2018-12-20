from typing import Any, Dict

from chaosplt_grpc import remote_channel
from chaosplt_grpc.experiment.client import create_registration, \
    get_by_id

from ..model import User

__all__ = ["ExperimentService"]


class ExperimentService:
    def __init__(self, config: Dict[str, Any]):
        self.exp_addr = config["grpc"]["experiment"]["addr"]

    def release(self):
        pass

    def create(self, username: str, name: str, email: str) -> User:
        with remote_channel(self.exp_addr) as channel:
            registration = create_registration(channel, username, name, email)
            return User(
                registration.id, registration.username, registration.name,
                registration.email, is_active=registration.is_active,
                is_authenticated=registration.is_authenticated,
                is_anonymous=registration.is_anonymous)

    def get(self, registration_id: str) -> User:
        with remote_channel(self.exp_addr) as channel:
            registration = get_by_id(channel, registration_id)
            return User(
                registration.id, registration.username, registration.name,
                registration.email, is_active=registration.is_active,
                is_authenticated=registration.is_authenticated,
                is_anonymous=registration.is_anonymous)
