import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from src.core.concurrency import manager
from src.database.models import Message, MessageRole, MessageType
from src.database.session import AsyncSessionLocal
from src.services.anthropic_client import agent_client

router = APIRouter(prefix="/ws/v1/sessions", tags=["websockets"])

@router.websocket("/{session_id}")
async def websocket_session(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)

    # In-memory history cache to build contextual loops
    session_history = []

    # T023: Hydrate context from Database
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Message).where(Message.session_id == uuid.UUID(session_id)).order_by(Message.sequence)
        )
        for msg in result.scalars().all():
            session_history.append({"role": msg.role.value, "content": msg.content})


    try:
        while True:
            # Wait for user input (prompt)
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)

                if payload.get("type") == "user_prompt":
                    session_history.append({"role": "user", "content": payload.get("text")})

                    # Ensure locks if we proceed (T018-T020 placeholder)
                    lock = manager.session_locks.get(session_id)
                    if lock and lock.locked():
                        await manager.send_personal_message({"type": "error", "message": "Task is in progress"}, session_id)
                        continue

                    if lock:
                        await lock.acquire()

                    try:
                        # Feed to Anthropic
                        async for chunk in agent_client.stream_agent_loop(messages=session_history):
                            await manager.send_personal_message(chunk, session_id)

                        # T022: Flush whole session to DB implicitly on turn-completion
                        async with AsyncSessionLocal() as db:
                            # In standard production, only append diffs. For MVP flush all.
                            await db.execute(Message.__table__.delete().where(Message.session_id == uuid.UUID(session_id)))
                            for idx, m in enumerate(session_history):
                                db_msg = Message(
                                    session_id=uuid.UUID(session_id),
                                    role=MessageRole(m["role"]),
                                    type=MessageType.TEXT, # Abstracted type locally
                                    content=m["content"],
                                    sequence=idx
                                )
                                db.add(db_msg)
                            await db.commit()

                    finally:
                        if lock:
                            lock.release()

            except json.JSONDecodeError:
                await manager.send_personal_message({"error": "Invalid JSON"}, session_id)

    except WebSocketDisconnect:
        manager.disconnect(session_id)
