import click
import os

from . import __version__
from .log import configure_logger
from .server import run_forever
from .settings import load_settings


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


@cli.command()
@click.option('--env-path',
              type=click.Path(exists=True, readable=True, resolve_path=True),
              help='Dot env file or directory path.')
@click.option('--verbose', is_flag=True, help='Enable more traces.')
@click.option('--logger-config',
              type=click.Path(exists=False, readable=True, resolve_path=True),
              help='Python logger JSON definition.')
def run(env_path: str = None, verbose: bool = False,
        logger_config: str = None):
    """
    Runs the application.
    """
    if verbose:
        os.environ["CHAOSPLATFORM_DEBUG"] = "1"
    config = load_settings(env_path)
    configure_logger(logger_config, config)
    run_forever(config)
