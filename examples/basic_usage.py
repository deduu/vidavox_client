import json
from vidavox_rag_client.client import RAGClient
from vidavox_rag_client.exceptions import NotFoundError


# Get the api key from your RAG API account
api_key = ".."

# Initialize the client
client = RAGClient(api_key=api_key)

# Create a folder
folder = client.create_folder("My Docs")
print(f"Created folder: {folder.id}")

#  Upload files
uploaded_files = client.upload_files_to_folder(
    folder_name="My Docs",
    file_paths=["./docs/Journal.pdf"]
)
print(f"Uploaded files: {uploaded_files}")

# # # # # List folders

tree = client.get_folder_tree()
# e.g. print(tree) → see: [{"id":"8572...", "name":"My Documents", "type":"folder", "children":[...]}, ...]
print("Your folder tree:")
print(json.dumps(tree, indent=2))

# Create a folder
folder = client.create_folder("My Docs")
print(f"Created folder: {folder.id}")

# file_ids_all = client.get_file_ids_in_folder_by_name(
#     "Test",
#     recursive=True
# )
# print(file_ids_all)

# deleted = client.delete_files(
#     file_ids=file_ids_all,
#     raise_on_error=False
# )

# tree = client.get_folder_tree()
# print("Your folder tree:")
# print(json.dumps(tree, indent=2))

# Delete files
# files = client.delete_files(
#     file_ids=["14772d42-ddd2-470b-b906-7f99052a51be",
#               "dfe27bb1-d8fc-4764-a0e7-ef3bc354e339"]
# )
# print(f"Files: {files}")


# # Search documents
# results = client.rag_search_in_folder(
#     folder_name="My Documents",
#     query="what is the introduction of the research paper?",
#     prompt_type="agentic"
# )

# print(results.to_dict())


client.close()
