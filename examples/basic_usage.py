import json
from vidavox_rag_client.client import RAGClient
from vidavox_rag_client.exceptions import NotFoundError, RAGAPIError

API_KEY = "YOUR_API_KEY_HERE"
client = RAGClient(api_key=API_KEY)

try:
    # ──────── 1) CREATE A FOLDER ─────────
    folder_name = "My Docs"
    folder = client.create_folder(folder_name)
    print(f"🗂 Created folder '{folder_name}' (id={folder.id})")

    # ──────── 2) UPLOAD FILES ────────────
    file_paths = ["./docs/Journal.pdf"]
    upload_resp = client.upload_files_to_folder(folder_name, file_paths)
    print(
        f"📤 Uploaded {upload_resp.total_uploaded} file(s) to '{folder_name}':")
    for result in upload_resp.results:
        name = result.file.name if result.file else "<unknown>"
        status = "OK" if result.success else f"ERROR ({result.error})"
        print(f"   • {name}: {status}")

    # ──────── 3) INSPECT FOLDERS ─────────
    tree = client.get_folder_tree()
    print("\n🌳 Full folder tree:")
    print(json.dumps(tree, indent=2))

    nested = client.list_folder_names()
    print("\n📁 Folder names (nested):")
    print(json.dumps(nested, indent=2))

    # ──────── 4) DELETE BY NAME ──────────
    try:
        deleted_folders = client.delete_folders_by_names(["My Doc"])
        print(f"\n🗑 Deleted folders: {deleted_folders}")
    except NotFoundError as e:
        print(f"\n⚠️  Could not delete folder: {e}")

    try:
        deleted_files = client.delete_files_by_names(
            "My Docs", ["AR for improved learnability.pdf"])
        print(f"\n🗑 Deleted files in '{folder_name}': {deleted_files}")
    except NotFoundError as e:
        print(f"\n⚠️  Could not delete file: {e}")

    # ──────── 5) BULK DELETE ALL FILES ───
    file_ids = client.get_file_ids_in_folder_by_name(
        folder_name, recursive=True)
    results = client.delete_files(file_ids=file_ids, raise_on_error=False)
    print(f"\n🗑 Bulk delete results in '{folder_name}': {results}")

    # ──────── 6) FINAL STATE ─────────────
    final_tree = client.get_folder_tree()
    print("\n🌳 Final folder tree:")
    print(json.dumps(final_tree, indent=2))


except RAGAPIError as e:
    print(f"\n❌ API error: {e}")
finally:
    client.close()
