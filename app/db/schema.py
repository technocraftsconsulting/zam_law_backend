import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import String, DateTime, Boolean, Enum, Text, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db import Base


def enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    return [e.value for e in enum_cls]


class Precedential(enum.Enum):
    BINDING = "BINDING"
    PERSUASIVE = "PERSUASIVE"
    NON_PRECEDENTIAL = "NON_PRECEDENTIAL"


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class DocType(enum.Enum):
    CASE_LAW = "CASE_LAW"
    STATUTE = "STATUTE"
    REGULATION = "REGULATION"
    CONSTITUTION = "CONSTITUTION"
    LEGAL_MEMO = "LEGAL_MEMO"
    OTHER = "OTHER"


class IngestionStatus(enum.Enum):
    PENDING = "PENDING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class VerificationMethod(enum.Enum):
    EXACT_MATCH = "EXACT_MATCH"
    FUZZY_MATCH = "FUZZY_MATCH"
    CHUNK_LOOKUP = "CHUNK_LOOKUP"
    UNVERIFIED = "UNVERIFIED"
    MANUALLY_CONFIRMED = "MANUALLY_CONFIRMED"


class EventType(enum.Enum):
    ADMIN_LOGIN = "ADMIN_LOGIN"
    ADMIN_LOGOUT = "ADMIN_LOGOUT"
    ADMIN_LOGIN_FAILED = "ADMIN_LOGIN_FAILED"
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    DOCUMENT_UPDATED = "DOCUMENT_UPDATED"
    DOCUMENT_DELETED = "DOCUMENT_DELETED"
    INGESTION_STARTED = "INGESTION_STARTED"
    INGESTION_COMPLETED = "INGESTION_COMPLETED"
    INGESTION_FAILED = "INGESTION_FAILED"
    SESSION_CREATED = "SESSION_CREATED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    MESSAGE_SENT = "MESSAGE_SENT"
    RAG_QUERY_COMPLETED = "RAG_QUERY_COMPLETED"
    RAG_QUERY_FAILED = "RAG_QUERY_FAILED"
    CITATION_VERIFIED = "CITATION_VERIFIED"
    CITATION_FLAGGED = "CITATION_FLAGGED"
    HALLUCINATION_DETECTED = "HALLUCINATION_DETECTED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


class MessageRole(enum.Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=enum_values, name="userrole")
    )
    is_active: Mapped[bool] = mapped_column(Boolean)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    documents: Mapped[List["Document"]] = relationship(back_populates="admin")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="admin")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("admins.id"))
    title: Mapped[str] = mapped_column(String(255))
    doc_type: Mapped[DocType] = mapped_column(
        Enum(DocType, values_callable=enum_values, name="doctype")
    )
    jurisdiction: Mapped[str] = mapped_column(String(255))
    citation: Mapped[Optional[str]] = mapped_column(String(255))
    decided_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_good_law: Mapped[bool] = mapped_column(Boolean)
    storage_path: Mapped[str] = mapped_column(String(255))
    ingestion_status: Mapped[IngestionStatus] = mapped_column(
        Enum(IngestionStatus, values_callable=enum_values, name="ingestionstatus")
    )
    ingested_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    admin: Mapped["Admin"] = relationship(back_populates="documents")
    chunks: Mapped[List["DocumentChunk"]] = relationship(back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    vector_id: Mapped[int] = mapped_column(unique=True, index=True)
    chunk_index: Mapped[int] = mapped_column()
    text_preview: Mapped[str] = mapped_column(Text)
    section_path: Mapped[List[str]] = mapped_column(ARRAY(Text))
    is_holding: Mapped[bool] = mapped_column(Boolean)
    precedential: Mapped[Precedential] = mapped_column(
        Enum(Precedential, values_callable=enum_values, name="precedential")
    )
    prev_chunk_id: Mapped[Optional[int]] = mapped_column(ForeignKey("document_chunks.id"))
    next_chunk_id: Mapped[Optional[int]] = mapped_column(ForeignKey("document_chunks.id"))
    token_count: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    document: Mapped["Document"] = relationship(back_populates="chunks")

    prev_chunk: Mapped[Optional["DocumentChunk"]] = relationship(
        foreign_keys=[prev_chunk_id],
        remote_side="DocumentChunk.id",
        uselist=False,
    )

    next_chunk: Mapped[Optional["DocumentChunk"]] = relationship(
        foreign_keys=[next_chunk_id],
        remote_side="DocumentChunk.id",
        uselist=False,
    )

    retrieved_chunks: Mapped[List["RetrievedChunk"]] = relationship(back_populates="document_chunk")
    citations: Mapped[List["Citation"]] = relationship(back_populates="document_chunk")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_token: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    jurisdiction_hint: Mapped[Optional[str]] = mapped_column(String(255))
    ip_hash: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime)

    messages: Mapped[List["Message"]] = relationship(back_populates="session")
    rag_queries: Mapped[List["RagQuery"]] = relationship(back_populates="session")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="session")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, values_callable=enum_values, name="messagerole")
    )
    content: Mapped[str] = mapped_column(Text)
    turn_index: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    session: Mapped["ChatSession"] = relationship(back_populates="messages")
    rag_query: Mapped[Optional["RagQuery"]] = relationship(back_populates="message")


class RagQuery(Base):
    __tablename__ = "rag_queries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"))

    raw_query: Mapped[str] = mapped_column(Text)
    detected_jurisdiction: Mapped[Optional[str]] = mapped_column(String(255))

    retrieval_ms: Mapped[int] = mapped_column()
    generation_ms: Mapped[int] = mapped_column()
    grounding_score: Mapped[float] = mapped_column()
    hallucination_flags: Mapped[int] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    session: Mapped["ChatSession"] = relationship(back_populates="rag_queries")
    message: Mapped["Message"] = relationship(back_populates="rag_query")

    retrieved_chunks: Mapped[List["RetrievedChunk"]] = relationship(back_populates="rag_query")
    citations: Mapped[List["Citation"]] = relationship(back_populates="rag_query")


class RetrievedChunk(Base):
    __tablename__ = "retrieved_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    query_id: Mapped[int] = mapped_column(ForeignKey("rag_queries.id"))
    chunk_id: Mapped[int] = mapped_column(ForeignKey("document_chunks.id"))

    rank_position: Mapped[int] = mapped_column()
    dense_score: Mapped[float] = mapped_column()
    sparse_score: Mapped[float] = mapped_column()
    rerank_score: Mapped[float] = mapped_column()

    used_in_context: Mapped[bool] = mapped_column(Boolean)

    rag_query: Mapped["RagQuery"] = relationship(back_populates="retrieved_chunks")
    document_chunk: Mapped["DocumentChunk"] = relationship(back_populates="retrieved_chunks")


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    query_id: Mapped[int] = mapped_column(ForeignKey("rag_queries.id"))
    chunk_id: Mapped[Optional[int]] = mapped_column(ForeignKey("document_chunks.id"))

    raw_citation_text: Mapped[str] = mapped_column(Text)
    verified: Mapped[bool] = mapped_column(Boolean)
    verification_method: Mapped[VerificationMethod] = mapped_column(
        Enum(VerificationMethod, values_callable=enum_values, name="verificationmethod")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    rag_query: Mapped["RagQuery"] = relationship(back_populates="citations")
    document_chunk: Mapped["DocumentChunk"] = relationship(back_populates="citations")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id"))
    session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("chat_sessions.id"))

    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, values_callable=enum_values, name="eventtype")
    )
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True))
    payload: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    session: Mapped["ChatSession"] = relationship(back_populates="audit_logs")
    admin: Mapped["Admin"] = relationship(back_populates="audit_logs")
