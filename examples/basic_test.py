import json
import sys
import time
from pathlib import Path

from vidavox_rag_client.client import RAGClient
from vidavox_rag_client.exceptions import NotFoundError, RAGAPIError

# ── EDIT THIS ──
base_url = "http://34.27.153.226:8003"   # Your RAG API base URL
api_key = "TE-kWiL2XUpCvtlgLXEl0TMcFA9Oe-9rqSakG_dEUr8"  # Your API key

# Make sure these files actually exist on disk before running.
file1 = "./docs/PACKING LIST.pdf"
file2 = "./docs/Journal.pdf"

# Name of the folder we'll create and later delete
test_folder_name = "My Doc"


def main():
    client = RAGClient(base_url=base_url, api_key=api_key, timeout=120)

    try:
        print("▶ 1) Attempting to create folder:", test_folder_name)
        try:
            folder = client.create_folder(test_folder_name)
            print(
                f"    • Folder created: ID = {folder.id}, name = {folder.name}")
        except RAGAPIError as e:
            # If the folder already exists, you might get a ValidationError or some other error.
            # In that case, fetch the existing one by name instead of failing.
            print("    • Could not create folder (maybe it already exists):", str(e))
            existing_id = client.find_folder_id(test_folder_name)
            if existing_id:
                print(
                    f"    • Found existing folder '{test_folder_name}' with ID = {existing_id}")
                folder = type(
                    "Dummy", (), {"id": existing_id, "name": test_folder_name})
            else:
                print("    • Folder not found in tree; re-raising.")
                raise

        print("\n▶ 2) Listing full folder tree:")
        tree = client.get_folder_tree()
        print(json.dumps(tree, indent=2))

        print(f"\n▶ 3) Uploading files into '{test_folder_name}':")
        # Make sure the files exist
        for path in (file1, file2):
            if not Path(path).exists():
                print(f"    ✖ File not found on disk: {path}")
                print("    Please correct the file paths and re-run.")
                client.close()
                sys.exit(1)

        try:
            upload_resp = client.upload_files_to_folder(
                folder_name=test_folder_name,
                file_paths=[file1, file2]
            )
            print("    • UploadResponse:", upload_resp.to_dict()
                  if hasattr(upload_resp, "to_dict") else upload_resp)
        except Exception as e:
            print("    ✖ Error during upload:", str(e))
            client.close()
            sys.exit(1)

        # Small pause in case indexing happens asynchronously on the server side
        time.sleep(1)

        print(
            f"\n▶ 4) Fetching file IDs in '{test_folder_name}' (non-recursive):")
        try:
            # Non-recursive: immediate children only
            file_ids_immediate = client.get_file_ids_in_folder_by_name(
                test_folder_name,
                recursive=False
            )
            print("    • Immediate file IDs:", file_ids_immediate)

            print(
                f"\n▶ 5) Fetching file IDs in '{test_folder_name}' (recursive):")
            file_ids_all = client.get_file_ids_in_folder_by_name(
                test_folder_name,
                recursive=True
            )
            print("    • All nested file IDs:", file_ids_all)

        except NotFoundError as e:
            print("    ✖ Could not find folder to list files:", str(e))
            client.close()
            sys.exit(1)

        print(f"\n▶ 6) Performing a RAG search in '{test_folder_name}':")
        try:
            results = client.rag_search_in_folder(
                folder_name=test_folder_name,
                query="What is the introduction of this paper?",
                top_k=5,
                threshold=0.4,
                prompt_type="agentic"
            )
            # Assuming SearchResponse has a to_dict() or similar
            print("    • RAG search results:")
            if hasattr(results, "to_dict"):
                print(json.dumps(results.to_dict(), indent=2))
            else:
                print(results)
        except Exception as e:
            print("    ✖ Error during RAG search:", str(e))

        print(f"\n▶ 7) Deleting the uploaded files in bulk:")
        try:
            # Use file_ids_all (all nested) for deletion
            delete_results = client.delete_files(
                file_ids_all, raise_on_error=False)
            print("    • Delete results (per file):", delete_results)
        except Exception as e:
            print("    ✖ Error during bulk delete:", str(e))

        print(f"\n▶ 8) Deleting folder by name: '{test_folder_name}'")
        try:
            client.delete_folder_by_name(test_folder_name)
            print(f"    • Folder '{test_folder_name}' deleted successfully.")
        except NotFoundError:
            print(
                f"    • Folder '{test_folder_name}' not found (maybe already deleted).")
        except Exception as e:
            print("    ✖ Error deleting folder:", str(e))

        print(
            f"\n▶ 9) Attempting to delete '{test_folder_name}' a second time (should catch NotFoundError):")
        try:
            client.delete_folder_by_name(test_folder_name)
            print("    • (Unexpected) second-time delete succeeded.")
        except NotFoundError:
            print(
                f"    • As expected, folder '{test_folder_name}' no longer exists.")
        except Exception as e:
            print("    ✖ Error on second-time delete:", str(e))

    finally:
        client.close()
        print("\n✔ All done. Client session closed.")


if __name__ == "__main__":
    main()
