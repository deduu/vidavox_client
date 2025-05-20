# src/utils.py

"""
Helper functions for HTTP requests and error handling
"""
import requests
from typing import Dict, Any
from .config import HEADERS


def _handle_response(response: requests.Response) -> Any:
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"API Error: {e}, {response.text}")
    if response.status_code == 204:
        return None
    return response.json()


def get(url: str, params: Dict[str, Any] = None, headers: Dict[str, str] = HEADERS) -> Any:
    response = requests.get(url, params=params, headers=headers)
    return _handle_response(response)


def post(url: str, json: Dict[str, Any] = None, files: Any = None,
         data: Any = None, headers: Dict[str, str] = HEADERS) -> Any:
    response = requests.post(url, json=json, files=files,
                             data=data, headers=headers)
    return _handle_response(response)


def delete(url: str, headers: Dict[str, str] = HEADERS) -> Any:
    response = requests.delete(url, headers=headers)
    return _handle_response(response)
