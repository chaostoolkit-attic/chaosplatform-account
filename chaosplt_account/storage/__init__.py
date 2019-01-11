from typing import Any, Dict, NoReturn

from chaosplt_relational_storage import get_storage, \
    configure_storage, release_storage
import pkg_resources

from .concrete import OrgService, RegistrationService, UserService, \
    WorkspaceService
from .interface import BaseAccountStorage

__all__ = ["initialize_storage", "shutdown_services", "AccountStorage"]


class AccountStorage(BaseAccountStorage):
    def __init__(self, config: Dict[str, Any]):
        self.driver = get_storage(config)
        configure_storage(self.driver)

        user = UserService(self.driver)
        org = OrgService(self.driver)
        workspace = WorkspaceService(self.driver)
        registration = RegistrationService(self.driver)

        BaseAccountStorage.__init__(
            self, user, org, workspace, registration)

    def release(self) -> NoReturn:
        release_storage(self.driver)


def initialize_storage(config: Dict[str, Any]) -> BaseAccountStorage:
    for plugin in pkg_resources.iter_entry_points('chaosplatform.storage'):
        if plugin.name == "account":
            service_class = plugin.load()
            return service_class(config)

    return AccountStorage(config)


def shutdown_storage(storage: BaseAccountStorage) -> NoReturn:
    storage.release()
