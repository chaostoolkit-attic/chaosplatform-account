from datetime import datetime
from typing import Any, Dict

from chaosplt_grpc import remote_channel
from chaosplt_grpc.activity.client import record_activity
from tzlocal import get_localzone

__all__ = ["ActivityService"]


class ActivityService:
    def __init__(self, config: Dict[str, Any]):
        self.addr = config["grpc"]["activity"]["addr"]

    def release(self):
        pass

    def record(self, event_type: str, phase: str,
               authenticated_user_id: str, user_id: str = None, 
               org_id: str = None, workspace_id: str = None,
               experiment_id: str = None, execution_id: str = None,
               payload: Any = None) -> str:
        """
        Record a new activity
        """
        with remote_channel(self.addr) as channel:
            tz = get_localzone()
            ts = datetime.now().astimezone(tz).isoformat()
            activity_id = record_activity(
                channel,
                user_id=user_id, org_id=org_id, workspace_id=workspace_id,
                experiment_id=experiment_id, execution_id=execution_id,
                event_type=event_type, timestamp=ts, phase=phase,
                authenticated_user_id=authenticated_user_id,
                payload=payload)
            return activity_id
