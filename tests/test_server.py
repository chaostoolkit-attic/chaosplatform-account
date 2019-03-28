from typing import Any, Dict
from unittest.mock import MagicMock, patch

from chaosplt_account.service import Services
from chaosplt_account.server import initialize_all, release_all, \
    initialize_grpc
from chaosplt_account.storage import AccountStorage
from chaosplt_grpc import create_grpc_server, start_grpc_server, \
    stop_grpc_server
import grpc


@patch('chaosplt_account.server.create_grpc_server', autospec=True)
def test_initialize_all(create_grpc_server, config: Dict[str, Any],
                        services: Services):
    grpc_server = MagicMock()
    create_grpc_server.return_value = grpc_server

    try:
        web_app, api_app, services, grpc_server, \
            storage = initialize_all(config, services=services)

        assert services.account is not None
    finally:
        release_all(
            web_app, api_app, services, grpc_server, storage)


def test_initialize_and_start_grpc_server(config: Dict[str, Any],
                                          account_storage: AccountStorage):
    try:
        grpc_server = initialize_grpc(config, account_storage, None)
        assert grpc_server is not None
        assert grpc_server._state.stage == grpc._server._ServerStage.STARTED

        assert len(grpc_server._state.generic_handlers) == 1

        handler = grpc_server._state.generic_handlers[0]
        svc_name = 'chaosplatform.registration.RegistrationService'
        assert handler.service_name() == svc_name
    finally:
        stop_grpc_server(grpc_server, timeout=0)


def test_initialize_and_reuse_grpc_server(config: Dict[str, Any],
                                          account_storage: AccountStorage):
    server = create_grpc_server('0.0.0.0', pool_size=1)

    try:
        start_grpc_server(server)
        grpc_server = initialize_grpc(config, account_storage, server)
        assert grpc_server == server
        assert len(grpc_server._state.generic_handlers) == 1

        handler = grpc_server._state.generic_handlers[0]
        svc_name = 'chaosplatform.registration.RegistrationService'
        assert handler.service_name() == svc_name
    finally:
        stop_grpc_server(server, timeout=0)
