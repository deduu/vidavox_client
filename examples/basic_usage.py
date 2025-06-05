import json
from vidavox_rag_client.client import RAGClient
from vidavox_rag_client.exceptions import NotFoundError
base_url = "http://localhost:8002"
api_key = "TE-kWiL2XUpCvtlgLXEl0TMcFA9Oe-9rqSakG_dEUr8"
# Initialize the client
client = RAGClient(base_url=base_url, api_key=api_key)

# Create a folder
# folder = client.create_folder("My Documents")
# print(f"Created folder: {folder.id}")

# Upload files
# uploaded_files = client.upload_files_to_folder(
#     folder_name="My Documents",
#     file_paths=["./docs/PACKING LIST.pdf", "./docs/Journal.pdf"]
# )
# List folders
tree = client.get_folder_tree()
# e.g. print(tree) → see: [{"id":"8572...", "name":"My Documents", "type":"folder", "children":[...]}, ...]
print("Your folder tree:")
print(json.dumps(tree, indent=2))
# Delete folder
folders = client.delete_folder_by_name("My Documents")
print(f"Folders: {folders}")


# Delete files
# files = client.delete_files(
#     file_ids=["ef15ffb3-3e54-4484-a7fd-171ceb1b1833",
#               "caf37089-afe0-40ba-92d2-427a2555c7a2"]
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
