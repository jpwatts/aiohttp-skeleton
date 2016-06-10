#!/usr/bin/env python

import asyncio
import logging
import uuid

from aiohttp import web

from .events import CommentEvent, RetryEvent


logger = logging.getLogger(__name__)


class Client:
    """A connected client"""
    def __init__(self, server, request):
        self.server = server
        self.request = request
        self.client_id = uuid.uuid4().hex
        self.ip_address = request.transport.get_extra_info('peername')[0]
        self.queue = None

    async def __aenter__(self):
        client_id = self.client_id
        logger.info("OPEN %s %s", self.ip_address, client_id)
        server = self.server
        self.queue = asyncio.Queue(loop=server.loop)
        server.clients[client_id] = self
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        server = self.server
        client_id = self.client_id
        del server.clients[client_id]
        self.queue = None
        logger.info("CLOSE %s %s", self.ip_address, client_id)


class Server:
    """An event source server"""

    def __init__(self, address, port, *, loop=None, timeout=30):
        self.address = address
        self.port = port
        self.loop = loop
        self.timeout = timeout
        self.clients = {}
        self._server = None

    async def publish_event(self, event):
        """Add an event to the queue of each connected client."""
        for client in self.clients.values():
            await client.queue.put(event)

    async def stream_events(self, request):
        """Respond to a request to stream events."""
        response = web.StreamResponse()
        response.content_type = "text/event-stream"
        response.headers.update({
            'Access-Control-Allow-Credentials': "true",
            'Access-Control-Allow-Headers': "Content-Type",
            'Access-Control-Allow-Methods': "GET",
            'Access-Control-Allow-Origin': request.headers.get('Origin', "*")
        })

        async with Client(self, request) as client:
            client_id = client.client_id
            queue = client.queue
            timeout = self.timeout

            response.headers['client-id'] = client_id
            await response.prepare(request)

            CommentEvent("Howdy {}!".format(client_id)).dump(response)
            RetryEvent(10).dump(response)

            await response.drain()

            while True:
                try:
                    event = await asyncio.wait_for(
                        queue.get(),
                        timeout
                    )
                except asyncio.TimeoutError:
                    # Send something so the connection doesn't time out.
                    event = CommentEvent()
                event.dump(response)
                await response.drain()

        await response.write_eof()
        return response

    async def start(self):
        """Start the server."""
        assert self._server is None
        loop = self.loop
        app = web.Application(loop=loop)
        app.router.add_route("GET", '/events', self.stream_events)
        self._server = await loop.create_server(
            app.make_handler(access_log=logger.getChild("access")),
            self.address,
            self.port
        )

    async def stop(self):
        """Stop the server."""
        server = self._server
        assert server is not None
        server.close()
        await server.wait_closed()
        self._server = None
