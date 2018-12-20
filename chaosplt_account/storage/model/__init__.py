# -*- coding: utf-8 -*-
from enum import Enum

__all__ = ["Org", "OrgsMembers", "OrgType", "User", "UserInfo", "UserPrivacy",
           "Workspace", "WorkspacesMembers", "WorkspaceType",
           "ExperimentVisibility", "ExecutionVisibility"]


class ExperimentVisibility(Enum):
    private = "private"
    protected = "protected"
    public = "public"

    @staticmethod
    def is_valid_visibility(experiment_visibility: str):
        return experiment_visibility in (
            ExperimentVisibility.private.value,
            ExperimentVisibility.protected.value,
            ExperimentVisibility.public.value,
        )

    @staticmethod
    def get_visibility(experiment_visibility: str):
        if experiment_visibility == ExperimentVisibility.private.value:
            return ExperimentVisibility.personal

        if experiment_visibility == ExperimentVisibility.protected.value:
            return ExperimentVisibility.protected

        if experiment_visibility == ExperimentVisibility.public.value:
            return ExperimentVisibility.public


class ExecutionVisibility(Enum):
    none = "none"
    status = "status"
    full = "full"

    @staticmethod
    def is_valid_visibility(execution_visibility: str):
        return execution_visibility in (
            ExecutionVisibility.none.value,
            ExecutionVisibility.status.value,
            ExecutionVisibility.full.value,
        )

    @staticmethod
    def get_visibility(execution_visibility: str):
        if execution_visibility == ExecutionVisibility.none.value:
            return ExecutionVisibility.none

        if execution_visibility == ExecutionVisibility.status.value:
            return ExecutionVisibility.status

        if execution_visibility == ExecutionVisibility.full.value:
            return ExecutionVisibility.full


from .org import Org, OrgsMembers, OrgType  # noqa: E402
from .user import User, UserInfo, UserPrivacy  # noqa: E402
from .workspace import Workspace, WorkspacesMembers, WorkspaceType  # noqa: E402
