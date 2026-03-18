from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Message, Session, SessionState
from src.database.session import get_db

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])

class SessionCreate(BaseModel):
    user_id: str

class SessionResponse(BaseModel):
    session_id: UUID
    vnc_host: str | None = None
    status: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=list[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Session).order_by(Session.created_at.desc()))
    sessions = result.scalars().all()
    
    return [
        SessionResponse(
            session_id=s.id,
            vnc_host=None,
            status=s.state.value,
            created_at=s.created_at
        )
        for s in sessions
    ]

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(session_in: SessionCreate, db: AsyncSession = Depends(get_db)):
    # Create an empty session
    new_session = Session(
        user_id=session_in.user_id,
        state=SessionState.IDLE
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return SessionResponse(
        session_id=new_session.id,
        vnc_host=None,  # Handled dynamically by VNC provisioning in later steps
        status=new_session.state.value,
        created_at=new_session.created_at
    )

class MessageResponse(BaseModel):
    role: str
    content: Any

@router.get("/{session_id}/history", response_model=list[MessageResponse])
async def get_session_history(session_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message).where(Message.session_id == session_id).order_by(Message.sequence)
    )
    messages = result.scalars().all()
    if not messages:
        return []

    return [MessageResponse(role=msg.role.value, content=msg.content) for msg in messages]
