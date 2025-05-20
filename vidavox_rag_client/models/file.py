"""
Models for file operations
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path


@dataclass
class File:
    """File model representing a file in the RAG system."""
    id: str
    name: str
    folder_id: str
    size: int
    content_type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: str = "processed"
    error_message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'File':
        """Create File instance from dictionary."""
        # Parse datetime strings if present
        created_at = None
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(
                    data['created_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        updated_at = None
        if data.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(
                    data['updated_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        return cls(
            id=data['id'],
            name=data['name'],
            folder_id=data['folder_id'],
            size=data.get('size', 0),
            content_type=data.get('content_type', 'application/octet-stream'),
            created_at=created_at,
            updated_at=updated_at,
            status=data.get('status', 'processed'),
            error_message=data.get('error_message')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert file to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'folder_id': self.folder_id,
            'size': self.size,
            'content_type': self.content_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status,
            'error_message': self.error_message
        }

    @property
    def size_human(self) -> str:
        """Human readable file size."""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        elif self.size < 1024 * 1024 * 1024:
            return f"{self.size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.size / (1024 * 1024 * 1024):.1f} GB"

    def __str__(self) -> str:
        """String representation of file."""
        return f"File(id='{self.id}', name='{self.name}', size={self.size_human})"


@dataclass
class UploadResult:
    """Result of a single file upload."""
    file: Optional[File] = None
    error: Optional[str] = None
    success: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UploadResult':
        """Create UploadResult instance from dictionary."""
        file_obj = None
        if data.get('file'):
            file_obj = File.from_dict(data['file'])

        return cls(
            file=file_obj,
            error=data.get('error'),
            success=data.get('success', False)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert upload result to dictionary."""
        return {
            'file': self.file.to_dict() if self.file else None,
            'error': self.error,
            'success': self.success
        }


@dataclass
class UploadResponse:
    """Response model for file upload operations."""
    results: List[UploadResult]
    total_uploaded: int
    total_failed: int
    message: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UploadResponse':
        """Create UploadResponse instance from dictionary."""
        results = []

        # Handle different response formats
        if 'results' in data:
            results = [UploadResult.from_dict(result)
                       for result in data['results']]
        elif 'files' in data:
            # Handle simple file list format
            for file_data in data['files']:
                results.append(UploadResult(
                    file=File.from_dict(file_data),
                    success=True
                ))
        elif 'file' in data:
            # Handle single file format
            results.append(UploadResult(
                file=File.from_dict(data['file']),
                success=True
            ))

        total_uploaded = data.get('total_uploaded', len(
            [r for r in results if r.success]))
        total_failed = data.get('total_failed', len(
            [r for r in results if not r.success]))

        return cls(
            results=results,
            total_uploaded=total_uploaded,
            total_failed=total_failed,
            message=data.get('message', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert upload response to dictionary."""
        return {
            'results': [result.to_dict() for result in self.results],
            'total_uploaded': self.total_uploaded,
            'total_failed': self.total_failed,
            'message': self.message
        }

    @property
    def successful_files(self) -> List[File]:
        """Get list of successfully uploaded files."""
        return [result.file for result in self.results if result.success and result.file]

    @property
    def failed_uploads(self) -> List[UploadResult]:
        """Get list of failed uploads."""
        return [result for result in self.results if not result.success]

    def __str__(self) -> str:
        """String representation of upload response."""
        return f"UploadResponse(uploaded={self.total_uploaded}, failed={self.total_failed})"


@dataclass
class FileList:
    """Response model for listing files."""
    files: List[File]
    total: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileList':
        """Create FileList instance from dictionary."""
        files = [File.from_dict(file_data)
                 for file_data in data.get('files', [])]
        return cls(
            files=files,
            total=data.get('total', len(files))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert file list to dictionary."""
        return {
            'files': [file.to_dict() for file in self.files],
            'total': self.total
        }
