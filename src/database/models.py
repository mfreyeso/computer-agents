import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from src.database.session import Base


class SessionState(enum.Enum):
    IDLE = "IDLE"
    EXECUTING = "EXECUTING"
    ERROR = "ERROR"

class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class MessageType(enum.Enum):
    TEXT = "text"
    THOUGHT = "thought"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"

class VncEnvironmentStatus(enum.Enum):
    PROVISIONING = "PROVISIONING"
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    TERMINATED = "TERMINATED"

class VncEnvironment(Base):
    __tablename__ = "vnc_environments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    status = Column(SQLEnum(VncEnvironmentStatus), default=VncEnvironmentStatus.AVAILABLE, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    vnc_environment_id = Column(UUID(as_uuid=True), ForeignKey("vnc_environments.id"), nullable=True)
    state = Column(SQLEnum(SessionState), default=SessionState.IDLE, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    vnc_environment = relationship("VncEnvironment")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    role = Column(SQLEnum(MessageRole), nullable=False)
    type = Column(SQLEnum(MessageType), nullable=False)
    content = Column(JSONB, nullable=False)
    sequence = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    session = relationship("Session", back_populates="messages")
