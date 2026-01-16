"""WebSocket connection manager."""
import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Optional

from fastapi import WebSocket


@dataclass
class Connection:
    """Een actieve WebSocket connectie."""
    websocket: WebSocket
    client_id: str
    connected_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    conversation_id: str = "default"


class ConnectionManager:
    """
    Beheert WebSocket connecties.

    Features:
    - Multiple client support
    - Heartbeat tracking
    - Broadcast naar specifieke clients
    """

    def __init__(self, heartbeat_timeout: int = 60):
        self._connections: dict[str, Connection] = {}
        self.heartbeat_timeout = heartbeat_timeout
        self._lock = asyncio.Lock()

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        conversation_id: str = "default"
    ) -> Connection:
        """
        Accept en registreer nieuwe connectie.

        Args:
            websocket: FastAPI WebSocket instance
            client_id: Unieke client identifier
            conversation_id: Conversation ID voor deze client

        Returns:
            Connection object
        """
        await websocket.accept()

        connection = Connection(
            websocket=websocket,
            client_id=client_id,
            conversation_id=conversation_id
        )

        async with self._lock:
            self._connections[client_id] = connection

        return connection

    async def disconnect(self, client_id: str) -> None:
        """Verwijder connectie."""
        async with self._lock:
            if client_id in self._connections:
                del self._connections[client_id]

    def get_connection(self, client_id: str) -> Optional[Connection]:
        """Haal connectie op bij ID."""
        return self._connections.get(client_id)

    def get_connections_for_conversation(self, conversation_id: str) -> list[Connection]:
        """Haal alle connecties voor een conversation."""
        return [
            conn for conn in self._connections.values()
            if conn.conversation_id == conversation_id
        ]

    async def send_json(self, client_id: str, data: dict) -> bool:
        """
        Stuur JSON naar specifieke client.

        Returns:
            True als verzonden, False als client niet gevonden
        """
        connection = self.get_connection(client_id)
        if connection is None:
            return False

        try:
            await connection.websocket.send_json(data)
            return True
        except Exception:
            await self.disconnect(client_id)
            return False

    async def send_to_conversation(self, conversation_id: str, data: dict) -> int:
        """
        Stuur JSON naar alle clients in een conversation.

        Returns:
            Aantal clients dat het bericht ontving
        """
        connections = self.get_connections_for_conversation(conversation_id)
        sent = 0

        for conn in connections:
            if await self.send_json(conn.client_id, data):
                sent += 1

        return sent

    async def broadcast(self, data: dict) -> int:
        """
        Stuur JSON naar alle clients.

        Returns:
            Aantal clients dat het bericht ontving
        """
        sent = 0
        client_ids = list(self._connections.keys())

        for client_id in client_ids:
            if await self.send_json(client_id, data):
                sent += 1

        return sent

    def update_heartbeat(self, client_id: str) -> None:
        """Update heartbeat timestamp voor client."""
        connection = self.get_connection(client_id)
        if connection:
            connection.last_heartbeat = time.time()

    async def check_heartbeats(self) -> list[str]:
        """
        Check en verwijder inactieve connecties.

        Returns:
            Lijst van verwijderde client IDs
        """
        now = time.time()
        stale = []

        async with self._lock:
            for client_id, conn in list(self._connections.items()):
                if now - conn.last_heartbeat > self.heartbeat_timeout:
                    stale.append(client_id)

            for client_id in stale:
                del self._connections[client_id]

        return stale

    @property
    def active_count(self) -> int:
        """Aantal actieve connecties."""
        return len(self._connections)

    def list_clients(self) -> list[dict]:
        """Lijst alle actieve clients."""
        return [
            {
                "client_id": conn.client_id,
                "conversation_id": conn.conversation_id,
                "connected_at": conn.connected_at,
                "last_heartbeat": conn.last_heartbeat
            }
            for conn in self._connections.values()
        ]
