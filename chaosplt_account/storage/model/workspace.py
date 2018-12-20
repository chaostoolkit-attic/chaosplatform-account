# -*- coding: utf-8 -*-
from enum import Enum
from typing import Dict, List, NoReturn, Union
import uuid
from uuid import UUID

from chaosplt_relational_storage.db import Base
from sqlalchemy import Boolean, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as EnumType
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from sqlalchemy_utils import UUIDType
from sqlalchemy_utils import JSONType as JSONB

from . import ExperimentVisibility, ExecutionVisibility
from .org import Org
from .user import User

__all__ = ["Workspace", "WorkspacesMembers", "WorkspaceType"]


class WorkspacesMembers(Base):  # type: ignore
    __tablename__ = "workspaces_members"

    workspace_id = Column(
        UUIDType(binary=False), ForeignKey('workspace.id'), primary_key=True)
    user_id = Column(
        UUIDType(binary=False), ForeignKey('user.id'), primary_key=True)
    is_owner = Column(Boolean(name='is_owner'), default=False)
    account = relationship('User')
    workspace = relationship('Workspace')

    @staticmethod
    def create(workspace: 'Workspace', user: 'User', owner: bool,
               session: Session) -> 'WorkspacesMembers':
        assoc = WorkspacesMembers(
            workspace=workspace,
            account=user,
            is_owner=owner
        )
        session.add(assoc)
        return assoc

    @staticmethod
    def create_from_ids(workspace_id: Union[UUID, str],
                        user_id: Union[UUID, str], owner: bool,
                        session: Session) -> 'WorkspacesMembers':
        assoc = WorkspacesMembers(
            workspace_id=workspace_id,
            user_id=user_id,
            is_owner=owner
        )
        session.add(assoc)
        return assoc

    @staticmethod
    def load(workspace_id: Union[UUID, str], user_id: Union[UUID, str],
             session: Session) -> 'WorkspacesMembers':
        return session.query(WorkspacesMembers).\
            filter_by(workspace_id=workspace_id).\
            filter_by(user_id=user_id).\
            first()


class WorkspaceType(Enum):
    personal = "personal"
    protected = "protected"
    public = "public"

    @staticmethod
    def is_valid_type(workspace_type: str):
        return workspace_type in (
            WorkspaceType.personal.value,
            WorkspaceType.protected.value,
            WorkspaceType.public.value,
        )

    @staticmethod
    def get_type(workspace_type: str):
        if workspace_type == WorkspaceType.personal.value:
            return WorkspaceType.personal

        if workspace_type == WorkspaceType.protected.value:
            return WorkspaceType.protected

        if workspace_type == WorkspaceType.public.value:
            return WorkspaceType.public


DEFAULT_WORKSPACE_SETTINGS = {
    "visibility": {
        "execution": {
            "anonymous": ExecutionVisibility.none.value,
            "members": ExecutionVisibility.full.value
        },
        "experiment": {
            "anonymous": ExperimentVisibility.public.value,
            "members": ExperimentVisibility.public.value,
        }
    }
}


class Workspace(Base):  # type: ignore
    __tablename__ = "workspace"
    __table_args__ = (
        UniqueConstraint(
            'name', 'org_id'
        ),
    )

    id = Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = Column(String(), nullable=False)
    name_lower = Column(String(), nullable=False)
    kind = Column(
        EnumType(WorkspaceType), nullable=False,
        default=WorkspaceType.personal)
    org_id = Column(
        UUIDType(binary=False), ForeignKey('org.id'), nullable=False)
    settings = Column(
        JSONB(), nullable=False, default=DEFAULT_WORKSPACE_SETTINGS)

    @staticmethod
    def load_all(session: Session) -> List['Workspace']:
        return session.query(Workspace).all()

    @staticmethod
    def load(workspace_id: Union[UUID, str], session: Session) -> 'Org':
        return session.query(Workspace).filter_by(id=workspace_id).first()

    @staticmethod
    def create(user: User, org: Org, workspace_name: str, workspace_type: str,
               visibility: Dict[str, Dict[str, str]],
               session: Session) -> 'Workspace':

        visibility = visibility or \
            DEFAULT_WORKSPACE_SETTINGS["visibility"].copy()
        workspace = Workspace(
            org=org,
            name=workspace_name,
            name_lower=workspace_name.lower(),
            kind=WorkspaceType.get_type(workspace_type),
            settings={
                "visibility": visibility
            }
        )

        session.add(workspace)
        return workspace

    @staticmethod
    def delete(workspace_id: Union[UUID, str], session: Session) -> NoReturn:
        workspace = session.query(Workspace).filter_by(id=workspace_id).first()

        if workspace:
            session.delete(workspace)
