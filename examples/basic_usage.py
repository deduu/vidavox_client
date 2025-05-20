from vidavox_rag_client.client import RAGClient

# Initialize the client
client = RAGClient()

# Create a folder
folder = client.create_folder("My Documents")
print(f"Created folder: {folder.id}")

# # Upload files
# uploaded_files = client.upload_files(
#     folder_id=folder.id,
#     file_paths=["document1.pdf", "document2.txt"]
# )

# # Search documents
# results = client.search(
#     folder_id=folder.id,
#     query="What is the main topic?",
#     prompt_type="agentic"
# )

# print(results.response)
