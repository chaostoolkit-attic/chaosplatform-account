from datetime import datetime
from typing import Dict, List, Union
from uuid import UUID

import attr

__all__ = ["Organization", "User", "Workspace", "AccessToken"
           "OrganizationMember", "WorkspaceCollaborator"]


@attr.s
class Workspace:
    id: UUID = attr.ib()
    name: str = attr.ib()
    org_id: UUID = attr.ib()
    org_name: str = attr.ib()
    kind: str = attr.ib()
    visibility: Dict[str, str] = attr.ib()
    owner: bool = attr.ib(default=False)
    settings = attr.ib(default=None)


@attr.s
class Organization:
    id: UUID = attr.ib()
    name: str = attr.ib()
    kind: str = attr.ib()
    created_on: datetime = attr.ib()
    owner: bool = attr.ib(default=False)
    workspaces: List[Workspace] = attr.ib(default=None)
    settings = attr.ib(default=None)


@attr.s
class User:
    id: UUID = attr.ib()
    username: str = attr.ib()
    org_name: str = attr.ib()
    is_authenticated: bool = attr.ib()
    is_active: bool = attr.ib()
    is_anonymous: bool = attr.ib()
    fullname: str = attr.ib(default=None)
    email: str = attr.ib(default=None)
    bio: str = attr.ib(default=None)
    company: str = attr.ib(default=None)
    orgs: List[Organization] = attr.ib(default=None)
    workspaces: List[Workspace] = attr.ib(default=None)

    def get_id(self) -> str:
        return str(self.id)

    def get_org(self, org_id: Union[UUID, str]) -> Organization:
        for o in self.orgs:
            if o.id == org_id:
                return o

    def get_workspace(self, workspace_id: Union[UUID, str]) -> Workspace:
        for w in self.workspaces:
            if w.id == workspace_id:
                return w

@attr.s
class OrganizationMember:
    id: UUID = attr.ib()
    username: str = attr.ib()
    org_name: str = attr.ib()
    fullname: str = attr.ib()
    owner: bool = attr.ib(default=False)
    member: bool = attr.ib(default=False)


@attr.s
class WorkspaceCollaborator:
    id: UUID = attr.ib()
    username: str = attr.ib()
    fullname: str = attr.ib()
    owner: bool = attr.ib(default=False)
    collaborator: bool = attr.ib(default=False)
    workspace_name: str = attr.ib()
    workspace_id = UUID = attr.ib()


@attr.s
class AccessToken:
    name: str = attr.ib()
    id: UUID = attr.ib()
    user_id: UUID = attr.ib()
    access_token: str = attr.ib()
    refresh_token: str = attr.ib()
    jti: str = attr.ib()

    def get_id(self) -> str:
        return str(self.id)
