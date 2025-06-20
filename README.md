# Vidavox RAG Client

A Python client library to interact with Vidavox RAG (Retrieval-Augmented Generation) API for managing folders, uploading files, and performing semantic search on document collections.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🔧 Features

- 📁 **Folder Management** – Create, list, and delete folders
- 📄 **File Handling** – Upload, delete, and fetch document IDs from folders
- 🔍 **Semantic Search** – RAG-based query answering over uploaded documents
- 🔍 **Multi-Folder Search** – Search across multiple folders simultaneously
- 🔁 **End-to-End Workflow** – Upload + search + cleanup in one client flow
- 🔐 **API Key Authentication** – Secure interaction with your RAG service
- 🧪 **Examples Included** – Easy-to-use scripts under `examples/`

---

## 📦 Installation

```bash
# Install from source
git clone https://github.com/deduu/vidavox_client.git
cd vidavox_client
pip install -e .

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies and package
pip install -r requirements.txt
pip install -e .
```

Ensure your environment includes Python 3.8 or higher.

## ⚙️ Configuration

The client reads the RAG API base URL and API key from environment variables or .env:

```env
# create .env file in your root project and add your API key
VIDAVOX_API_KEY="" # Your API key
```

Alternatively, you can pass config explicitly to the client constructor.

## 🚀 Quick Start

Here's a full working pipeline example using the client:

```python
from vidavox_rag_client.client import RAGClient
from pathlib import Path
import json, sys, time

client = RAGClient(
    api_key="your-api-key",
    timeout=120
)

folder_name = "My Doc"
file_paths = ["./docs/PACKING LIST.pdf", "./docs/Journal.pdf"]

# 1. Create folder
try:
    folder = client.create_folder(folder_name)
except Exception:
    folder_id = client.find_folder_id(folder_name)
    folder = type("Dummy", (), {"id": folder_id, "name": folder_name})

# 2. Upload files
client.upload_files_to_folder(folder_name=folder_name, file_paths=file_paths)

# 3. Get file IDs
file_ids = client.get_file_ids_in_folder_by_name(folder_name, recursive=True)

# 4. Perform RAG search
results = client.rag_search_in_folder(
    folder_name=folder_name,
    query="What is the introduction of this paper?",
    top_k=5,
    threshold=0.4,
    prompt_type="agentic"
)
print(json.dumps(results.to_dict(), indent=2))

# 5. Cleanup
client.delete_files(file_ids)
client.delete_folder_by_name(folder_name)
client.close()
```

## 🧪 Examples

You can explore these scripts inside the `examples/` folder:

| File             | Description                                  |
| ---------------- | -------------------------------------------- |
| `basic_test.py`  | Full flow: create → upload → search → delete |
| `basic_usage.py` | Minimal demonstration of usage               |

## 🧩 API Overview

### Initialization

```python
from vidavox_rag_client.client import RAGClient

# From environment
client = RAGClient()

# Or explicit config
client = RAGClient(api_key="your-key")
```

### Folder Operations

```python
folder = client.create_folder("Project Reports")
client.delete_folder_by_name("Project Reports")
folder_tree = client.get_folder_tree()
```

### File Operations

```python
# Upload
client.upload_files_to_folder("Project Reports", ["file1.pdf", "file2.pdf"])

# Get file IDs
ids = client.get_file_ids_in_folder_by_name("Project Reports", recursive=True)

# Delete
client.delete_files(ids)
```

### RAG Search

#### Single Folder Search

```python
response = client.rag_search_in_folder(
    folder_name="Project Reports",
    query="Summarize the abstract",
    top_k=3,
    threshold=0.5,
    prompt_type="agentic"
)
print(response.response)
```

#### Multi-Folder Search

Search across multiple folders simultaneously:

```python
response = client.rag_search_in_folders(
    folder_names=["Project Reports", "Research Papers", "Documentation"],
    query="What are the key findings?",
    top_k=10,
    threshold=0.4,
    prompt_type="agentic",
    prefixes=None,  # Optional: additional file ID prefixes
    include_doc_ids=None,  # Optional: specific docs to include
    exclude_doc_ids=None   # Optional: specific docs to exclude
)
print(response.response)
```

## 🧯 Error Handling

Gracefully catch common API exceptions:

```python
from vidavox_rag_client.exceptions import RAGAPIError, NotFoundError

try:
    client.delete_folder_by_name("Nonexistent Folder")
except NotFoundError:
    print("Folder not found.")
except RAGAPIError as e:
    print(f"Unexpected error: {e}")

# Multi-folder search error handling
try:
    response = client.rag_search_in_folders(
        folder_names=["Folder1", "NonexistentFolder"],
        query="test query"
    )
except NotFoundError as e:
    print(f"One or more folders not found: {e}")
```

## 🧪 Development

```bash
# Clone and setup
git clone https://github.com/deduu/vidavox_client.git
cd vidavox_client
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install local package
pip install -e .
```

### ✅ Testing

Tests can be added under a `tests/` directory.

```bash
pytest
```

## 🧑‍💻 Contributing

1. Fork this repo
2. Create a feature branch (`git checkout -b feat/feature-name`)
3. Commit changes
4. Push and open a PR

## 📄 License

This project is licensed under the MIT License. See LICENSE for more information.

## 🔗 Links

- 📘 **Docs**: See examples folder
- 🐞 **Bugs**: [Issue Tracker](https://github.com/deduu/vidavox_client/issues)
- 💬 **Discussion**: [GitHub Discussions](https://github.com/deduu/vidavox_client/discussions)

---

✔ **Built with care by [@deduu](https://github.com/deduu)**
