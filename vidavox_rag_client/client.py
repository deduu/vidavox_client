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
    ServerError,
    DuplicateFolderError
)
from vidavox_rag_client.models.folder import Folder, FolderCreateRequest
from vidavox_rag_client.models.file import File, UploadResponse, DeleteResponse
from vidavox_rag_client.models.search import SearchResponse, SearchRequest
from vidavox_rag_client.helper import _find_folder_id, _find_folder_node_by_id, _collect_immediate_file_ids, _collect_all_file_ids_recursive


class RAGClient:
    """
    Main client class for interacting with the RAG API.

    This client provides methods for folder management, file operations,
    and search functionality with proper error handling and response parsing.
    """

    def __init__(
        self,
        base_url: Optional[str] = "http://34.27.153.226:8003",
        api_key: Optional[str] = None,
        timeout: int = 3600,
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
        self.config = Config(
            override_base_url=base_url,
            override_api_key=api_key
        )

        self.base_url = self.config.base_url
        self.api_key = self.config.api_key
        self.timeout = timeout
        self.max_retries = max_retries

        if not self.base_url:
            raise ValueError("Base URL is required")
        if not self.api_key:
            raise ValueError("API key is required")

        if self.api_key:
            self.config.api_key = self.api_key

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
        elif response.status_code == 409:
            raise DuplicateFolderError(response.json()["detail"])
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
            '/v1/folders/',
            json=request_data.dict(exclude_none=True),
            headers={'Content-Type': 'application/json'}
        )

        return Folder.from_dict(response.json())

    def delete_folder(self, folder_id: str) -> DeleteResponse:
        """
        Delete a folder by ID and return the server’s structured response.

        Raises
        -------
        NotFoundError
            If the folder ID is not present in the cached folder tree.
        """
        # 1) make sure it exists locally (optional but nice UX)
        if not self.find_folder_node_by_id(folder_id):
            raise NotFoundError(
                f"Folder with ID '{folder_id}' does not exist.")

        # 2) call backend – assume _make_request returns the decoded JSON dict
        resp: dict = self._make_request(
            "DELETE",
            f"/v1/folders/{folder_id}",
        )

        # 3) parse into typed response object
        raw_json: dict = resp.json()          # <─ add .json()
        return DeleteResponse.from_dict(raw_json)

    def delete_folder_by_name(self, folder_name: str) -> DeleteResponse:
        """
        Convenience wrapper: resolve folder name → ID → delete.
        """
        folder_id = self.find_folder_id(folder_name)
        if not folder_id:
            raise NotFoundError(f"Folder named '{folder_name}' not found.")

        return self.delete_folder(folder_id)
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
                f'/v1/folders/{folder_id}/upload',
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
            f'/v1/folders/{folder_id}/upload',
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
        self._make_request('DELETE', f'/v1/folders/file/{file_id}')

    def delete_files(
        self,
        file_ids: List[str],
        raise_on_error: bool = True
    ) -> Dict[str, bool]:
        """
        Delete multiple files by their IDs.

        Args:
            file_ids: List of file-ID strings to delete.
            raise_on_error: If True, raise on first error. If False, continue and return results.

        Returns:
            Dict mapping file_id -> success boolean
        """
        results: Dict[str, bool] = {}
        first_error = None

        for fid in file_ids:
            try:
                self.delete_file(fid)
                results[fid] = True
            except Exception as e:
                results[fid] = False
                if raise_on_error and first_error is None:
                    first_error = e

        # If raise_on_error=True and we had any errors, raise the first one
        if raise_on_error and first_error:
            raise first_error

        return results

    # Search Operations

    def search(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.4,
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
        data = [("query", query), ("prompt_type", prompt_type),
                ("top_k", top_k), ("threshold", threshold)]

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
            f'/v1/analysis/perform_rag',
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
                f'/v1/folders/{folder_id}/upload-and-search',
                files=files,
                data=data
            )

            return SearchResponse.from_dict(response.json())

        finally:
            # Ensure all file handles are closed
            for _, file_tuple in files:
                if hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()

    def get_folder_tree(self) -> List[Dict[str, Any]]:
        response = self._make_request("GET", "/v1/folders/tree")
        return response.json()

    def find_folder_node_by_id(self, folder_id: str) -> Optional[Dict[str, Any]]:
        """
        Search the user's folder tree for a folder with the exact ID.
        Returns its node if found, else None.
        """
        tree = self.get_folder_tree()
        return _find_folder_node_by_id(tree, folder_id)

    def find_folder_id(self, folder_name: str) -> Optional[str]:
        """
        Search the user's folder tree for a folder with the exact name.
        Returns its ID if found, else None.
        """
        tree = self.get_folder_tree()
        return _find_folder_id(tree, folder_name)

    def get_file_ids_in_folder(
        self,
        folder_id: str,
        recursive: bool = False
    ) -> List[str]:
        """
        Given a folder_id, return a list of file IDs contained within that folder.
        By default, this only returns the immediate children of type 'file'.
        If recursive=True, also descend into subfolders and return all nested file IDs.

        Raises NotFoundError if folder_id does not exist in the tree.
        """
        # 1) Fetch the entire tree
        tree = self.get_folder_tree()

        # 2) Locate the folder node by its ID
        folder_node = _find_folder_node_by_id(tree, folder_id)
        if not folder_node:
            raise NotFoundError(f"Folder with id '{folder_id}' not found.")

        # 3) Collect file IDs
        if recursive:
            return _collect_all_file_ids_recursive(folder_node)
        else:
            return _collect_immediate_file_ids(folder_node)

    def get_file_ids_in_folder_by_name(
        self,
        folder_name: str,
        recursive: bool = False
    ) -> List[str]:
        """
        Find a folder by folder_name, then return a list of file IDs under it.
        By default, this only returns the immediate children of type 'file'.
        If recursive=True, it will also collect files nested inside subfolders.

        Raises NotFoundError if folder_name does not exist.
        """
        folder_id = self.find_folder_id(folder_name)
        if not folder_id:
            raise NotFoundError(f"Folder named '{folder_name}' not found.")
        return self.get_file_ids_in_folder(folder_id, recursive=recursive)

    def upload_files_to_folder(
        self,
        folder_name: str,
        file_paths: List[Union[str, Path]]
    ) -> UploadResponse:
        """
        Convenience wrapper: find a folder by name, then upload files there.
        Raises FileNotFoundError if folder not found, or if any file missing.
        """
        folder_id = self.find_folder_id(folder_name)
        if not folder_id:
            raise NotFoundError(
                f"Folder named '{folder_name}' not found in your tree.")

        return self.upload_files(folder_id, file_paths)

    def rag_search_in_folders(
        self,
        folder_names: List[str],
        query: str,
        top_k: int = 10,
        threshold: float = 0.4,
        prompt_type: str = "agentic",
        prefixes: Optional[List[str]] = None,
        include_doc_ids: Optional[List[str]] = None,
        exclude_doc_ids: Optional[List[str]] = None,
    ) -> SearchResponse:
        """
        Extended wrapper: accept multiple folder names and run search on all their files.

        Raises NotFoundError if any folder is not found.
        """
        all_file_ids = []

        for folder_name in folder_names:
            folder_id = self.find_folder_id(folder_name)
            if not folder_id:
                raise NotFoundError(
                    f"Folder named '{folder_name}' not found in your tree.")

            file_ids = self.get_file_ids_in_folder(folder_id, recursive=True)
            all_file_ids.extend(file_ids)

        # Merge with user-supplied prefixes, then deduplicate
        combined_prefixes = list(set(all_file_ids + (prefixes or [])))

        return self.search(
            query=query,
            top_k=top_k,
            threshold=threshold,
            prompt_type=prompt_type,
            prefixes=combined_prefixes,
            include_doc_ids=include_doc_ids,
            exclude_doc_ids=exclude_doc_ids
        )

    # Key methods to add for better developer experience

    def list_folders(self, parent_id: Optional[str] = None) -> List[Folder]:
        """List all folders, optionally filtered by parent."""
        endpoint = "/v1/folders/"
        if parent_id:
            endpoint += f"?parent_id={parent_id}"

        response = self._make_request('GET', endpoint)
        return [Folder.from_dict(folder) for folder in response.json()]

    def get_folder(self, folder_id: str) -> Folder:
        """Get detailed information about a specific folder."""
        response = self._make_request('GET', f'/v1/folders/{folder_id}')
        return Folder.from_dict(response.json())

    def list_files(self, folder_id: str) -> List[File]:
        """List all files in a folder."""
        response = self._make_request('GET', f'/v1/folders/{folder_id}/files')
        return [File.from_dict(file_data) for file_data in response.json()]

    def get_file(self, file_id: str) -> File:
        """Get detailed information about a specific file."""
        response = self._make_request('GET', f'/v1/files/{file_id}')
        return File.from_dict(response.json())

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session."""
        self.session.close()

    def close(self):
        """Explicitly close the client session."""
        self.session.close()
