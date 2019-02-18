from abc import ABC, abstractmethod
from uuid import UUID
from typing import Dict, List, NoReturn, Union

import attr
from chaosplt_account.model import User, Organization, Workspace, \
    OrganizationMember, WorkspaceCollaborator

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
    def get_by_user(self, user_id: Union[UUID, str]) -> List[Organization]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, org_id: Union[UUID, str]) -> Organization:
        raise NotImplementedError()

    @abstractmethod
    def get_by_name(self, org_name: str) -> Organization:
        raise NotImplementedError()

    @abstractmethod
    def get_members(self, org_id: Union[UUID, str]) \
        -> List[OrganizationMember]:
        raise NotImplementedError()

    @abstractmethod
    def create(self, name: str, user_id: Union[UUID, str]) -> Organization:
        raise NotImplementedError()

    @abstractmethod
    def save(self, org: Organization) -> NoReturn:
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

    @abstractmethod
    def is_member(self, org_id: Union[UUID, str],
                  user_id: Union[str, UUID]) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def is_owner(self, org_id: Union[UUID, str],
                 user_id: Union[str, UUID]) -> bool:
        raise NotImplementedError()


class BaseWorkspaceService(ABC):
    @abstractmethod
    def list_all(self) -> List[Workspace]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, workspace_id: Union[UUID, str]) -> Workspace:
        raise NotImplementedError()

    @abstractmethod
    def get_by_name(self, org_id: Union[UUID, str],
                    workspace_name: str) -> Workspace:
        raise NotImplementedError()

    @abstractmethod
    def get_by_user(self, user_id: Union[UUID, str]) -> List[Workspace]:
        raise NotImplementedError()

    @abstractmethod
    def create(self, name: str, org_id: Union[UUID, str],
               user_id: Union[UUID, str],
               visibility: Dict[str, Dict[str, str]]) -> Workspace:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, workspace_id: Union[UUID, str]) -> NoReturn:
        raise NotImplementedError()

    @abstractmethod
    def get_collaborators(self, workspace_id: Union[UUID, str]) \
        -> List[WorkspaceCollaborator]:
        raise NotImplementedError()

    @abstractmethod
    def is_collaborator(self, workspace_id: Union[UUID, str],
                        user_id: Union[str, UUID]) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def is_owner(self, workspace_id: Union[UUID, str],
                 user_id: Union[str, UUID]) -> bool:
        raise NotImplementedError()


@attr.s
class BaseAccountStorage:
    user: BaseUserService = attr.ib()
    org: BaseOrganizationService = attr.ib()
    workspace: BaseWorkspaceService = attr.ib()
    registration: BaseRegistrationService = attr.ib()
