from uuid import UUID

from chaosplt_account.storage.model.org import OrgsMembers, Org
from chaosplt_account.storage.model.workspace import Workspace, \
    WorkspacesMembers
from chaosplt_account.storage.model.user import User, UserInfo
from chaosplt_relational_storage.db import orm_session, get_engine, Base
from flask import Flask


__all__ = ["create_orgs", "create_users", "create_workspaces",
           "reset_dataset", "create_user_to_be_deleted"]


def create_orgs(app: Flask):
    with app.app_context():
        with orm_session() as session:
            info = session.query(UserInfo).filter_by(username="myuser").first()
            o = Org.create_personal(
                user=info.user, org_name="myorg", session=session)
            o1 = Org.create(org_name="org1", session=session)
            o2 = Org.create(org_name="org2", session=session)

            OrgsMembers.create(o, info.user, owner=True, session=session)
            OrgsMembers.create(o1, info.user, owner=True, session=session)
            OrgsMembers.create(o2, info.user, owner=False, session=session)

            info = session.query(UserInfo).filter_by(username="user1").first()
            OrgsMembers.create(o1, info.user, owner=False, session=session)
            OrgsMembers.create(o2, info.user, owner=True, session=session)


def create_workspaces(app: Flask):
    with app.app_context():
        with orm_session() as session:
            info = session.query(UserInfo).filter_by(username="myuser").first()
            o = Org.load_by_name("myorg", session=session)
            w = Workspace.create(
                o, "myworkspace", "personal", visibility=None,
                session=session)
            w1 = Workspace.create(
                o, "workspace1", "public", visibility=None, session=session)
            o1 = Org.load_by_name("org1", session=session)
            w2 = Workspace.create(
                o1, "workspace2", "public", visibility=None,
                session=session)

            WorkspacesMembers.create(w, info.user, True, session=session)
            WorkspacesMembers.create(w1, info.user, False, session=session)
            WorkspacesMembers.create(w2, info.user, False, session=session)

            info = session.query(UserInfo).filter_by(username="user1").first()
            WorkspacesMembers.create(w2, info.user, True, session=session)


def create_users(app: Flask):
    with app.app_context():
        with orm_session() as session:
            User.create("myuser", "My User", "myuser@example.com",
                        session=session)
            User.create("user1", "User 1", "u1@example.com", session=session)
            User.create("user2", "User 2", "u2@example.com", session=session)
            User.create("user3", "User 3", "u3@example.com", session=session)
            user = User.create(
                "inactive-user", "User 5", "u5@example.com", session=session)
            user.is_active = False
            User.create(
                "user-no-orgs", "User 6", "u6@example.com", session=session)


def create_user_to_be_deleted(app: Flask) -> UUID:
    with app.app_context():
        with orm_session() as session:
            user = User.create(
                "user-to-delete", "User to be deleted",
                "del@example.com", session=session)

            o = Org.create_personal(user, org_name="temp-org", session=session)
            OrgsMembers.create(o, user, owner=True, session=session)

            o2 = Org.load_by_name("org2", session=session)
            OrgsMembers.create(o2, user, owner=False, session=session)

            w = Workspace.create(
                o, "temp-workspace", "personal", visibility=None,
                session=session)
            WorkspacesMembers.create(w, user, True, session=session)
            session.flush()
            return user.id


def reset_dataset(app: Flask):
    """
    Delete all data from our database
    """
    with app.app_context():
        engine = get_engine({
            "db": {
                "uri": "sqlite:///:memory:"
            }
        })
        meta = Base.metadata
        meta.reflect(bind=engine)
        for table in reversed(meta.sorted_tables):
            engine.execute(table.delete())
