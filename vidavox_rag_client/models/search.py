"""
Models for search operations
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


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
    """Document result from search operation."""
    id: str
    name: str
    relevance_score: float
    content_preview: str
    metadata: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchDocument':
        """Create SearchDocument instance from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            relevance_score=data.get('relevance_score', 0.0),
            content_preview=data.get('content_preview', ''),
            metadata=data.get('metadata', {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert search document to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'relevance_score': self.relevance_score,
            'content_preview': self.content_preview,
            'metadata': self.metadata
        }

    def __str__(self) -> str:
        """String representation of search document."""
        return f"SearchDocument(name='{self.name}', score={self.relevance_score:.3f})"


@dataclass
class SearchResponse:
    """Response model for search operations."""
    response: str
    documents: List[SearchDocument]
    query: str
    prompt_type: str
    total_documents: int
    processing_time: float
    model_used: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResponse':
        """Create SearchResponse instance from dictionary."""
        # Parse documents
        documents = []
        if 'documents' in data:
            documents = [SearchDocument.from_dict(
                doc) for doc in data['documents']]
        elif 'sources' in data:
            # Handle alternative format where documents are called 'sources'
            documents = [SearchDocument.from_dict(
                doc) for doc in data['sources']]

        # Parse datetime if present
        created_at = None
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(
                    data['created_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        return cls(
            response=data.get('response', data.get('answer', '')),
            documents=documents,
            query=data.get('query', ''),
            prompt_type=data.get('prompt_type', 'agentic'),
            total_documents=data.get('total_documents', len(documents)),
            processing_time=data.get('processing_time', 0.0),
            model_used=data.get('model_used'),
            created_at=created_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert search response to dictionary."""
        return {
            'response': self.response,
            'documents': [doc.to_dict() for doc in self.documents],
            'query': self.query,
            'prompt_type': self.prompt_type,
            'total_documents': self.total_documents,
            'processing_time': self.processing_time,
            'model_used': self.model_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @property
    def best_documents(self, limit: int = 3) -> List[SearchDocument]:
        """Get the top N documents by relevance score."""
        return sorted(self.documents, key=lambda x: x.relevance_score, reverse=True)[:limit]

    def __str__(self) -> str:
        """String representation of search response."""
        return f"SearchResponse(query='{self.query}', docs={len(self.documents)}, time={self.processing_time:.2f}s)"


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
