from datetime import datetime
from typing import Any, Dict, List, Union
from uuid import UUID

import attr

__all__ = ["Organization", "User", "Workspace", "AccessToken",
           "OrganizationMember", "WorkspaceCollaborator", "anonymous_user",
           "Experiment", "Execution", "Schedule"]


@attr.s
class WorkspaceCollaborator:
    id: UUID = attr.ib()
    username: str = attr.ib()
    fullname: str = attr.ib()
    workspace_name: str = attr.ib()
    workspace_id: UUID = attr.ib()
    owner: bool = attr.ib(default=False)
    collaborator: bool = attr.ib(default=False)


@attr.s
class Workspace:
    id: UUID = attr.ib()
    name: str = attr.ib()
    org_id: UUID = attr.ib()
    org_name: str = attr.ib()
    kind: str = attr.ib()
    created_on: datetime = attr.ib()
    visibility: Dict[str, str] = attr.ib()
    owner: bool = attr.ib(default=False)
    member: bool = attr.ib(default=False)
    collaborators: List[WorkspaceCollaborator] = attr.ib(default=None)
    settings = attr.ib(default=None)


@attr.s
class OrganizationMember:
    id: UUID = attr.ib()
    username: str = attr.ib()
    fullname: str = attr.ib()
    org_name: str = attr.ib()
    org_id: UUID = attr.ib()
    owner: bool = attr.ib(default=False)
    member: bool = attr.ib(default=False)
    settings = attr.ib(default=None)


@attr.s
class Organization:
    id: UUID = attr.ib()
    name: str = attr.ib()
    kind: str = attr.ib()
    created_on: datetime = attr.ib()
    owner: bool = attr.ib(default=False)
    member: bool = attr.ib(default=False)
    workspaces: List[Workspace] = attr.ib(default=None)
    members: List[OrganizationMember] = attr.ib(default=None)
    settings = attr.ib(default=None)


@attr.s
class User:
    id: UUID = attr.ib()
    username: str = attr.ib()
    org_name: str = attr.ib()
    is_authenticated: bool = attr.ib()
    is_active: bool = attr.ib()
    is_anonymous: bool = attr.ib()
    is_local: bool = attr.ib(default=False)
    is_closed: bool = attr.ib(default=False)
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


anonymous_user = User(
    id=None, username=None, org_name=None, is_authenticated=False,
    is_active=False, is_anonymous=True
)


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


@attr.s
class Execution:
    id: UUID = attr.ib()
    user_id: UUID = attr.ib()
    org_id: UUID = attr.ib()
    org_name: str = attr.ib()
    workspace_id: UUID = attr.ib()
    workspace_name: str = attr.ib()
    experiment_id: UUID = attr.ib()
    payload: Dict[str, Any] = attr.ib(default=None)


@attr.s
class Experiment:
    id: UUID = attr.ib()
    user_id: UUID = attr.ib()
    username: str = attr.ib()
    user_org_name: str = attr.ib()
    org_id: UUID = attr.ib()
    org_name: str = attr.ib()
    workspace_id: UUID = attr.ib()
    workspace_name: str = attr.ib()
    created_date: datetime = attr.ib()
    updated_date: datetime = attr.ib()
    payload: Dict[str, Any] = attr.ib(default=None)
    executions: List[Execution] = attr.ib(default=None)


@attr.s
class Schedule:
    id: UUID = attr.ib()
    user_id: UUID = attr.ib()
    username: str = attr.ib()
    user_org_name: str = attr.ib()
    org_id: UUID = attr.ib()
    org_name: str = attr.ib()
    workspace_id: UUID = attr.ib()
    workspace_name: str = attr.ib()
    experiment_id: UUID = attr.ib()
    experiment_name: str = attr.ib()
    token_id: UUID = attr.ib()
    created_on: datetime = attr.ib()
    active_from: datetime = attr.ib()
    active_until: datetime = attr.ib()
    status: str = attr.ib()
    job_id: UUID = attr.ib(default=None)
    repeat: int = attr.ib(default=None)
    interval: int = attr.ib(default=None)
    cron: str = attr.ib(default=None)
    plan: List[datetime] = attr.ib(default=None)
    settings: Dict[str, Any] = attr.ib(default=None)
    configuration: Dict[str, Any] = attr.ib(default=None)
    secrets: Dict[str, Any] = attr.ib(default=None)
