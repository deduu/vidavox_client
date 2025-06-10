"""
Models for file operations
"""

from dataclasses import dataclass, field
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
    # existing fields:
    results: List[UploadResult]
    total_uploaded: int
    total_failed: int
    message: str = ""

    # new fields (match exactly what your backend returns)
    success: bool = False
    folder_id: Optional[str] = None
    filenames: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UploadResponse":
        """Create UploadResponse instance from dictionary."""
        results: List[UploadResult] = []

        # 1) preserve the existing logic for "results" / "files" / "file"…
        if "results" in data:
            results = [UploadResult.from_dict(r) for r in data["results"]]
        elif "files" in data:
            # “files” ➔ we only know them as fully successful File uploads
            for file_data in data["files"]:
                results.append(UploadResult(
                    file=File.from_dict(file_data),
                    success=True
                ))
        elif "file" in data:
            results.append(UploadResult(
                file=File.from_dict(data["file"]),
                success=True
            ))
        # 2) if none of those keys exist, leave results = []

        total_uploaded = data.get(
            "total_uploaded",
            len([r for r in results if r.success])
        )
        total_failed = data.get(
            "total_failed",
            len([r for r in results if not r.success])
        )

        # 3) read the newly added keys:
        success = data.get("success", False)
        folder_id = data.get("folder_id")
        filenames = data.get("filenames", [])

        return cls(
            results=results,
            total_uploaded=total_uploaded,
            total_failed=total_failed,
            message=data.get("message", ""),
            success=success,
            folder_id=folder_id,
            filenames=filenames
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert upload response to dictionary (including new fields)."""
        return {
            "success": self.success,
            "folder_id": self.folder_id,
            "filenames": self.filenames,
            "results": [r.to_dict() for r in self.results],
            "total_uploaded": self.total_uploaded,
            "total_failed": self.total_failed,
            "message": self.message,
        }

    @property
    def successful_files(self) -> List[File]:
        return [r.file for r in self.results if r.success and r.file]

    @property
    def failed_uploads(self) -> List[UploadResult]:
        return [r for r in self.results if not r.success]

    def __str__(self) -> str:
        return (
            f"UploadResponse(success={self.success}, "
            f"folder_id={self.folder_id!r}, "
            f"filenames={self.filenames!r}, "
            f"uploaded={self.total_uploaded}, "
            f"failed={self.total_failed})"
        )


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


@dataclass
class DeletedFile:
    id: str
    filename: str
    folder_id: str
    path: str
    url: str
    uploaded_at: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeletedFile":
        return cls(
            id=data["id"],
            filename=data["filename"],
            folder_id=data["folder_id"],
            path=data["path"],
            url=data["url"],
            uploaded_at=datetime.fromisoformat(data["uploaded_at"]),
        )


@dataclass
class DeleteResponse:
    success: bool
    deleted_docs: int
    files_scheduled: int
    records: List[DeletedFile]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteResponse":
        recs = [DeletedFile.from_dict(r) for r in data.get("records", [])]
        return cls(
            success=data.get("success", True),
            deleted_docs=data.get("deleted_docs", len(recs)),
            files_scheduled=data.get("files_scheduled", 0),
            records=recs,
        )
