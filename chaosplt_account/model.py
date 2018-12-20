from typing import Dict, List, Union
from uuid import UUID

import attr

__all__ = ["Organization", "User", "Workspace"]


@attr.s
class Workspace:
    id: UUID = attr.ib()
    name: str = attr.ib()
    org_id: UUID = attr.ib()
    kind: str = attr.ib()
    visibility: Dict[str, str] = attr.ib()
    owner: bool = attr.ib(default=False)


@attr.s
class Organization:
    id: UUID = attr.ib()
    name: str = attr.ib()
    kind: str = attr.ib()
    owner: bool = attr.ib(default=False)
    workspaces: List[Workspace] = attr.ib(default=None)


@attr.s
class User:
    id: UUID = attr.ib()
    username: str = attr.ib()
    name: str = attr.ib()
    email: str = attr.ib()
    is_authenticated: bool = attr.ib()
    is_active: bool = attr.ib()
    is_anonymous: bool = attr.ib()
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
