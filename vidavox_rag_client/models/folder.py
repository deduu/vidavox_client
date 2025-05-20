"""
Models for folder operations
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class FolderCreateRequest:
    """Request model for creating a folder."""
    name: str
    parent_id: Optional[str] = None

    def dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            'name': self.name,
            'parent_id': self.parent_id
        }
        if exclude_none:
            result = {k: v for k, v in result.items() if v is not None}
        return result


@dataclass
class Folder:
    """Folder model representing a folder in the RAG system."""
    id: str
    name: str
    parent_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    file_count: int = 0
    total_size: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Folder':
        """Create Folder instance from dictionary."""
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
            parent_id=data.get('parent_id'),
            created_at=created_at,
            updated_at=updated_at,
            file_count=data.get('file_count', 0),
            total_size=data.get('total_size', 0)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert folder to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'file_count': self.file_count,
            'total_size': self.total_size
        }

    def __str__(self) -> str:
        """String representation of folder."""
        return f"Folder(id='{self.id}', name='{self.name}', files={self.file_count})"


@dataclass
class FolderList:
    """Response model for listing folders."""
    folders: List[Folder]
    total: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FolderList':
        """Create FolderList instance from dictionary."""
        folders = [Folder.from_dict(folder_data)
                   for folder_data in data.get('folders', [])]
        return cls(
            folders=folders,
            total=data.get('total', len(folders))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert folder list to dictionary."""
        return {
            'folders': [folder.to_dict() for folder in self.folders],
            'total': self.total
        }
