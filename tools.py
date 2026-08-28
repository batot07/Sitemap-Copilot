from collections import Counter
from typing import Any, Dict, List, Tuple


MAX_DEPTH_BY_ARCHETYPE = {
    "E-Commerce": 4,
    "B2B SaaS": 3,
    "Mobile App": 2,
    "Content": 3,
    "EdTech": 3,
    "Developer Platform": 3,
    "Fintech": 3,
    "Healthcare": 3,
}

MAX_BREADTH_BY_ARCHETYPE = {
    "E-Commerce": 8,
    "B2B SaaS": 6,
    "Mobile App": 5,
    "Content": 7,
    "EdTech": 6,
    "Developer Platform": 6,
    "Fintech": 6,
    "Healthcare": 6,
}

def _sanitize_text(value: str) -> str:
    if not value:
        return value
    return value.replace("\\'", "'").replace('\\"', '"')

def _get_nodes(ia: Any) -> list:
    if isinstance(ia, dict):
        return ia.get("nodes", [])
    return getattr(ia, "nodes", [])


def _get_archetype(ia: Any) -> str:
    if isinstance(ia, dict):
        return ia.get("archetype", "B2B SaaS")
    return getattr(ia, "archetype", "B2B SaaS")


def validate_root(nodes: list) -> list:
    errors = []
    root_nodes = [n for n in nodes if (getattr(n, "parent_id", None) if hasattr(n, "parent_id") else n.get("parent_id")) is None]
    if len(root_nodes) == 0:
        errors.append("No root node found (a node with parent_id = None).")
    elif len(root_nodes) > 1:
        errors.append(f"Multiple root nodes found ({len(root_nodes)}). Exactly 1 root allowed.")
    return errors


def validate_orphan_nodes(nodes: list) -> list:
    errors = []
    node_ids = {getattr(n, "id", None) if hasattr(n, "id") else n.get("id") for n in nodes}
    for n in nodes:
        parent_id = getattr(n, "parent_id", None) if hasattr(n, "parent_id") else n.get("parent_id")
        label = getattr(n, "label", "Unnamed") if hasattr(n, "label") else n.get("label", "Unnamed")
        if parent_id is not None and parent_id not in node_ids:
            errors.append(f"Orphan node '{label}': parent_id '{parent_id}' does not exist.")
    return errors


def validate_duplicate_routes(nodes: list) -> list:
    errors = []
    ids = [getattr(n, "id", None) if hasattr(n, "id") else n.get("id") for n in nodes]
    duplicates = [node_id for node_id, count in Counter(ids).items() if count > 1]
    if duplicates:
        errors.append(f"Duplicate node IDs found: {duplicates}")
    return errors


def validate_hierarchy_depth(nodes: list, archetype: str) -> list:
    errors = []
    max_depth = MAX_DEPTH_BY_ARCHETYPE.get(archetype, 3)
    for n in nodes:
        depth = getattr(n, "depth", 0) if hasattr(n, "depth") else n.get("depth", 0)
        label = getattr(n, "label", "Unnamed") if hasattr(n, "label") else n.get("label", "Unnamed")
        if depth > max_depth:
            errors.append(f"Node '{label}' exceeds maximum depth limit of {max_depth} for '{archetype}' (depth={depth}).")
    return errors


def validate_navigation_breadth(nodes: list, archetype: str) -> list:
    errors = []
    max_breadth = MAX_BREADTH_BY_ARCHETYPE.get(archetype, 6)
    level_1 = [n for n in nodes if (getattr(n, "depth", 0) if hasattr(n, "depth") else n.get("depth", 0)) == 1]
    if len(level_1) > max_breadth:
        errors.append(f"Excessive navigation breadth: '{archetype}' has {len(level_1)} top-level items (max allowed: {max_breadth}).")
    return errors


def validate_information_architecture(ia: Any) -> Dict[str, Any]:
    nodes = _get_nodes(ia)
    archetype = _get_archetype(ia)
    errors = []
    errors.extend(validate_root(nodes))
    errors.extend(validate_orphan_nodes(nodes))
    errors.extend(validate_duplicate_routes(nodes))
    errors.extend(validate_hierarchy_depth(nodes, archetype))
    errors.extend(validate_navigation_breadth(nodes, archetype))
    return {"valid": len(errors) == 0, "errors": errors}

def build_mermaid_from_nodes(ia: Any) -> str:
    """Deterministically builds Mermaid.js syntax from validated nodes,
    replacing anything the LLM tried to generate for mermaid_code."""
    nodes = _get_nodes(ia)
    lines = ["graph TD"]

    for n in nodes:
        node_id = getattr(n, "id", None) if hasattr(n, "id") else n.get("id")
        label = getattr(n, "label", None) if hasattr(n, "label") else n.get("label")
        label = _sanitize_text(label)
        safe_label = (label or "").replace('"', "'")
        lines.append(f'    {node_id}["{safe_label}"]')

    for n in nodes:
        node_id = getattr(n, "id", None) if hasattr(n, "id") else n.get("id")
        parent_id = getattr(n, "parent_id", None) if hasattr(n, "parent_id") else n.get("parent_id")
        if parent_id:
            lines.append(f"    {parent_id} --> {node_id}")

    return "\n".join(lines)


def export_markdown_spec(ia: Any) -> str:
    site_name = getattr(ia, "site_name", "App") if hasattr(ia, "site_name") else ia.get("site_name", "App")
    archetype = _get_archetype(ia)
    nodes = _get_nodes(ia)
    mermaid_code = getattr(ia, "mermaid_code", "") if hasattr(ia, "mermaid_code") else ia.get("mermaid_code", "")

    md = [
        f"# UX Specification: {site_name}",
        f"**Archetype:** {archetype}\n",
        "## Information Architecture & Page Hierarchy\n",
        "| ID | Label | Parent | Depth | Description | Rationale |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    for n in nodes:
        node_id = getattr(n, "id", "") if hasattr(n, "id") else n.get("id", "")
        label = getattr(n, "label", "") if hasattr(n, "label") else n.get("label", "")
        label = _sanitize_text(label)
        parent = getattr(n, "parent_id", None) if hasattr(n, "parent_id") else n.get("parent_id")
        depth = getattr(n, "depth", 0) if hasattr(n, "depth") else n.get("depth", 0)
        desc = getattr(n, "description", "") if hasattr(n, "description") else n.get("description", "")
        desc = _sanitize_text(desc) 
        rationale = getattr(n, "rationale", "N/A") if hasattr(n, "rationale") else n.get("rationale", "N/A")
        rationale = _sanitize_text(rationale)
        parent_str = f"`{parent}`" if parent else "*(Root)*"
        md.append(f"| `{node_id}` | **{label}** | {parent_str} | {depth} | {desc} | {rationale} |")

    md.append("\n## Mermaid Diagram\n")
    md.append(f"```mermaid\n{mermaid_code}\n```\n")
    return "\n".join(md)