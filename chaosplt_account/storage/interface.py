from abc import ABC, abstractmethod
from uuid import UUID
from typing import Dict, List, NoReturn, Union

import attr
from chaosplt_account.model import User, Organization, Workspace

__all__ = ["BaseAccountStorage"]


class BaseRegistrationService(ABC):
    @abstractmethod
    def get(self, user_id: Union[UUID, str]) -> User:
        raise NotImplementedError()

    @abstractmethod
    def create(self, username: str, name: str, email: str) -> User:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, user_id: Union[UUID, str]) -> NoReturn:
        raise NotImplementedError()


class BaseUserService(ABC):
    @abstractmethod
    def get(self, user_id: Union[UUID, str]) -> User:
        raise NotImplementedError()

    @abstractmethod
    def get_bare(self, user_id: Union[UUID, str]) -> User:
        raise NotImplementedError()

    @abstractmethod
    def create(self, username: str, name: str, email: str) -> User:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, user_id: Union[UUID, str]) -> NoReturn:
        raise NotImplementedError()

    @abstractmethod
    def add_org(self, user_id: Union[UUID, str],
                org_id: Union[UUID, str], owner: bool = False) -> NoReturn:
        raise NotImplementedError()

    @abstractmethod
    def remove_org(self, user_id: Union[UUID, str],
                   org_id: Union[UUID, str]) -> NoReturn:
        raise NotImplementedError()

    @abstractmethod
    def add_workspace(self, user_id: Union[UUID, str],
                      workspace_id: Union[UUID, str],
                      owner: bool = False) -> NoReturn:
        raise NotImplementedError()

    @abstractmethod
    def remove_workspace(self, user_id: Union[UUID, str],
                         workspace_id: Union[UUID, str]) -> NoReturn:
        raise NotImplementedError()


class BaseOrganizationService(ABC):
    @abstractmethod
    def list_all(self) -> List[Organization]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, org_id: Union[UUID, str]) -> Organization:
        raise NotImplementedError()

    @abstractmethod
    def create(self, name: str, user_id: Union[UUID, str]) -> Organization:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, org_id: Union[UUID, str]) -> NoReturn:
        raise NotImplementedError()

    @abstractmethod
    def add_workspace(self, org_id: Union[UUID, str],
                      workspace_id: Union[UUID, str]) -> NoReturn:
        raise NotImplementedError()

    @abstractmethod
    def remove_workspace(self, user_id: Union[UUID, str],
                         org_id: Union[UUID, str]) -> NoReturn:
        raise NotImplementedError()

    @abstractmethod
    def has_org_by_name(self, org_name: str = None) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def has_org_by_id(self, org_id: Union[UUID, str] = None) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def has_workspace_by_name(self, org_id: Union[UUID, str],
                              workspace_name: str = None) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def has_workspace_by_id(self, org_id: Union[UUID, str],
                            workspace_id: Union[UUID, str] = None) -> bool:
        raise NotImplementedError()


class BaseWorkspaceService(ABC):
    @abstractmethod
    def list_all(self) -> List[Workspace]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, workspace_id: Union[UUID, str]) -> Workspace:
        raise NotImplementedError()

    @abstractmethod
    def create(self, name: str, org_id: Union[UUID, str],
               user_id: Union[UUID, str], workspace_type: str,
               visibility: Dict[str, Dict[str, str]]) -> Workspace:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, workspace_id: Union[UUID, str]) -> NoReturn:
        raise NotImplementedError()


@attr.s
class BaseAccountStorage:
    user: BaseUserService = attr.ib()
    org: BaseOrganizationService = attr.ib()
    workspace: BaseWorkspaceService = attr.ib()
    registration: BaseRegistrationService = attr.ib()
