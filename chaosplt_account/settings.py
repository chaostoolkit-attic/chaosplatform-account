# -*- coding: utf-8 -*-
import glob
import os

import cherrypy
from dotenv import load_dotenv

__all__ = ["load_settings"]


def load_settings(env_path: str):
    """
    Load settings from the environment:

    * if `env_path` is a file, read it
    * if `env_path` is a directory, load, all its `*.env` files
    """
    if os.path.isdir(env_path):
        pattern = os.path.join(env_path, '**', '.env')
        for env_file in glob.iglob(pattern, recursive=True):
            cherrypy.log("Loading: {}".format(env_file))
            load_dotenv(dotenv_path=env_file)
    else:
        cherrypy.log("Loading: {}".format(env_path))
        load_dotenv(dotenv_path=env_path)

    debug = True if os.getenv('CHAOSPLATFORM_DEBUG') else False
    cherrypy.config.update({
        'server.socket_host': os.getenv('SERVER_LISTEN_ADDR'),
        'server.socket_port': int(os.getenv('SERVER_LISTEN_PORT', 8080)),
        'engine.autoreload.on': False,
        'log.screen': debug,
        'log.access_file': '',
        'log.error_file': '',
        'environment': '' if debug else 'production',
        'tools.proxy.on': True,
        'tools.proxy.base': os.getenv('CHERRYPY_PROXY_BASE')
    })

    config = {
        'GRPC_LISTEN_ADDR': os.getenv("GRPC_LISTEN_ADDR"),
        'db': {
            'uri': os.getenv("DATABASE_URI"),
            'debug': debug
        },
        'debug': debug,
        'grpc': {
        }
    }

    return config
