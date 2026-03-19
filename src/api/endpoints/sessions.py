from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Message, Session, SessionState, VncEnvironment, VncEnvironmentStatus
from src.database.session import get_db
from src.services.docker_provisioner import docker_provisioner

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
    result = await db.execute(
        select(Session).options(selectinload(Session.vnc_environment)).order_by(Session.created_at.desc())
    )
    sessions = result.scalars().all()
    
    responses = []
    for s in sessions:
        vnc_host = None
        if s.vnc_environment:
            vnc_host = f"localhost:{s.vnc_environment.port}"
            
        responses.append(SessionResponse(
            session_id=s.id,
            vnc_host=vnc_host,
            status=s.state.value,
            created_at=s.created_at
        ))
    return responses

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

    # Provision Dynamic VNC Environment
    computed_vnc_host = None
    try:
        container_info = docker_provisioner.spawn_vnc_environment(new_session.id)
        
        # Create VncEnvironment record using host for container_name and port for host port
        vnc_env = VncEnvironment(
            host=container_info["container_name"],
            port=container_info["websockify_port"],
            status=VncEnvironmentStatus.IN_USE
        )
        db.add(vnc_env)
        await db.flush()

        new_session.vnc_environment_id = vnc_env.id
        await db.commit()
        await db.refresh(new_session)

        # We expose localhost with the mapped port to the UI since it runs from local browser mapping to host
        computed_vnc_host = f"localhost:{container_info['websockify_port']}"
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to provision VNC for session {new_session.id}: {e}")

    return SessionResponse(
        session_id=new_session.id,
        vnc_host=computed_vnc_host,
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
