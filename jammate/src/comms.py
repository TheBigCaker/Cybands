import zmq
import json
import threading
import time
import logging
from typing import Callable, Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class CommsMode(Enum):
    SERVER = "SERVER"  # Desktop
    CLIENT = "CLIENT"  # Laptop

class ZMQBridge:
    """
    Handles high-speed communication between Desktop (Server) and Laptop (Client).
    Uses REQ/REP for synchronous commands and PUB/SUB for asynchronous state broadcasting.
    """
    def __init__(self, mode: CommsMode, host: str = "127.0.0.1", req_port: int = 5555, pub_port: int = 5556):
        self.mode = mode
        self.host = host
        self.req_port = req_port
        self.pub_port = pub_port
        self.context = zmq.Context()
        self.running = False
        
        # Sockets
        self.req_socket = None  # Client uses REQ, Server uses REP
        self.sub_socket = None  # Client uses SUB, Server uses PUB (actually Server uses PUB to broadcast, Client SUBs)
        self.pub_socket = None  # Server PUBs
        
        # Callbacks
        self.command_handler: Optional[Callable[[Dict], Dict]] = None
        self.state_handler: Optional[Callable[[Dict], None]] = None

        self._thread = threading.Thread(target=self._loop, daemon=True)

    def start(self):
        """Initializes sockets and starts the background listener thread."""
        logger.info(f"Starting ZMQBridge in {self.mode.value} mode")
        
        if self.mode == CommsMode.SERVER:
            # Server Binds
            self.req_socket = self.context.socket(zmq.REP)
            self.req_socket.bind(f"tcp://*:{self.req_port}")
            
            self.pub_socket = self.context.socket(zmq.PUB)
            self.pub_socket.bind(f"tcp://*:{self.pub_port}")
            
        else:
            # Client Connects
            self.req_socket = self.context.socket(zmq.REQ)
            self.req_socket.connect(f"tcp://{self.host}:{self.req_port}")
            
            self.sub_socket = self.context.socket(zmq.SUB)
            self.sub_socket.connect(f"tcp://{self.host}:{self.pub_port}")
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "") # Subscribe to everything

        self.running = True
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self.context.term()

    def send_command(self, command: str, payload: Dict[str, Any] = {}) -> Dict:
        """
        Send a command (Client -> Server). Returns the response.
        Blocking call (standard REQ/REP).
        """
        if self.mode != CommsMode.CLIENT:
            logger.warning("send_command should mostly be used by Client.")
            
        msg = {"type": "COMMAND", "cmd": command, "payload": payload, "ts": time.time()}
        self.req_socket.send_json(msg)
        return self.req_socket.recv_json()

    def broadcast_state(self, state_data: Dict[str, Any]):
        """
        Broadcast state update (Server -> Clients).
        Fire and forget (PUB).
        """
        if self.mode != CommsMode.SERVER:
            logger.warning("broadcast_state should only be used by Server.")
            return

        msg = {"type": "STATE", "payload": state_data, "ts": time.time()}
        self.pub_socket.send_json(msg)

    def _loop(self):
        """Background loop to handle incoming messages."""
        poller = zmq.Poller()
        
        if self.mode == CommsMode.SERVER:
            poller.register(self.req_socket, zmq.POLLIN)
        else:
            poller.register(self.sub_socket, zmq.POLLIN)

        while self.running:
            try:
                socks = dict(poller.poll(100)) # 100ms timeout
                
                # SERVER: Handle Incoming Commands
                if self.req_socket in socks and socks[self.req_socket] == zmq.POLLIN:
                    msg = self.req_socket.recv_json()
                    response = {"status": "ok"}
                    if self.command_handler:
                        try:
                            response = self.command_handler(msg)
                        except Exception as e:
                            logger.error(f"Command handler error: {e}")
                            response = {"status": "error", "message": str(e)}
                    self.req_socket.send_json(response)

                # CLIENT: Handle Incoming State Broadcasts
                if self.sub_socket in socks and socks[self.sub_socket] == zmq.POLLIN:
                    msg = self.sub_socket.recv_json()
                    if self.state_handler:
                        self.state_handler(msg)
                        
            except zmq.ZMQError as e:
                if self.running:
                    logger.error(f"ZMQ Error: {e}")
                break
