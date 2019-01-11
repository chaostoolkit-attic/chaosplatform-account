import logging
from logging import StreamHandler
from typing import Any, Dict, Tuple

from chaosplt_grpc import create_grpc_server, start_grpc_server, \
    stop_grpc_server
from chaosplt_grpc.registration.server import \
    register_registration_service
import cherrypy
from flask import Flask
from flask_caching import Cache
from grpc import Server

from .cache import setup_cache
from .log import http_requests_logger
from .rpc.registration import RegistrationRPC
from .service import initialize_services, shutdown_services, Services
from .storage import AccountStorage, initialize_storage, shutdown_storage
from .views.api import create_api, cleanup_api, serve_api
from .views.web import create_app, cleanup_app, serve_app

__all__ = ["initialize_all", "release_all", "run_forever"]
logger = logging.getLogger("chaosplatform")


def initialize_all(config: Dict[str, Any], web_app: Flask = None,
                   api_app: Flask = None, services: Services = None,
                   grpc_server: Server = None, web_cache: Cache = None,
                   api_cache: Cache = None, web_mount_point: str = "/account",
                   api_mount_point: str = "/api/v1",
                   access_log_handler: StreamHandler = None) \
                   -> Tuple[Flask, Flask, Services, Server, AccountStorage]:
    access_log_handler = access_log_handler or logging.StreamHandler()
    logger.info("Initializing account service resources")

    embedded = True
    if not services:
        embedded = False
        services = Services()

    storage = initialize_storage(config)
    if embedded:
        services.account = storage

    initialize_services(services, config)

    if not web_app:
        web_app = create_app(config)
        web_cache = setup_cache(web_app)
        wsgiapp = http_requests_logger(web_app, access_log_handler)
        cherrypy.tree.graft(wsgiapp, "/account")
    serve_app(
        web_app, web_cache, services, storage, config, web_mount_point,
        log_handler=access_log_handler)

    if not api_app:
        api_app = create_api(config)
        api_cache = setup_cache(api_app)
        wsgiapp = http_requests_logger(api_app, access_log_handler)
        cherrypy.tree.graft(wsgiapp, "/api/v1")
    serve_api(
        api_app, api_cache, services, storage, config, api_mount_point,
        log_handler=access_log_handler)

    if not grpc_server:
        srv_addr = config["GRPC_LISTEN_ADDR"]
        if srv_addr:
            grpc_server = create_grpc_server(srv_addr)
            start_grpc_server(grpc_server)
            logger.info("gRPC server started on {}".format(srv_addr))

        register_registration_service(RegistrationRPC(storage), grpc_server)

    return (web_app, api_app, services, grpc_server, storage)


def release_all(web_app: Flask, api_app: Flask, services: Services,
                grpc_server: Server, storage: AccountStorage):
    logger.info("Releasing account service resources")
    if grpc_server:
        logger.info("gRPC server stopping")
        stop_grpc_server(grpc_server)
        logger.info("gRPC server stopped")
    cleanup_app(web_app)
    cleanup_api(api_app)
    shutdown_services(services)
    shutdown_storage(storage)


def run_forever(config: Dict[str, Any]):
    """
    Run and block until a signal is sent to the process.

    The application, services or gRPC server are all created and initialized
    when the application starts.
    """
    def run_stuff(config: Dict[str, Any]):
        resources = initialize_all(config)
        cherrypy.engine.subscribe(
            'stop', lambda: release_all(*resources),
            priority=20)

    cherrypy.engine.subscribe(
        'start', lambda: run_stuff(config), priority=80)

    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()
