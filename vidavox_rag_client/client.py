"""
RAG API Client - Main client class
"""

import os
import json
from typing import List, Dict, Any, Optional, Union
import requests
from pathlib import Path

from vidavox_rag_client.config import Config
from vidavox_rag_client.exceptions import (
    RAGAPIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    ServerError
)
from vidavox_rag_client.models.folder import Folder, FolderCreateRequest
from vidavox_rag_client.models.file import File, UploadResponse
from vidavox_rag_client.models.search import SearchResponse, SearchRequest


class RAGClient:
    """
    Main client class for interacting with the RAG API.

    This client provides methods for folder management, file operations,
    and search functionality with proper error handling and response parsing.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the RAG API client.

        Args:
            base_url: Base URL of the RAG API (defaults to config)
            api_key: API key for authentication (defaults to config)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.config = Config()
        self.base_url = base_url or self.config.base_url
        self.api_key = api_key or self.config.api_key
        self.timeout = timeout
        self.max_retries = max_retries

        if not self.base_url:
            raise ValueError("Base URL is required")
        if not self.api_key:
            raise ValueError("API key is required")

        # Remove trailing slash from base URL
        self.base_url = self.base_url.rstrip('/')

        # Setup session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'doc-api-key': self.api_key,
            'User-Agent': f'RAG-Client/{self._get_version()}'
        })

    def _get_version(self) -> str:
        """Get client version."""
        try:
            from . import __version__
            return __version__
        except ImportError:
            return "0.1.0"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make an authenticated request to the API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            RAGAPIError: For various API error conditions
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Set default timeout
        kwargs.setdefault('timeout', self.timeout)

        try:
            response = self.session.request(method, url, **kwargs)
            self._handle_response_errors(response)
            return response
        except requests.exceptions.Timeout:
            raise RAGAPIError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise RAGAPIError("Connection error")
        except requests.exceptions.RequestException as e:
            raise RAGAPIError(f"Request failed: {str(e)}")

    def _handle_response_errors(self, response: requests.Response) -> None:
        """
        Handle HTTP response errors and raise appropriate exceptions.

        Args:
            response: HTTP response object

        Raises:
            AuthenticationError: For 401 Unauthorized
            NotFoundError: For 404 Not Found
            ValidationError: For 400 Bad Request
            ServerError: For 5xx Server Errors
            RAGAPIError: For other error conditions
        """
        if response.status_code < 400:
            return

        try:
            error_data = response.json()
            error_message = error_data.get('message', response.text)
        except (json.JSONDecodeError, ValueError):
            error_message = response.text or f"HTTP {response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(error_message)
        elif response.status_code == 404:
            raise NotFoundError(error_message)
        elif response.status_code == 400:
            raise ValidationError(error_message)
        elif 500 <= response.status_code < 600:
            raise ServerError(error_message)
        else:
            raise RAGAPIError(f"HTTP {response.status_code}: {error_message}")

    # Folder Operations

    def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None
    ) -> Folder:
        """
        Create a new folder.

        Args:
            name: Folder name
            parent_id: Optional parent folder ID

        Returns:
            Created folder object
        """
        request_data = FolderCreateRequest(name=name, parent_id=parent_id)

        response = self._make_request(
            'POST',
            '/folders/',
            json=request_data.dict(exclude_none=True),
            headers={'Content-Type': 'application/json'}
        )

        return Folder.from_dict(response.json())

    def delete_folder(self, folder_id: str) -> None:
        """
        Delete a folder.

        Args:
            folder_id: Folder ID to delete
        """
        self._make_request('DELETE', f'/folders/{folder_id}')

    # File Operations

    def upload_files(
        self,
        folder_id: str,
        file_paths: List[Union[str, Path]]
    ) -> UploadResponse:
        """
        Upload files to a folder.

        Args:
            folder_id: Target folder ID
            file_paths: List of file paths to upload

        Returns:
            Upload response with file information
        """
        files = []
        try:
            for file_path in file_paths:
                path = Path(file_path)
                if not path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")

                files.append(
                    ("files", (path.name, open(path, "rb"), "application/octet-stream"))
                )

            response = self._make_request(
                'POST',
                f'/folders/{folder_id}/v1/upload',
                files=files
            )

            return UploadResponse.from_dict(response.json())

        finally:
            # Ensure all file handles are closed
            for _, file_tuple in files:
                if hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()

    def process_directory(
        self,
        folder_id: str,
        directory_path: Union[str, Path]
    ) -> UploadResponse:
        """
        Process a local directory (server-side operation).

        Args:
            folder_id: Target folder ID
            directory_path: Path to directory to process

        Returns:
            Upload response with processed files
        """
        directory_path = str(Path(directory_path).resolve())

        response = self._make_request(
            'POST',
            f'/folders/{folder_id}/v1/upload',
            json={'directory_path': directory_path},
            headers={'Content-Type': 'application/json'}
        )

        return UploadResponse.from_dict(response.json())

    def delete_file(self, file_id: str) -> None:
        """
        Delete a file.

        Args:
            file_id: File ID to delete
        """
        self._make_request('DELETE', f'/folders/file/{file_id}')

    # Search Operations

    def search(
        self,
        folder_id: str,
        query: str,
        prompt_type: str = "agentic",
        prefixes: Optional[List[str]] = None,
        include_doc_ids: Optional[List[str]] = None,
        exclude_doc_ids: Optional[List[str]] = None
    ) -> SearchResponse:
        """
        Search documents in a folder.

        Args:
            folder_id: Folder ID to search in
            query: Search query
            prompt_type: Type of prompt ("agentic" or "consistency")
            prefixes: Optional list of prefixes to include
            include_doc_ids: Optional list of document IDs to include
            exclude_doc_ids: Optional list of document IDs to exclude

        Returns:
            Search response with results
        """
        search_request = SearchRequest(
            query=query,
            prompt_type=prompt_type,
            prefixes=prefixes,
            include_doc_ids=include_doc_ids,
            exclude_doc_ids=exclude_doc_ids
        )

        # Convert to form data for consistency with upload_and_search
        data = [("query", query), ("prompt_type", prompt_type)]

        if prefixes:
            for prefix in prefixes:
                data.append(("prefixes", prefix))

        if include_doc_ids:
            for doc_id in include_doc_ids:
                data.append(("include_doc_ids", doc_id))

        if exclude_doc_ids:
            for doc_id in exclude_doc_ids:
                data.append(("exclude_doc_ids", doc_id))

        response = self._make_request(
            'POST',
            f'/folders/{folder_id}/v1/search',
            data=data
        )

        return SearchResponse.from_dict(response.json())

    def upload_and_search(
        self,
        folder_id: str,
        query: str,
        prompt_type: str = "agentic",
        file_paths: Optional[List[Union[str, Path]]] = None,
        directory_path: Optional[Union[str, Path]] = None,
        prefixes: Optional[List[str]] = None,
        include_doc_ids: Optional[List[str]] = None,
        exclude_doc_ids: Optional[List[str]] = None
    ) -> SearchResponse:
        """
        Upload files and search in one operation.

        Args:
            folder_id: Target folder ID
            query: Search query
            prompt_type: Type of prompt ("agentic" or "consistency")
            file_paths: Optional list of file paths to upload
            directory_path: Optional directory path to process
            prefixes: Optional list of prefixes to include
            include_doc_ids: Optional list of document IDs to include
            exclude_doc_ids: Optional list of document IDs to exclude

        Returns:
            Search response with results
        """
        files = []
        data = [("query", query), ("prompt_type", prompt_type)]

        try:
            # Prepare files if provided
            if file_paths:
                for file_path in file_paths:
                    path = Path(file_path)
                    if not path.exists():
                        raise FileNotFoundError(f"File not found: {file_path}")

                    files.append(
                        ("files", (path.name, open(path, "rb"),
                         "application/octet-stream"))
                    )

            # Add directory path if provided
            if directory_path:
                directory_path = str(Path(directory_path).resolve())
                data.append(("directory_path", directory_path))

            # Add optional parameters
            if prefixes:
                for prefix in prefixes:
                    data.append(("prefixes", prefix))

            if include_doc_ids:
                for doc_id in include_doc_ids:
                    data.append(("include_doc_ids", doc_id))

            if exclude_doc_ids:
                for doc_id in exclude_doc_ids:
                    data.append(("exclude_doc_ids", doc_id))

            response = self._make_request(
                'POST',
                f'/folders/{folder_id}/v1/upload-and-search',
                files=files,
                data=data
            )

            return SearchResponse.from_dict(response.json())

        finally:
            # Ensure all file handles are closed
            for _, file_tuple in files:
                if hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session."""
        self.session.close()

    def close(self):
        """Explicitly close the client session."""
        self.session.close()
