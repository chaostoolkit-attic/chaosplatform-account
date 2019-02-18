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
           "my_executions_schema", "my_schedules_schema",
           "user_profile_schema", "access_token_schema", "org_name_schema",
           "access_tokens_schema", "new_access_token_schema",
           "created_access_token_schema", "profile_new_org_schema",
           "profile_org_schema", "org_dashboard_schema", "org_settings_schema",
           "org_members_dashboard_schema", "org_info_schema",
           "profile_workspace_schema", "profile_workspaces_schema",
           "profile_new_workspace_schema", "workspace_dashboard_schema",
           "workspace_collaborators_schema"]

ma = Marshmallow()


def setup_schemas(app: Flask):
    return ma.init_app(app)


class WorkspaceSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    org_id = fields.UUID(required=True)
    org_name = fields.String(required=True)
    name = fields.String(required=True)
    kind = fields.String(
        data_key="type",
        required=True,
        validate=lambda k: k in ("personal", "protected", "public")
    )
    owner = fields.Boolean(default=False)
    visibility = fields.Dict(
        keys=fields.Str(validate=lambda k: k in ("execution", "experiment")),
        values=fields.String(
            validate=lambda v: v in (
                "private", "protected", "public",
                "none", "status", "full"
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
        values=fields.String(
            validate=lambda v: v in (
                "private", "protected", "public",
                "none", "status", "full"
            )
        )
    )


class LinkWorkpaceSchema(ma.Schema):
    owner = fields.Boolean(default=False)


class OrgSettingsSchema(ma.Schema):
    description = fields.String(allow_none=True)
    url = fields.URL(allow_none=True)
    logo = fields.URL(allow_none=True)
    email = fields.Email(allow_none=True)


class OrganizationSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    name = fields.String(required=True)
    owner = fields.Boolean(default=False)
    created_on = fields.DateTime()
    kind = fields.String(data_key="type", required=True)
    workspaces = fields.Nested(WorkspaceSchema, many=True)
    url = ma.AbsoluteURLFor('org.get', org_id='<id>')
    links = ma.Hyperlinks({
        'self': ma.URLFor('org.get', org_id='<id>')
    })


class NewOrgSchema(ma.Schema):
    name = fields.String(required=True)
    settings = fields.Nested(OrgSettingsSchema, allow_none=True)
    visibility = fields.Dict(
        keys=fields.Str(validate=lambda k: k in ("execution", "experiment")),
        values=fields.String(
            validate=lambda v: v in (
                "private", "protected", "public",
                "none", "status", "full"
            )
        )
    )


class LinkOrgSchema(ma.Schema):
    owner = fields.Boolean(default=False)


class WorkspaceCollaboratorSchema(ma.Schema):
    id = fields.UUID()
    username = fields.String()
    fullname = fields.String()
    owner = fields.Boolean()
    collaborator = fields.Boolean()
    workspace_id = fields.UUID()
    workspace_name = fields.String()


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


class CurrentOrgSchema(ma.Schema):
    id = fields.UUID(required=True)
    name = fields.String(required=True)
    owner = fields.Boolean(default=False)
    kind = fields.String(data_key="type", required=True)


class CurrentWorkspaceSchema(ma.Schema):
    id = fields.UUID(required=True)
    name = fields.String(required=True)
    owner = fields.Boolean(default=False)
    kind = fields.String(data_key="type", required=True)


class UserProfileSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=False)
    username = fields.String(required=True)
    name = fields.String()
    email = fields.String()
    bio = fields.String()
    company = fields.String()


class AccessTokenSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=False)
    user_id = fields.UUID()
    name = fields.String()
    jti = fields.String()
    access_token = fields.String(load_only=True)
    refresh_token = fields.String(load_only=True)
    revoked = fields.Boolean()
    issued_on = fields.DateTime()
    last_used_on = fields.DateTime()


class CreatedAccessTokenSchema(AccessTokenSchema):
    access_token = fields.String(load_only=False)


class NewAccessTokenSchema(ma.Schema):
    name = fields.String(required=True)
    scopes = fields.String(many=True, default=None, allow_none=True)


class PagingSchema(ma.Schema):
    prev_item = fields.Integer(default=1, data_key="prev")
    next_item = fields.Integer(default=1, data_key="next")


class ProfileWorkspaceSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    org_id = fields.UUID(required=True)
    org_name = fields.String(required=True)
    name = fields.String(required=True)
    owner = fields.Boolean(default=False)
    created_on = fields.DateTime()
    kind = fields.String(data_key="type", required=True)


class ProfileWorkspacesSchema(ma.Schema):
    workspaces = fields.Nested(ProfileWorkspaceSchema, many=True)
    paging = fields.Nested(PagingSchema, default={"prev": 1, "next": 1})


class ProfileOrganizationSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    name = fields.String(required=True)
    owner = fields.Boolean(default=False)
    created_on = fields.DateTime()
    kind = fields.String(data_key="type", required=True)


class ProfileOrganizationsSchema(ma.Schema):
    orgs = fields.Nested(ProfileOrganizationSchema, many=True)
    paging = fields.Nested(PagingSchema, default={"prev": 1, "next": 1})


class OrgNameSchema(ma.Schema):
    name = fields.String(required=True)


class ProfileNewOrganizationSchema(ma.Schema):
    name = fields.String(required=True)
    settings = fields.Nested(OrgSettingsSchema)


class DashboardOrganizationSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    name = fields.String(required=True)
    owner = fields.Boolean(default=False)
    member = fields.Boolean(default=False)
    kind = fields.String(data_key="type", required=True)
    created_on = fields.DateTime()
    workspaces = fields.Nested(WorkspaceSchema, many=True)
    settings = fields.Nested(OrgSettingsSchema, allow_none=True)


class DashboardOrganizationMemberSchema(ma.Schema):
    id = fields.UUID()
    username = fields.String()
    fullname = fields.String()
    owner = fields.Boolean()
    org_name = fields.String()


class DashboardOrganizationMembersSchema(ma.Schema):
    users = fields.Nested(DashboardOrganizationMemberSchema, many=True)
    paging = fields.Nested(PagingSchema, default={"prev": 1, "next": 1})


class WorkspaceInfoSchema(ma.Schema):
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
        values=fields.String(
            validate=lambda v: v in (
                "private", "protected", "public",
                "none", "status", "full"
            )
        )
    )


class OrganizationInfoSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    name = fields.String(required=True)
    owner = fields.Boolean(default=False)
    member = fields.Boolean(default=False)
    kind = fields.String(data_key="type", required=True)
    created_on = fields.DateTime()
    workspaces = fields.Nested(WorkspaceInfoSchema, many=True, default=None)


class ProfileNewWorkspaceSchema(ma.Schema):
    name = fields.String(required=True)
    org_id = fields.UUID(required=True)
    visibility = fields.Dict(
        keys=fields.Str(validate=lambda k: k in ("execution", "experiment")),
        values=fields.String(
            validate=lambda v: v in (
                "private", "protected", "public",
                "none", "status", "full"
            )
        )
    )


class DashboardWorkspaceSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    org_id = fields.UUID(required=True)
    org_name = fields.String(required=True)
    name = fields.String(required=True)
    owner = fields.Boolean(default=False)
    collaborator = fields.Boolean(default=False)
    kind = fields.String(data_key="type", required=True)
    settings = fields.Nested(OrgSettingsSchema, allow_none=True)


class DashboardWorkspaceCollaboratorSchema(ma.Schema):
    id = fields.UUID()
    username = fields.String()
    fullname = fields.String()
    owner = fields.Boolean()
    org_name = fields.String()
    workspace_name = fields.String()


class DashboardWorkspaceCollaboratorsSchema(ma.Schema):
    collaborators = fields.Nested(
        DashboardWorkspaceCollaboratorSchema, many=True)
    paging = fields.Nested(PagingSchema, default={"prev": 1, "next": 1})


class WorkspaceInfoSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.UUID(required=True)
    org_id = fields.UUID(required=True)
    name = fields.String(required=True)
    owner = fields.Boolean(default=False)
    collaborator = fields.Boolean(default=False)
    kind = fields.String(data_key="type", required=True)
    created_on = fields.DateTime()



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


user_profile_schema = UserProfileSchema()

access_token_schema = AccessTokenSchema()
access_tokens_schema = AccessTokenSchema(many=True)
new_access_token_schema = NewAccessTokenSchema()
created_access_token_schema = CreatedAccessTokenSchema()
profile_org_schema = ProfileOrganizationSchema()
profile_orgs_schema = ProfileOrganizationsSchema()
profile_new_org_schema = ProfileNewOrganizationSchema()
org_dashboard_schema = DashboardOrganizationSchema()
org_members_dashboard_schema = DashboardOrganizationMembersSchema()
org_info_schema = OrganizationInfoSchema()
org_settings_schema = OrgSettingsSchema()
org_name_schema = OrgNameSchema()
profile_workspace_schema = ProfileWorkspaceSchema()
profile_workspaces_schema = ProfileWorkspacesSchema()
profile_new_workspace_schema = ProfileNewWorkspaceSchema()
workspace_dashboard_schema = DashboardWorkspaceSchema()
workspace_collaborators_schema = WorkspaceCollaboratorSchema(many=True)
workspace_info_schema = WorkspaceInfoSchema()