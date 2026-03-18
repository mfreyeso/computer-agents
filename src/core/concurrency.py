import asyncio
import concurrent.futures

from fastapi import WebSocket


class ConnectionManager:
    """
    Manages active WebSocket connections mapped by session_id.
    Includes session-specific asyncio Locks to prevent race conditions (T018).
    Includes a ThreadPoolExecutor for offloading CPU-bound tool executions (T015).
    """
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.session_locks: dict[str, asyncio.Lock] = {}
        # Free-threading executor for offloading PyAutoGUI and screen captures
        self.tool_executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        if session_id not in self.session_locks:
            self.session_locks[session_id] = asyncio.Lock()

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        # We optionally keep the lock to avoid edge-cases where tasks are mid-flight during a drop

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()
