from datetime import datetime
from typing import Any, Dict, Union
from uuid import UUID

from chaosplt_grpc import remote_channel
from chaosplt_grpc.activity.client import record_activity
from tzlocal import get_localzone

__all__ = ["ActivityService"]


class ActivityService:
    def __init__(self, config: Dict[str, Any]):
        self.event = EventService(config)

    def release(self):
        pass


class EventService:
    def __init__(self, config: Dict[str, Any]):
        self.addr = config["grpc"]["activity"]["address"]

    def record(self, user_id: Union[UUID, str], event_type: str, phase: str,
               org_id: Union[UUID, str] = None,
               workspace_id: Union[UUID, str] = None,
               experiment_id: Union[UUID, str] = None,
               execution_id: Union[UUID, str] = None,
               authenticated_user_id: Union[UUID, str] = None,
               access_token_id: Union[UUID, str] = None,
               payload: str = None) -> str:
        """
        Record a new activity
        """
        with remote_channel(self.addr) as channel:
            tz = get_localzone()
            ts = datetime.now().astimezone(tz).isoformat()
            activity_id = record_activity(
                channel, authenticated_user_id=str(authenticated_user_id),
                access_token_id=str(access_token_id),
                user_id=str(user_id) if user_id else None,
                org_id=str(org_id) if org_id else None,
                workspace_id=str(workspace_id) if workspace_id else None,
                experiment_id=str(experiment_id) if experiment_id else None,
                execution_id=str(execution_id) if execution_id else None,
                event_type=event_type, phase=phase,
                timestamp=ts, payload=payload)
            return activity_id
