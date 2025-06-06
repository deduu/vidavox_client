# vidavox_client
# RAG API Client

A Python client library for interacting with RAG (Retrieval-Augmented Generation) API services.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- 🚀 **Simple and intuitive** API for folder and file management
- 📁 **Folder operations**: Create, delete, and manage folder hierarchies
- 📄 **File operations**: Upload individual files or entire directories
- 🔍 **Search capabilities**: Advanced search with filtering and prompt types
- 🔄 **Upload and search**: Combined operations for efficiency
- 🛡️ **Error handling**: Comprehensive exception handling with custom error types
- ⚙️ **Configurable**: Environment-based configuration management
- 📚 **Well documented**: Complete API reference and examples

## Installation

```bash
# Install from PyPI (when published)
pip install rag-api-client

# Install from source
git clone https://github.com/your-username/rag-api-client.git
cd rag-api-client
pip install -e .
```

## Quick Start

### 1. Configuration

Create a `.env` file or set environment variables:

```bash
cp .env.example .env
# Edit .env with your API details
```

```env
RAG_API_BASE_URL=http://localhost:8002
RAG_API_KEY=your-api-key-here
```

### 2. Basic Usage

```python
from rag_client import RAGClient

# Initialize the client
client = RAGClient()

# Create a folder
folder = client.create_folder("My Documents")
print(f"Created folder: {folder.id}")

# Upload files
uploaded_files = client.upload_files(
    folder_id=folder.id,
    file_paths=["document1.pdf", "document2.txt"]
)

# Search documents
results = client.search(
    folder_id=folder.id,
    query="What is the main topic?",
    prompt_type="agentic"
)

print(results.response)
```

### 3. Upload and Search in One Operation

```python
# Upload files and search immediately
result = client.upload_and_search(
    folder_id=folder.id,
    file_paths=["new_doc.pdf"],
    query="Summarize this document",
    prompt_type="agentic"
)

print(result.response)
```

## API Reference

### Client Initialization

```python
from rag_client import RAGClient

# Using environment variables
client = RAGClient()

# Using explicit configuration
client = RAGClient(
    base_url="http://localhost:8002",
    api_key="your-api-key"
)
```

### Folder Operations

```python
# Create folder
folder = client.create_folder("Folder Name", parent_id=None)

# Delete folder
client.delete_folder(folder_id="folder-id")
```

### File Operations

```python
# Upload individual files
files = client.upload_files(
    folder_id="folder-id",
    file_paths=["file1.pdf", "file2.txt"]
)

# Process directory
files = client.process_directory(
    folder_id="folder-id",
    directory_path="/path/to/directory"
)

# Delete file
client.delete_file(file_id="file-id")
```

### Search Operations

```python
# Basic search
results = client.search(
    folder_id="folder-id",
    query="your search query",
    prompt_type="agentic"  # or "consistency"
)

# Advanced search with filters
results = client.search(
    folder_id="folder-id",
    query="your search query",
    prompt_type="agentic",
    prefixes=["prefix1", "prefix2"],
    include_doc_ids=["doc1", "doc2"],
    exclude_doc_ids=["doc3"]
)

# Upload and search
result = client.upload_and_search(
    folder_id="folder-id",
    file_paths=["new_file.pdf"],
    query="analyze this document",
    prompt_type="agentic"
)
```

## Error Handling

The client includes comprehensive error handling:

```python
from rag_client.exceptions import (
    RAGAPIError,
    AuthenticationError,
    NotFoundError,
    ValidationError
)

try:
    folder = client.create_folder("Test Folder")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Validation error: {e}")
except RAGAPIError as e:
    print(f"API error: {e}")
```

## Examples

Check out the `examples/` directory for more detailed usage examples:

- [`examples/basic_usage.py`](examples/basic_usage.py) - Getting started
- [`examples/folder_management.py`](examples/folder_management.py) - Folder operations
- [`examples/file_operations.py`](examples/file_operations.py) - File handling
- [`examples/search_operations.py`](examples/search_operations.py) - Search functionality

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/rag-api-client.git
cd rag-api-client

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rag_client

# Run specific test file
pytest tests/test_client.py
```

### Code Quality

```bash
# Format code
black rag_client/ tests/ examples/

# Lint code
flake8 rag_client/ tests/ examples/

# Type checking
mypy rag_client/
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/your-username/rag-api-client/issues)
- 💬 [Discussions](https://github.com/your-username/rag-api-client/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes in each version.

---
