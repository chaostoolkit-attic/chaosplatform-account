from unittest.mock import MagicMock, patch
from uuid import uuid4

from chaosplt_account.rpc.activity import ActivityService


@patch("chaosplt_account.rpc.activity.remote_channel", autospec=True)
def test_record_activity_with_no_context(remote_channel):
    channel = MagicMock()
    remote_channel.__enter__ = MagicMock(return_value=channel)

    svc = ActivityService({
        "grpc": {
            "activity": {
                "addr": "localhost:50051"
            }
        }
    })
    activity_id = svc.record(
        "test", "run", authenticated_user_id=str(uuid4())
    )
    assert activity_id is not None


@patch("chaosplt_account.rpc.activity.remote_channel", autospec=True)
def test_record_activity_with_user_id(remote_channel):
    channel = MagicMock()
    remote_channel.__enter__ = MagicMock(return_value=channel)

    svc = ActivityService({
        "grpc": {
            "activity": {
                "addr": "localhost:50051"
            }
        }
    })
    activity_id = svc.record(
        "test", "run", authenticated_user_id=str(uuid4()), user_id=str(uuid4())
    )
    assert activity_id is not None
