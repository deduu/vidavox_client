from typing import List, Dict, Any, Optional


def _find_folder_node_by_id(
    nodes: List[Dict[str, Any]],
    target_id: str
) -> Optional[Dict[str, Any]]:
    for node in nodes:
        # Only fold a folder match if the ID matches and type is "folder"
        if node.get("id") == target_id and node.get("type") == "folder":
            return node
        children = node.get("children", [])
        if children:
            found = _find_folder_node_by_id(children, target_id)
            if found:
                return found
    return None


def _collect_immediate_file_ids(folder_node: Dict[str, Any]) -> List[str]:
    file_ids: List[str] = []
    for child in folder_node.get("children", []):
        if child.get("type") == "file":
            file_ids.append(child.get("id"))
    return file_ids


def _collect_all_file_ids_recursive(folder_node: Dict[str, Any]) -> List[str]:
    collected: List[str] = []

    def _recurse(node: Dict[str, Any]):
        if node.get("type") == "file":
            collected.append(node.get("id"))
            return
        if node.get("type") == "folder":
            for child in node.get("children", []):
                _recurse(child)

    _recurse(folder_node)
    return collected


def _find_folder_id(
    nodes: List[Dict[str, Any]],
    target_name: str
) -> Optional[str]:
    """
    Recursively search a list of TreeNode dicts for a folder whose 'name' matches target_name.
    Returns the 'id' string if found, else None.
    """
    for node in nodes:
        # Only consider nodes of type "folder"
        if node.get("type") == "folder" and node.get("name") == target_name:
            return node.get("id")
        # Recurse into children regardless of type (in case folders are nested)
        children = node.get("children", [])
        if children:
            found = _find_folder_id(children, target_name)
            if found:
                return found
    return None
