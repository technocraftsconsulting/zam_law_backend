import enum
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import String, Integer, DateTime, Boolean, Enum, Text, ForeignKey, Float, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db import Base


class Precedential(enum.Enum):
    BINDING = "binding"
    PERSUASIVE = "persuasive"
    NON_PRECEDENTIAL = "non_precedential"


class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class DocType(enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    CSV = "csv"


class IngestionStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"


class VerificationMethod(enum.Enum):
    EXACT_MATCH = "exact_match"
    FUZZY_MATCH = "fuzzy_match"
    CHUNK_LOOKUP = "chunk_lookup"
    UNVERIFIED = "unverified"
    MANUALLY_CONFIRMED = "manually_confirmed"


class EventType(enum.Enum):
    ADMIN_LOGIN = "admin_login"
    ADMIN_LOGOUT = "admin_logout"
    ADMIN_LOGIN_FAILED = "admin_login_failed"
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_UPDATED = "document_updated"
    DOCUMENT_DELETED = "document_deleted"
    INGESTION_STARTED = "ingestion_started"
    INGESTION_COMPLETED = "ingestion_completed"
    INGESTION_FAILED = "ingestion_failed"
    SESSION_CREATED = "session_created"
    SESSION_EXPIRED = "session_expired"
    MESSAGE_SENT = "message_sent"
    RAG_QUERY_COMPLETED = "rag_query_completed"
    RAG_QUERY_FAILED = "rag_query_failed"
    CITATION_VERIFIED = "citation_verified"
    CITATION_FLAGGED = "citation_flagged"
    HALLUCINATION_DETECTED = "hallucination_detected"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


# ADMIN

class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    is_active: Mapped[bool] = mapped_column(Boolean)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    documents: Mapped[List["Document"]] = relationship(back_populates="admin")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="admin")


# DOCUMENT

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("admins.id"))
    title: Mapped[str] = mapped_column(String(255))
    doc_type: Mapped[DocType] = mapped_column(Enum(DocType))
    jurisdiction: Mapped[str] = mapped_column(String(255))
    citation: Mapped[Optional[str]] = mapped_column(String(255))
    decided_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_good_law: Mapped[bool] = mapped_column(Boolean)
    storage_path: Mapped[str] = mapped_column(String(255))
    ingestion_status: Mapped[IngestionStatus] = mapped_column(Enum(IngestionStatus))
    ingested_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    admin: Mapped["Admin"] = relationship(back_populates="documents")
    chunks: Mapped[List["DocumentChunk"]] = relationship(back_populates="document")


# DOCUMENT CHUNK

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    vector_id: Mapped[int] = mapped_column(unique=True, index=True)
    chunk_index: Mapped[int] = mapped_column()
    text_preview: Mapped[str] = mapped_column(Text)
    section_path: Mapped[List[str]] = mapped_column(ARRAY(Text))
    is_holding: Mapped[bool] = mapped_column(Boolean)
    precedential: Mapped[Precedential] = mapped_column(Enum(Precedential))
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


# CHAT SESSION

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


# MESSAGE

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole))
    content: Mapped[str] = mapped_column(Text)
    turn_index: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    session: Mapped["ChatSession"] = relationship(back_populates="messages")
    rag_query: Mapped[Optional["RagQuery"]] = relationship(back_populates="message")


# RAG QUERY

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


# RETRIEVED CHUNK

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


# CITATION

class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    query_id: Mapped[int] = mapped_column(ForeignKey("rag_queries.id"))
    chunk_id: Mapped[Optional[int]] = mapped_column(ForeignKey("document_chunks.id"))

    raw_citation_text: Mapped[str] = mapped_column(Text)
    verified: Mapped[bool] = mapped_column(Boolean)
    verification_method: Mapped[VerificationMethod] = mapped_column(Enum(VerificationMethod))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    rag_query: Mapped["RagQuery"] = relationship(back_populates="citations")
    document_chunk: Mapped["DocumentChunk"] = relationship(back_populates="citations")


# AUDIT LOG

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id"))
    session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("chat_sessions.id"))

    event_type: Mapped[EventType] = mapped_column(Enum(EventType))
    entity_id: Mapped[Optional[str]] = mapped_column(PG_UUID(as_uuid=True))
    payload: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    session: Mapped["ChatSession"] = relationship(back_populates="audit_logs")
    admin: Mapped["Admin"] = relationship(back_populates="audit_logs")