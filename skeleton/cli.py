import asyncio
import logging

import click

from .server import Server


@click.group()
def main():
    pass


@main.command()
@click.option('--logging', '-l', default="INFO", envvar="SKELETON_SERVER_LOGGING", help="Log level", show_default=True)
@click.option('--debug', '-d', envvar="SKELETON_SERVER_DEBUG", is_flag=True, help="Enable debugging", show_default=True)
@click.option('--address', '-a', default="127.0.0.1", envvar="SKELETON_SERVER_ADDRESS", help="Server address", show_default=True)
@click.option('--port', '-p', default=8000, envvar="SKELETON_SERVER_PORT", help="Server port", show_default=True)
def server(**options):
    logging.basicConfig(level=getattr(logging, options['logging'].upper()))
    loop = asyncio.get_event_loop()
    loop.set_debug(options['debug'])

    server = Server(options['address'], options['port'], loop=loop)
    loop.run_until_complete(server.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    finally:
        loop.close()
