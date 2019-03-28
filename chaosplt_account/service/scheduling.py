from typing import Any, Dict, List

from chaosplt_grpc import remote_channel
from chaosplt_grpc.scheduling.client import get_by_user, \
    get_by_workspace, get_by_org

from ..model import Schedule

__all__ = ["SchedulingService"]


class SchedulingService:
    def __init__(self, config: Dict[str, Any]):
        self.addr = config["grpc"]["scheduling"]["addr"]

    def release(self):
        pass

    def get_by_user(self, user_id: str) -> List[Schedule]:
        with remote_channel(self.addr) as channel:
            schedules = get_by_user(
                channel, user_id, with_payload=False)
            result = []
            for schedule in schedules:
                result.append(
                    Schedule(
                        id=schedule.id,
                        user_id=schedule.user_id,
                        org_id=schedule.org_id,
                        workspace_id=schedule.workspace_id,
                        token_id=schedule.token_id,
                        scheduled=schedule.scheduled,
                        job_id=schedule.job_id,
                        repeat=schedule.repeat,
                        interval=schedule.interval,
                        cron=schedule.cron,
                        settings=schedule.settings,
                        configuration=schedule.configuration,
                        secrets=schedule.secrets,
                        results=schedule.results))

            return result

    def get_by_org(self, org_id: str) -> List[Schedule]:
        with remote_channel(self.addr) as channel:
            schedules = get_by_org(
                channel, org_id, with_payload=False)
            result = []
            for schedule in schedules:
                result.append(
                    Schedule(
                        id=schedule.id,
                        user_id=schedule.user_id,
                        org_id=schedule.org_id,
                        workspace_id=schedule.workspace_id,
                        token_id=schedule.token_id,
                        scheduled=schedule.scheduled,
                        job_id=schedule.job_id,
                        repeat=schedule.repeat,
                        interval=schedule.interval,
                        cron=schedule.cron,
                        settings=schedule.settings,
                        configuration=schedule.configuration,
                        secrets=schedule.secrets,
                        results=schedule.results))

            return result

    def get_by_workspace(self, workspace_id: str) -> List[Schedule]:
        with remote_channel(self.addr) as channel:
            schedules = get_by_workspace(
                channel, workspace_id, with_payload=False)
            result = []
            for schedule in schedules:
                result.append(
                    Schedule(
                        id=schedule.id,
                        user_id=schedule.user_id,
                        org_id=schedule.org_id,
                        workspace_id=schedule.workspace_id,
                        token_id=schedule.token_id,
                        scheduled=schedule.scheduled,
                        job_id=schedule.job_id,
                        repeat=schedule.repeat,
                        interval=schedule.interval,
                        cron=schedule.cron,
                        settings=schedule.settings,
                        configuration=schedule.configuration,
                        secrets=schedule.secrets,
                        results=schedule.results))

            return result
