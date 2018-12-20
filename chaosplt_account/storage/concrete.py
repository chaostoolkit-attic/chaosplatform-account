from typing import Dict, List, NoReturn, Union
from uuid import UUID

from chaosplt_account.model import Organization, User, Workspace
from chaosplt_relational_storage import RelationalStorage
from chaosplt_relational_storage.db import orm_session

from .interface import BaseOrganizationService, BaseUserService, \
    BaseRegistrationService, BaseWorkspaceService
from .model import User as UserModel, \
    Org as OrgModel, Workspace as WorkspaceModel, \
    OrgsMembers as OrgsMembersAssociation, \
    WorkspacesMembers as WorkspaceMembersAssociation, WorkspaceType


__all__ = ["UserService", "OrgService", "WorkspaceService",
           "RegistrationService"]


class UserService(BaseUserService):
    def __init__(self, driver: RelationalStorage):
        self.driver = driver

    def get_bare(self, user_id: Union[UUID, str]) -> User:
        with orm_session() as session:
            user = UserModel.load(user_id, session=session)
            if not user:
                return

            return User(
                id=user.id,
                name=user.info.fullname,
                username=user.info.username,
                email=user.info.details.get('email'),
                is_authenticated=user.is_authenticated,
                is_active=user.is_active,
                is_anonymous=user.is_anonymous,
                orgs=[],
                workspaces=[]
            )

    def get(self, user_id: Union[UUID, str]) -> User:
        with orm_session() as session:
            user = UserModel.load(user_id, session=session)
            if not user:
                return

            user_orgs = user.orgs or []
            orgs = []
            for org in user_orgs:
                org_id = org.id
                assoc = OrgsMembersAssociation.load(
                    org_id, user_id, session=session)
                orgs.append(
                    Organization(
                        id=org_id,
                        name=org.name,
                        owner=assoc.is_owner,
                        kind=org.kind.value,
                        workspaces=[]
                    )
                )

            user_workspaces = user.workspaces or []
            workspaces = []
            for workspace in user_workspaces:
                workspace_id = workspace.id
                assoc = WorkspaceMembersAssociation.load(
                    workspace_id, user_id, session=session)
                settings = workspace.settings

                workspaces.append(
                    Workspace(
                        id=workspace_id,
                        org_id=workspace.org_id,
                        name=workspace.name,
                        kind=workspace.kind.value,
                        owner=assoc.is_owner,
                        visibility=settings.get("visibility")
                    )
                )

            if user:
                return User(
                    id=user.id,
                    name=user.info.fullname,
                    username=user.info.username,
                    email=user.info.details.get('email'),
                    is_authenticated=user.is_authenticated,
                    is_active=user.is_active,
                    is_anonymous=user.is_anonymous,
                    orgs=orgs,
                    workspaces=workspaces
                )

    def create(self, username: str, name: str, email: str) -> User:
        with orm_session() as session:
            user = UserModel.create(username, name, email, session=session)
            org = OrgModel.create_personal(user, username, session=session)
            workspace = WorkspaceModel.create(
                user, org, username, WorkspaceType.personal.value, None,
                session=session)
            session.flush()

            settings = workspace.settings

            OrgsMembersAssociation.create(
                org=org, user=user, owner=True, session=session)
            WorkspaceMembersAssociation.create(
                workspace=workspace, user=user, owner=True, session=session)

            return User(
                id=user.id,
                name=user.info.fullname,
                username=user.info.username,
                email=user.info.details.get('email'),
                is_authenticated=user.is_authenticated,
                is_active=user.is_active,
                is_anonymous=user.is_anonymous,
                orgs=[
                    Organization(
                        id=org.id,
                        name=org.name,
                        kind=org.kind.value,
                        owner=True
                    )
                ],
                workspaces=[
                    Workspace(
                        id=workspace.id,
                        org_id=workspace.org_id,
                        name=workspace.name,
                        kind=workspace.kind.value,
                        owner=True,
                        visibility=settings.get("visibility")
                    )
                ]
            )

    def delete(self, user_id: Union[UUID, str]) -> NoReturn:
        with orm_session() as session:
            UserModel.delete(user_id, session=session)

    def add_org(self, user_id: Union[UUID, str],
                org_id: Union[UUID, str], owner: bool = False) -> NoReturn:
        with orm_session() as session:
            OrgsMembersAssociation.create_from_ids(
                org_id=org_id, user_id=user_id, owner=owner, session=session)

    def remove_org(self, user_id: Union[UUID, str],
                   org_id: Union[UUID, str]) -> NoReturn:
        with orm_session() as session:
            user = UserModel.load(user_id, session=session)
            org = OrgModel.load(org_id, session=session)
            if not user.orgs:
                return

            for o in user.orgs:
                if o.id == org.id:
                    user.orgs.remove(o)
                    break

    def add_workspace(self, user_id: Union[UUID, str],
                      workspace_id: Union[UUID, str],
                      owner: bool = False) -> NoReturn:
        with orm_session() as session:
            WorkspaceMembersAssociation.create_from_ids(
                workspace_id=workspace_id, user_id=user_id, owner=owner,
                session=session)

    def remove_workspace(self, user_id: Union[UUID, str],
                         workspace_id: Union[UUID, str]) -> NoReturn:
        with orm_session() as session:
            user = UserModel.load(user_id, session=session)
            workspace = WorkspaceModel.load(workspace_id, session=session)
            if not user.workspaces:
                return

            for w in user.workspaces:
                if w.id == workspace.id:
                    user.workspaces.remove(w)
                    break


class OrgService(BaseOrganizationService):
    def __init__(self, driver: RelationalStorage):
        self.driver = driver

    def list_all(self) -> List[Organization]:
        with orm_session() as session:
            orgs = []
            for org in OrgModel.load_all(session):
                orgs.append(
                    Organization(
                        id=org.id,
                        name=org.name,
                        kind=org.kind.value
                    )
                )
            return orgs

    def get(self, org_id: Union[UUID, str]) -> Organization:
        with orm_session() as session:
            org = OrgModel.load(org_id, session=session)
            if org:
                return Organization(
                    id=org.id,
                    name=org.name,
                    kind=org.kind.value,
                    workspaces=[
                        Workspace(
                            id=workspace.id,
                            org_id=workspace.org_id,
                            name=workspace.name,
                            kind=workspace.kind.value,
                            visibility=workspace.settings.get('visibility')
                        ) for workspace in org.workspaces
                    ]
                )

    def create(self, name: str, user_id: Union[UUID, str]) -> Organization:
        with orm_session() as session:
            user = UserModel.load(user_id, session=session)
            org = OrgModel.create(name, session=session)

            OrgsMembersAssociation.create(
                org=org, user=user, owner=True, session=session)
            session.flush()

            return Organization(
                id=org.id,
                name=org.name,
                kind=org.kind.value,
                workspaces=[]
            )

    def delete(self, org_id: Union[UUID, str]) -> NoReturn:
        with orm_session() as session:
            OrgModel.delete(org_id, session=session)

    def add_workspace(self, org_id: Union[UUID, str],
                      workspace_id: Union[UUID, str],
                      owner: bool = False) -> NoReturn:
        with orm_session() as session:
            WorkspaceMembersAssociation.create_from_ids(
                org_id=org_id, workspace_id=workspace_id, owner=owner,
                session=session)

    def remove_workspace(self, org_id: Union[UUID, str],
                         workspace_id: Union[UUID, str]) -> NoReturn:
        with orm_session() as session:
            org = OrgModel.load(org_id, session=session)
            workspace = WorkspaceModel.load(org_id, session=session)

            for w in org.workspaces:
                if w.id == workspace.id:
                    org.workspaces.remove(workspace)
                    break

    def has_org_by_name(self, org_name: str) -> bool:
        with orm_session() as session:
            org = OrgModel.load_by_name(org_name, session=session)
            return org is not None

    def has_org_by_id(self, org_id: Union[UUID, str]) -> bool:
        with orm_session() as session:
            org = OrgModel.load(org_id, session=session)
            return org is not None

    def has_workspace_by_name(self, org_id: Union[UUID, str],
                              workspace_name: str) -> bool:
        with orm_session() as session:
            org = OrgModel.load(org_id, session=session)
            workspace = org.get_workspace_by_name(
                workspace_name, session=session)
            return workspace is not None

    def has_workspace_by_id(self, org_id: Union[UUID, str],
                            workspace_id: Union[UUID, str]) -> bool:
        with orm_session() as session:
            org = OrgModel.load(org_id, session=session)
            workspace = org.get_workspace_by_id(
                workspace_id, session=session)
            return workspace is not None


class WorkspaceService(BaseWorkspaceService):
    def __init__(self, driver: RelationalStorage):
        self.driver = driver

    def list_all(self) -> List[Workspace]:
        with orm_session() as session:
            workspaces = []
            for workspace in WorkspaceModel.load_all(session):
                settings = workspace.settings

                workspaces.append(
                    Workspace(
                        id=workspace.id,
                        org_id=workspace.org_id,
                        name=workspace.name,
                        kind=workspace.kind.value,
                        visibility=settings.get("visibility", {})
                    )
                )
            return workspaces

    def get(self, workspace_id: Union[UUID, str]) -> Workspace:
        with orm_session() as session:
            workspace = WorkspaceModel.load(workspace_id, session=session)
            if workspace:
                return Workspace(
                    id=workspace.id,
                    name=workspace.name,
                    org_id=workspace.org_id,
                    kind=workspace.kind.value,
                    visibility=workspace.settings.get('visibility')
                )

    def create(self, name: str, org_id: Union[UUID, str],
               user_id: Union[UUID, str], workspace_type: str,
               visibility: Dict[str, str]) -> Workspace:
        with orm_session() as session:
            user = UserModel.load(user_id, session=session)
            org = OrgModel.load(org_id, session=session)
            workspace = WorkspaceModel.create(
                user, org, name, workspace_type, visibility, session=session)
            session.flush()

            settings = workspace.settings

            WorkspaceMembersAssociation.create(
                workspace=workspace, user=user, owner=True, session=session)

            return Workspace(
                id=workspace.id,
                name=workspace.name,
                kind=workspace.kind.value,
                org_id=org.id,
                owner=True,
                visibility=settings.get("visibility", {})
            )

    def delete(self, workspace_id: Union[UUID, str]) -> NoReturn:
        with orm_session() as session:
            WorkspaceModel.delete(workspace_id, session=session)


class RegistrationService(UserService, BaseRegistrationService):
    def __init__(self, driver: RelationalStorage):
        UserService.__init__(self, driver)
