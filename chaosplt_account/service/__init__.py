from typing import Any, Dict, NoReturn

import attr

from .activity import ActivityService
from .auth import AuthService, AccessTokenService

__all__ = ["initialize_services", "shutdown_services", "services", "Services"]


@attr.s
class Services:
    auth: AuthService = attr.ib(default=None)
    activity: ActivityService = attr.ib(default=None)


def initialize_services(services: Services, config: Dict[str, Any]):
    if not services.auth:
        services.auth = AuthService(AccessTokenService(config))

    if not services.activity:
        services.activity = ActivityService(config)


def shutdown_services(services: Services) -> NoReturn:
    pass
