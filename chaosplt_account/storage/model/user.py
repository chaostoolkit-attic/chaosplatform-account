# -*- coding: utf-8 -*-
from typing import NoReturn, Union
import uuid
from uuid import UUID

from chaosplt_relational_storage.db import Base, get_secret_key
from flask_login import UserMixin
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, \
    String, func
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.session import Session
from sqlalchemy_utils import EncryptedType, UUIDType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from sqlalchemy_utils import JSONType as JSONB

__all__ = ["User", "UserInfo", "UserPrivacy"]


class User(Base, UserMixin):  # type: ignore
    __tablename__ = 'user'

    id = Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    joined_dt = Column(DateTime(), server_default=func.now())
    closed_dt = Column(DateTime())
    inactive_dt = Column(DateTime())
    is_closed = Column(Boolean(name='is_closed'), default=False)
    is_active = Column(Boolean(name='is_active'), default=True)
    is_authenticated = Column(Boolean(name="is_authenticated"), default=False)
    is_anonymous = Column(Boolean(name="is_anonymous"), default=False)

    info = relationship(
        'UserInfo', backref='user', uselist=False,
        cascade="all, delete-orphan")
    privacy = relationship(
        'UserPrivacy', backref='user', uselist=False,
        cascade="all, delete-orphan")
    workspaces = relationship(
        'Workspace', secondary="workspaces_members",
        lazy='subquery', backref=backref(
            'users', lazy=True, passive_updates=False))
    orgs = relationship(
        'Org', secondary="orgs_members", lazy='subquery',
        backref=backref('users', lazy=True, passive_updates=False))
    # direct access to the unique personal org
    # but this org is also part of the many to many relationship
    personal_org = relationship(
        'Org', backref='user', uselist=False, cascade="all, delete-orphan")

    @staticmethod
    def load(user_id: Union[UUID, str], session: Session) -> 'User':
        return session.query(User).filter_by(id=user_id).first()

    @staticmethod
    def create(username: str, name: str, email: str,
               session: Session) -> 'User':
        info = UserInfo(
            username=username,
            fullname=name,
            details={
                "email": email
            })
        privacy = UserPrivacy()
        user = User(
            info=info,
            privacy=privacy,
            is_active=True,
            is_authenticated=True
        )

        session.add(info)
        session.add(privacy)
        session.add(user)
        return user

    @staticmethod
    def delete(user_id: Union[UUID, str], session: Session) -> NoReturn:
        user = session.query(User).filter_by(id=user_id).first()

        if user:
            session.delete(user)


class UserInfo(Base):  # type: ignore
    __tablename__ = 'user_info'

    id = Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUIDType(binary=False), ForeignKey('user.id'),
        nullable=False)
    last_updated = Column(
        DateTime(), server_default=func.now(),
        onupdate=func.current_timestamp())
    verified_email = Column(Boolean(name='verified_email'), default=False)

    # values for search purpose mostly
    username = Column(String, index=True, nullable=True)
    fullname = Column(String, index=True, nullable=True)

    details = Column(
        EncryptedType(
            JSONB, get_secret_key, AesEngine, 'pkcs5'))


class UserPrivacy(Base):  # type: ignore
    __tablename__ = 'user_privacy'

    id = Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUIDType(binary=False), ForeignKey('user.id'),
        nullable=False)
    last_changed = Column(DateTime(), server_default=func.now())
    details = Column(JSONB())
