from typing import Any, Dict

from flask import Flask
from flask_marshmallow import Marshmallow
from marshmallow import fields, post_load

from .model import User

__all__ = ["org_schema", "user_schema", "workspace_schema", "new_user_schema",
           "orgs_schema", "ma", "link_org_schema", "link_workspace_schema",
           "new_workspace_schema", "workspaces_schema", "orgs_schema_tiny",
           "org_schema_short", "workspaces_schema_tiny", "my_orgs_schema",
           "workspace_schema_short", "my_workspaces_schema",
           "experiments_schema", "my_experiments_schema", "setup_schemas",
           "my_executions_schema", "my_schedules_schema"]

ma = Marshmallow()


def setup_schemas(app: Flask):
    return ma.init_app(app)


class WorkspaceSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    org_id = fields.UUID(required=True)
    name = fields.String(required=True)
    kind = fields.String(
        data_key="type",
        required=True,
        validate=lambda k: k in ("personal", "protected", "public")
    )
    owner = fields.Boolean(default=False)
    visibility = fields.Dict(
        keys=fields.Str(validate=lambda k: k in ("execution", "experiment")),
        values=fields.Dict(
            keys=fields.String(
                validate=lambda k: k in ("anonymous", "members")
            ),
            values=fields.String(
                validate=lambda v: v in (
                    "private", "protected", "public",
                    "none", "status", "full"
                )
            )
        )
    )
    url = ma.AbsoluteURLFor('workspace.get', workspace_id='<id>')
    links = ma.Hyperlinks({
        'self': ma.URLFor('workspace.get', workspace_id='<id>')
    })


class NewWorkspaceSchema(ma.Schema):
    name = fields.String(required=True)
    org = fields.UUID(required=True)
    kind = fields.String(
        data_key="type",
        missing="collaborative",
        validate=lambda k: k in ("personal", "collaborative")
    )
    visibility = fields.Dict(
        keys=fields.Str(validate=lambda k: k in ("execution", "experiment")),
        values=fields.Dict(
            keys=fields.String(
                validate=lambda k: k in ("anonymous", "members")
            ),
            values=fields.String(
                validate=lambda v: v in (
                    "private", "protected", "public",
                    "none", "status", "full"
                )
            )
        )
    )


class LinkWorkpaceSchema(ma.Schema):
    owner = fields.Boolean(default=False)


class OrganizationSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    name = fields.String(required=True)
    owner = fields.Boolean(default=False)
    kind = fields.String(data_key="type", required=True)
    workspaces = fields.Nested(WorkspaceSchema, many=True)
    url = ma.AbsoluteURLFor('org.get', org_id='<id>')
    links = ma.Hyperlinks({
        'self': ma.URLFor('org.get', org_id='<id>')
    })


class NewOrgSchema(ma.Schema):
    name = fields.String(required=True)


class LinkOrgSchema(ma.Schema):
    owner = fields.Boolean(default=False)


class UserSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=False)
    username = fields.String(required=True)
    orgs = fields.Nested(OrganizationSchema, many=True, dump_only=True)
    workspaces = fields.Nested(WorkspaceSchema, many=True, dump_only=True)
    url = ma.AbsoluteURLFor('user.get', user_id='<id>')
    links = ma.Hyperlinks({
        'self': ma.URLFor('user.get', user_id='<id>'),
    })

    @post_load
    def make_user(self, data: Dict[str, Any]):
        return User(**data)


class NewUserSchema(ma.Schema):
    username = fields.String(required=True)


class ExperimentSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    user_id = fields.UUID(required=True)
    org_id = fields.UUID(required=True)
    workspace_id = fields.UUID(required=True)
    created_date = fields.DateTime()
    updated_date = fields.DateTime()


class ExecutionSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    user_id = fields.UUID(required=True)
    org_id = fields.UUID(required=True)
    workspace_id = fields.UUID(required=True)
    execution_id = fields.UUID(required=True)


class ScheduleSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    user_id = fields.UUID(required=True)
    org_id = fields.UUID(required=True)
    workspace_id = fields.UUID(required=True)
    experiment_id = fields.UUID(required=True)
    token_id = fields.UUID(required=True)
    scheduled = fields.DateTime(required=True)
    status = fields.String(required=True, default="pending")
    job_id = fields.UUID(required=False)


new_user_schema = NewUserSchema()
user_schema = UserSchema()
link_org_schema = LinkOrgSchema()
link_workspace_schema = LinkWorkpaceSchema()

org_schema = OrganizationSchema()
orgs_schema = OrganizationSchema(many=True)
orgs_schema_tiny = OrganizationSchema(
    many=True, exclude=('owner', 'workspaces'))
my_orgs_schema = OrganizationSchema(many=True, exclude=('workspaces', ))
org_schema_short = OrganizationSchema(exclude=('owner',))
new_org_schema = NewOrgSchema()

workspace_schema = WorkspaceSchema()
workspaces_schema = WorkspaceSchema(many=True)
workspaces_schema_tiny = WorkspaceSchema(
    many=True, exclude=('owner',))
workspace_schema_short = WorkspaceSchema(exclude=('owner',))
my_workspaces_schema = WorkspaceSchema(many=True)
new_workspace_schema = NewWorkspaceSchema()

experiments_schema = ExperimentSchema(many=True)
my_experiments_schema = ExperimentSchema(many=True)

my_executions_schema = ExecutionSchema(many=True)

my_schedules_schema = ScheduleSchema(many=True)
