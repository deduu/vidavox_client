import json
from vidavox_rag_client.client import RAGClient
from vidavox_rag_client.exceptions import NotFoundError
base_url = "http://localhost:8003"
api_key = "Z-OglNV8EinfVae9v66wxifSATdTr19-s2lLhafux9w"
# Initialize the client
client = RAGClient(base_url=base_url, api_key=api_key)

# folder = client.delete_folder_by_name("My Documents")
# print(f"Deleted folder: {folder.id}")

# # Create a folder
# folder = client.create_folder("My Documents")
# print(f"Created folder: {folder.id}")
# folder = client.create_folder("My Documents")
# print(f"Created folder: {folder.id}")
# # # Upload files
uploaded_files = client.upload_files_to_folder(
    folder_name="My Documents",
    file_paths=["./docs/NPWP PERUSAHAAN.pdf"]
)
print(f"Uploaded files: {uploaded_files}")
# # # List folders

# tree = client.get_folder_tree()
# # e.g. print(tree) → see: [{"id":"8572...", "name":"My Documents", "type":"folder", "children":[...]}, ...]
# print("Your folder tree:")
# print(json.dumps(tree, indent=2))


# tree = client.get_folder_tree()
# print("Your folder tree:")
# print(json.dumps(tree, indent=2))

# Delete files
# files = client.delete_files(
#     file_ids=["14772d42-ddd2-470b-b906-7f99052a51be",
#               "dfe27bb1-d8fc-4764-a0e7-ef3bc354e339"]
# )
# print(f"Files: {files}")


# print(f"Uploaded files: {uploaded_files}")

# # Search documents
# results = client.rag_search_in_folder(
#     folder_name="My Documents",
#     query="what is the introduction of the research paper?",
#     prompt_type="agentic"
# )

# print(results.to_dict())


client.close()
