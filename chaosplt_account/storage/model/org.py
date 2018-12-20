# -*- coding: utf-8 -*-
from enum import Enum
from typing import List, NoReturn, Union
import uuid
from uuid import UUID

from chaosplt_relational_storage.db import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, \
    String, func
from sqlalchemy import Enum as EnumType
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from sqlalchemy_utils import UUIDType
from sqlalchemy_utils import JSONType as JSONB

from . import ExperimentVisibility, ExecutionVisibility
from .user import User

__all__ = ["OrgsMembers", "Org", "OrgType"]


class OrgsMembers(Base):  # type: ignore
    __tablename__ = "orgs_members"

    org_id = Column(
        UUIDType(binary=False), ForeignKey('org.id'), primary_key=True)
    user_id = Column(
        UUIDType(binary=False), ForeignKey('user.id'), primary_key=True)
    is_owner = Column(Boolean(name='is_owner'), default=False)
    user = relationship('User')
    organization = relationship('Org')

    @staticmethod
    def create(org: 'Org', user: 'User', owner: bool,
               session: Session) -> 'OrgsMembers':
        assoc = OrgsMembers(
            organization=org,
            user=user,
            is_owner=owner
        )
        session.add(assoc)
        return assoc

    @staticmethod
    def create_from_ids(org_id: Union[UUID, str], user_id: Union[UUID, str],
                        owner: bool, session: Session) -> 'OrgsMembers':
        assoc = OrgsMembers(
            org_id=org_id,
            user_id=user_id,
            is_owner=owner
        )
        session.add(assoc)
        return assoc

    @staticmethod
    def load(org_id: Union[UUID, str], user_id: Union[UUID, str],
             session: Session) -> 'OrgsMembers':
        return session.query(OrgsMembers).\
            filter_by(org_id=org_id).\
            filter_by(user_id=user_id).\
            first()


class OrgType(Enum):
    personal = "personal"
    collaborative = "collaborative"


DEFAULT_ORG_SETTINGS = {  # type: ignore
    "meta": {},
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


class Org(Base):  # type: ignore
    __tablename__ = 'org'

    id = Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    # only set when this is a personal org linked to a single account,
    # otherwise it's not set
    user_id = Column(
        UUIDType(binary=False), ForeignKey('user.id'), nullable=True)
    name = Column(String(), nullable=False, unique=True)
    name_lower = Column(String(), nullable=False, unique=True)
    kind = Column(
        EnumType(OrgType), nullable=False, default=OrgType.personal)
    created_on = Column(DateTime(), server_default=func.now())
    workspaces = relationship(
        'Workspace', backref='org', cascade="all, delete-orphan")
    settings = Column(
        JSONB(), nullable=False, default=DEFAULT_ORG_SETTINGS)

    @staticmethod
    def load_all(session: Session) -> List['Org']:
        return session.query(Org).all()

    @staticmethod
    def load(org_id: Union[UUID, str], session: Session) -> 'Org':
        return session.query(Org).filter_by(id=org_id).first()

    @staticmethod
    def load_by_name(org_name: str, session: Session) -> 'Org':
        name = org_name.lower()
        return session.query(Org).filter_by(name_lower=name).first()

    @staticmethod
    def create_personal(user: User, org_name: str,
                        session: Session) -> 'Org':
        org = Org(
            user=user,
            name=org_name,
            name_lower=org_name.lower()
        )

        session.add(org)
        return org

    @staticmethod
    def create(org_name: str, session: Session) -> 'Org':
        org = Org(
            name=org_name,
            name_lower=org_name.lower(),
            kind=OrgType.collaborative
        )

        session.add(org)
        return org

    @staticmethod
    def delete(org_id: Union[UUID, str], session: Session) -> NoReturn:
        org = session.query(Org).filter_by(id=org_id).first()

        if org:
            session.delete(org)

    def get_workspace_by_name(self, workspace_name: str,
                              session: Session) -> 'Workspace':  # noqa: E0602
        for w in self.workspaces:
            if w.name == workspace_name:
                return w

    def get_workspace_by_id(self, workspace_id: str,
                            session: Session) -> 'Workspace':  # noqa: E0602
        for w in self.workspaces:
            if w.id == workspace_id:
                return w
