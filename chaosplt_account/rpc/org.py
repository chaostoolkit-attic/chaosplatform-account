import logging
from typing import List, NoReturn

from chaosplt_grpc.organization.message import Member, Organization
from chaosplt_grpc.organization.server import \
    OrganizationRPC as GRPCOrganizationService

from ..storage import AccountStorage

__all__ = ["OrganizationRPC"]
logger = logging.getLogger("chaosplatform")


class OrganizationRPC(GRPCOrganizationService):
    def __init__(self, storage: AccountStorage):
        GRPCOrganizationService.__init__(self)
        self.storage = storage

    def create_organization(self, user_id: str, name: str) -> Organization:
        org = self.storage.org.create(name, user_id)
        logger.info("Organization {} is created".format(org.id))

        members = [
            Member(c.user_id, c.user.username, c.is_owner)
            for c in self.storage.org.get_collaborators(org.id)
        ]
        return Organization(
            id=str(org.id), name=name, kind=str(org.kind),
            created_on=org.created_on, settings=org.settings,
            members=members)

    def delete_organization(self, organization_id: str) -> NoReturn:
        self.storage.org.delete(organization_id)
        logger.info("Organization {} now deleted".format(organization_id))

    def get_organization(self, organization_id: str) -> Organization:
        org = self.storage.org.get_organization(organization_id)
        if not org:
            return None

        members = [
            Member(m.user_id, m.user.username, m.is_owner)
            for m in self.storage.organization.get_members(org.id)
        ]
        return Organization(
            id=str(org.id), name=org.name, kind=str(org.kind),
            created_on=org.created_on, members=members, settings=org.settings)

    def get_organizations(self, organization_ids: List[str]) \
            -> List[Organization]:
        Organizations = self.storage.org.get_organizations(organization_ids)
        if not Organizations:
            return []

        result = []
        for organization_id in organization_ids:
            result.append(self.get_Organization(organization_id))
        return result

    def get_organizations_for_user(self, user_id: str) -> List[Organization]:
        orgs = self.storage.Organization.get_by_user(user_id)
        if not orgs:
            return []

        result = []
        for org in orgs:
            members = [
                Member(c.user_id, c.user.username, c.is_owner)
                for c in self.storage.org.get_collaborators(org.id)
            ]
            result.append(Organization(
                id=str(org.id), name=org.name, kind=str(org.kind),
                created_on=org.created_on, members=members,
                settings=org.settings))
        return result
