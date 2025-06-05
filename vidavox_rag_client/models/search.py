"""
Models for search operations
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


@dataclass
class SearchRequest:
    """Request model for search operations."""
    query: str
    prompt_type: str = "agentic"
    prefixes: Optional[List[str]] = None
    include_doc_ids: Optional[List[str]] = None
    exclude_doc_ids: Optional[List[str]] = None
    max_results: int = 10

    def to_form_data(self) -> List[tuple]:
        """Convert to form data format for API requests."""
        data = [
            ("query", self.query),
            ("prompt_type", self.prompt_type),
            ("max_results", str(self.max_results))
        ]

        if self.prefixes:
            for prefix in self.prefixes:
                data.append(("prefixes", prefix))

        if self.include_doc_ids:
            for doc_id in self.include_doc_ids:
                data.append(("include_doc_ids", doc_id))

        if self.exclude_doc_ids:
            for doc_id in self.exclude_doc_ids:
                data.append(("exclude_doc_ids", doc_id))

        return data

    def to_dict(self) -> Dict[str, Any]:
        """Convert search request to dictionary."""
        return {
            'query': self.query,
            'prompt_type': self.prompt_type,
            'prefixes': self.prefixes,
            'include_doc_ids': self.include_doc_ids,
            'exclude_doc_ids': self.exclude_doc_ids,
            'max_results': self.max_results
        }


@dataclass
class SearchDocument:
    """
    Lightweight client-side wrapper around a chunk returned by the RAG backend.
    Mirrors the shape of `DocumentChunk` sent by the API but deliberately
    keeps only what the UI typically needs.
    """
    id: str
    text: str
    relevance_score: float
    source: str
    page: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # --------------------------------------------------------------------- #
    # Factory helpers
    # --------------------------------------------------------------------- #
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchDocument":
        """
        Accepts either:
        • the `DocumentChunk` schema coming from the backend, or
        • a dict produced by `to_dict()` below (round-tripping).
        """
        return cls(
            id=data.get("id") or data.get("chunk_id", ""),
            text=data.get("text", ""),
            relevance_score=data.get(
                "relevance_score",          # ← already normalised by client
                data.get("score", 0.0)      # ← raw backend field
            ),
            source=data.get("source", ""),
            page=data.get("page"),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Round-trip back to JSON-serialisable form."""
        return {
            "id": self.id,
            "text": self.text,
            "relevance_score": self.relevance_score,
            "source": self.source,
            "page": self.page,
            "metadata": self.metadata,
        }


class Citation(BaseModel):
    """
    Pointer to evidence used in an LLM answer.
    Exactly mirrors the backend schema so the client can
    deserialise the JSON without extra glue code.
    """
    chunk_id: str = Field(..., description="ID of the cited chunk")
    quote: str = Field(..., description="Verbatim excerpt shown as evidence")
    source: str = Field(..., description="Human-readable source (URL)")
    page: Optional[int] = Field(
        None, description="Page number in the source document (if any)"
    )


@dataclass
class SearchResponse:
    # ─── top-level envelope ────────────────────────────────────────────────
    success: bool
    request_id: str

    # ─── RAG answer block ─────────────────────────────────────────────────
    answer: str
    citations: List[Citation]
    documents: List[SearchDocument]            # ← originally “used_chunks”
    total_documents: int

    # ─── misc. meta data ──────────────────────────────────────────────────
    stats: Dict[str, Any]
    model_used: Optional[str] = None
    created_at: Optional[datetime] = None

    # ---------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResponse":
        """Build SearchResponse from the backend JSON."""
        # Envelope
        success: bool = data.get("success", False)
        request_id: str = data.get("request_id", "")

        # RAG answer block (may be None on error cases)
        resp_block: Dict[str, Any] = data.get("response") or {}
        answer: str = resp_block.get("answer", "")
        citations = [Citation(**c) for c in resp_block.get("citations", [])]

        used_chunks = resp_block.get("used_chunks", [])
        documents = [SearchDocument.from_dict(c) for c in used_chunks]

        # Stats & misc
        stats: Dict[str, Any] = data.get("stats", {})
        model_used = stats.get("model_used")         # optional, if present

        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        return cls(
            success=success,
            request_id=request_id,
            answer=answer,
            citations=citations,
            documents=documents,
            total_documents=len(documents),
            stats=stats,
            model_used=model_used,
            created_at=created_at,
        )

    # ---------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """Round-trip back to the backend JSON shape."""
        return {
            "success": self.success,
            "request_id": self.request_id,
            "response": {
                "answer": self.answer,
                "citations": [c.model_dump() for c in self.citations],
                "used_chunks": [d.to_dict() for d in self.documents],
            },
            "stats": self.stats,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    # ---------------------------------------------------------------------
    def get_best_documents(self, limit: int = 3) -> List[SearchDocument]:
        """Return the top-`limit` documents sorted by relevance score."""
        return sorted(
            self.documents, key=lambda x: x.relevance_score, reverse=True
        )[:limit]

    # nicety for `print(response)`
    def __str__(self) -> str:
        return (
            f"SearchResponse(request_id='{self.request_id}', "
            f"docs={self.total_documents}, "
            f"latency_ms={self.stats.get('latency_ms', 'n/a')})"
        )


@dataclass
class SearchHistory:
    """Search history entry."""
    id: str
    query: str
    response: str
    folder_id: str
    prompt_type: str
    document_count: int
    created_at: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchHistory':
        """Create SearchHistory instance from dictionary."""
        created_at = datetime.fromisoformat(
            data['created_at'].replace('Z', '+00:00'))

        return cls(
            id=data['id'],
            query=data['query'],
            response=data['response'],
            folder_id=data['folder_id'],
            prompt_type=data.get('prompt_type', 'agentic'),
            document_count=data.get('document_count', 0),
            created_at=created_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert search history to dictionary."""
        return {
            'id': self.id,
            'query': self.query,
            'response': self.response,
            'folder_id': self.folder_id,
            'prompt_type': self.prompt_type,
            'document_count': self.document_count,
            'created_at': self.created_at.isoformat()
        }

    def __str__(self) -> str:
        """String representation of search history."""
        return f"SearchHistory(query='{self.query[:50]}...', docs={self.document_count})"
