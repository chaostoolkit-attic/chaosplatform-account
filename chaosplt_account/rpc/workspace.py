import logging
from typing import List, NoReturn

from chaosplt_grpc.workspace.message import Collaborator, Workspace
from chaosplt_grpc.workspace.server import WorkspaceRPC as GRPCWorkspaceService

from ..storage import AccountStorage

__all__ = ["WorkspaceRPC"]
logger = logging.getLogger("chaosplatform")


class WorkspaceRPC(GRPCWorkspaceService):
    def __init__(self, storage: AccountStorage):
        GRPCWorkspaceService.__init__(self)
        self.storage = storage

    def create_workspace(self, user_id: str, org_id: str,
                         name: str) -> Workspace:
        workspace = self.storage.workspace.create(name, org_id, user_id, None)
        logger.info("Workspace {} is created".format(workspace.id))

        collaborators = [
            Collaborator(c.user_id, c.user.username, c.is_owner)
            for c in self.storage.workspace.get_collaborators(workspace.id)
        ]
        return Workspace(
            id=str(workspace.id), org_id=org_id, name=name,
            org_name=workspace.org.name, kind=str(workspace.kind),
            created_on=workspace.created_on, settings=workspace.settings,
            collaborators=collaborators)

    def delete_workspace(self, workspace_id: str) -> NoReturn:
        self.storage.workspace.delete(workspace_id)
        logger.info("Workspace {} now deleted".format(workspace_id))

    def get_workspace(self, workspace_id: str) -> Workspace:
        workspace = self.storage.workspace.get_workspace(workspace_id)
        if not workspace:
            return None

        collaborators = [
            Collaborator(c.user_id, c.user.username, c.is_owner)
            for c in self.storage.workspace.get_collaborators(workspace.id)
        ]
        return Workspace(
            id=str(workspace.id), org_id=str(workspace.org_id),
            name=workspace.name, kind=str(workspace.kind),
            created_on=workspace.created_on, org_name=workspace.org.name,
            collaborators=collaborators, settings=workspace.settings)

    def get_workspaces(self, workspace_ids: List[str]) -> List[Workspace]:
        workspaces = self.storage.workspace.get_workspaces(workspace_ids)
        if not workspaces:
            return []

        result = []
        for workspace_id in workspace_ids:
            result.append(self.get_workspace(workspace_id))
        return result

    def get_workspaces_for_user(self, user_id: str) -> List[Workspace]:
        workspaces = self.storage.workspace.get_by_user(user_id)
        if not workspaces:
            return []

        result = []
        for workspace in workspaces:
            collaborators = [
                Collaborator(c.user_id, c.user.username, c.is_owner)
                for c in self.storage.workspace.get_collaborators(workspace.id)
            ]
            result.append(Workspace(
                id=str(workspace.id), org_id=str(workspace.org_id),
                name=workspace.name, kind=str(workspace.kind),
                created_on=workspace.created_on, org_name=workspace.org.name,
                collaborators=collaborators, settings=workspace.settings))
        return result
