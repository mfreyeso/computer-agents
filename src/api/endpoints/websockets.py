import asyncio
import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from src.core.concurrency import manager
from src.database.models import Message, MessageRole, MessageType
from src.database.session import AsyncSessionLocal
from src.services.anthropic_client import agent_client

router = APIRouter(prefix="/ws/v1/sessions", tags=["websockets"])

async def _process_turn(session_id: str, session_history: list):
    """
    Executes the agent loop continuously in the background allowing
    requests to process even if the user drops the connection.
    """
    # Ensure locks if we proceed (T018-T020 placeholder)
    lock = manager.session_locks.get(session_id)
    if lock and lock.locked():
        await manager.send_personal_message({"type": "error", "message": "Task is in progress"}, session_id)
        return

    if lock:
        await lock.acquire()

    try:
        # Feed to Anthropic
        async for chunk in agent_client.stream_agent_loop(messages=session_history, session_id=session_id):
            await manager.send_personal_message(chunk, session_id)

        # T022: Flush whole session to DB implicitly on turn-completion
        from sqlalchemy import func
        async with AsyncSessionLocal() as db:
            # Compute current max sequence to only append diffs
            result = await db.execute(select(func.max(Message.sequence)).where(Message.session_id == uuid.UUID(session_id)))
            max_seq = result.scalar()
            if max_seq is None:
                max_seq = -1
                
            for idx, m in enumerate(session_history):
                if idx > max_seq:
                    db_msg = Message(
                        session_id=uuid.UUID(session_id),
                        role=MessageRole(m["role"]),
                        type=MessageType.TEXT, # Abstracted type locally
                        content=m["content"],
                        sequence=idx
                    )
                    db.add(db_msg)
            await db.commit()

    except Exception as e:
        await manager.send_personal_message({"type": "error", "message": str(e)}, session_id)
    finally:
        if lock:
            lock.release()

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

                    # Run asynchronously so we don't block the WebSocket from receiving or disconnects
                    asyncio.create_task(_process_turn(session_id, session_history))

            except json.JSONDecodeError:
                await manager.send_personal_message({"error": "Invalid JSON"}, session_id)

    except WebSocketDisconnect:
        manager.disconnect(session_id)
