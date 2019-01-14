# -*- coding: utf-8 -*-
import cherrypy
import toml

__all__ = ["load_settings"]


def load_settings(toml_path: str):
    """
    Load settings from the environment.
    """
    config = toml.load(toml_path)
    if "chaosplatform" in config:
        config = config["chaosplatform"]

    debug = config.get("debug", False)
    server_addr = config["http"]["address"]
    host, port = server_addr.rsplit(":", 1)
    default_cherrypy_env = "" if debug else "production"

    cherrypy_config = config["http"].get("cherrypy", {})
    cherrypy.engine.unsubscribe('graceful', cherrypy.log.reopen_files)
    cherrypy.config.update({
        'server.socket_host': server_addr,
        'server.socket_port': server_addr,
        'engine.autoreload.on': False,
        'log.screen': debug,
        'log.access_file': cherrypy_config.get("access_file", ""),
        'log.error_file': cherrypy_config.get("error_file", ""),
        'environment': cherrypy_config.get(
            "environment", default_cherrypy_env)
    })

    if "proxy" in config["http"]:
        cherrypy.config.update({
            'tools.proxy.on': True,
            'tools.proxy.base': config["http"]["proxy"]
        })

    return config
