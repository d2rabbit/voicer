import asyncio
from loguru import logger
import threading
from typing import Optional
import websockets


class WebSocketServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client: Optional[websockets.WebSocketServerProtocol] = None
        self.logger = logger
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
        self.loop = None
        self.server = None

    async def _handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        if self.client is not None:
            await self.client.close(1000, "New client connected")
            self.logger.info("Closed previous client connection")

        self.client = websocket
        self.logger.info("New client connected")
        try:
            await asyncio.gather(
                self._message_handler(),
                self._process_message_queue()
            )
        finally:
            if self.client == websocket:
                self.client = None
                self.logger.info("Client disconnected")

    async def _message_handler(self):
        while True:
            try:
                message = await self.client.recv()
                self.logger.info(f"Received message: {message}")
                await self.client.send("1")
                self.logger.info(f"Sent message: {message}")
            except websockets.exceptions.ConnectionClosed:
                break

    async def _send_message(self, message: str):
        if self.client and not self.client.closed:
            try:
                await self.client.send(message)
                self.logger.info(f"Sent message: {message}")
            except websockets.exceptions.ConnectionClosed:
                self.logger.warning("Connection closed while sending message")
                self.client = None
        else:
            self.logger.warning("No client connected, message not sent")

    def queue_message(self, message: str):
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(lambda: asyncio.create_task(self.message_queue.put(message)))
        else:
            self.logger.warning("Server not running, message not queued")

    async def _process_message_queue(self):
        while self.is_running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self._send_message(message)
                self.message_queue.task_done()
            except asyncio.TimeoutError:
                continue

    async def _start_server(self):
        self.server = await websockets.serve(self._handle_client, self.host, self.port)
        self.logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
        self.is_running = True
        await self.server.wait_closed()

    def socket_start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._start_server())
        self.loop.run_forever()

    def server_start(self):
        thread = threading.Thread(target=self.socket_start, daemon=True)
        thread.start()
        self.logger.info("Server started in background thread")

    def server_stop(self):
        if self.loop and self.loop.is_running():
            self.is_running = False
            if self.server:
                self.loop.call_soon_threadsafe(self.server.close)
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.logger.info("Server stop requested")
        else:
            self.logger.warning("Server not running")

    def send_command_to_client(self, key):
        self.logger.info(f"发送指令：{key}")
        self.queue_message(key)

    def is_client_connected(self):
        return self.client is not None and not self.client.closed