import logging
from typing import NoReturn

from chaosplt_grpc.registration.message import Registration
from chaosplt_grpc.registration.server import \
    RegistrationService as GRPCRegistrationService

from ..storage import AccountStorage

__all__ = ["RegistrationRPC"]
logger = logging.getLogger("chaosplatform")


class RegistrationRPC(GRPCRegistrationService):
    def __init__(self, storage: AccountStorage):
        GRPCRegistrationService.__init__(self)
        self.storage = storage

    def create_registration(self, username: str, name: str,
                            email: str) -> Registration:
        user = self.storage.registration.create(username, name, email)
        logger.info("User {} is registered".format(user.id))
        return Registration(
            id=str(user.id),
            username=user.username,
            name=user.name,
            email=user.email,
            is_active=True,
            is_authenticated=True,
            is_anonymous=False
        )

    def delete_registration(self, registration_id: str) -> NoReturn:
        logger.info("User {} now deleted".format(registration_id))
        self.storage.registration.delete(registration_id)

    def get_by_id(self, registration_id: str) -> Registration:
        user = self.storage.registration.get(registration_id)
        if not user:
            logger.info("User {} does not exist".format(registration_id))
            return None

        return Registration(
            id=str(user.id),
            username=user.username,
            name=user.name,
            email=user.email,
            is_active=user.is_active,
            is_authenticated=user.is_authenticated,
            is_anonymous=user.is_active
        )
