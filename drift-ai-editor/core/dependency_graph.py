import uuid
import time
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field

@dataclass
class DependencyNode:
    node_id: str                      # Permanent immutable ID (e.g., scene UUID)
    node_type: str                    # 'scene', 'audio', 'video_asset', 'caption', 'sfx', 'timeline_clip'
    label: str                        # Human readable description
    data: Dict[str, Any] = field(default_factory=dict)
    is_dirty: bool = False            # True if upstream dependency changed and recalculation is needed
    user_locked: bool = False         # If True, manual user edits protect this node from AI overwrite
    updated_at: float = field(default_factory=time.time)

class ProjectDependencyGraph:
    """
    Project Dependency Graph:
    Maintains a Directed Acyclic Graph (DAG) of all project assets, scene IDs,
    voice tracks, video clips, and timeline placements.
    Enables:
      1. Permanent scene identity across timeline shifts.
      2. Pinpoint dirty recalculations when only one sentence changes.
      3. Missing asset impact analysis (showing exactly where a deleted file is used).
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.nodes: Dict[str, DependencyNode] = {}
        # adjacency: node_id -> set of downstream dependent node_ids
        self._downstream: Dict[str, Set[str]] = {}
        # reverse adjacency: node_id -> set of upstream prerequisite node_ids
        self._upstream: Dict[str, Set[str]] = {}

    def add_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        data: Optional[Dict[str, Any]] = None,
        user_locked: bool = False
    ) -> DependencyNode:
        node = DependencyNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            data=data or {},
            user_locked=user_locked
        )
        self.nodes[node_id] = node
        if node_id not in self._downstream:
            self._downstream[node_id] = set()
        if node_id not in self._upstream:
            self._upstream[node_id] = set()
        return node

    def add_dependency(self, upstream_id: str, downstream_id: str) -> None:
        """Indicates that downstream_id depends on upstream_id."""
        if upstream_id not in self.nodes or downstream_id not in self.nodes:
            return
        self._downstream[upstream_id].add(downstream_id)
        self._upstream[downstream_id].add(upstream_id)

    def mark_dirty(self, node_id: str) -> List[str]:
        """
        Recursively invalidates node_id and all its downstream dependents.
        Returns list of invalidated node IDs (excluding user-locked nodes).
        """
        affected = []
        stack = [node_id]
        while stack:
            curr = stack.pop()
            if curr in self.nodes:
                node = self.nodes[curr]
                if not node.user_locked:
                    node.is_dirty = True
                    affected.append(curr)
                # Recurse down
                for d in self._downstream.get(curr, set()):
                    if d not in affected:
                        stack.append(d)
        return affected

    def query_file_impact(self, file_path: str) -> List[DependencyNode]:
        """
        Pinpoints every scene, clip, or track in the project that relies on a specific file.
        Useful when an asset is missing or deleted from disk.
        """
        clean_path = str(file_path).replace("\\", "/").lower()
        impacted: List[DependencyNode] = []
        for node in self.nodes.values():
            node_path = str(node.data.get("file_path", "")).replace("\\", "/").lower()
            if node_path == clean_path:
                impacted.append(node)
                # Collect dependent timeline clips
                for down_id in self._downstream.get(node.node_id, set()):
                    if down_id in self.nodes and self.nodes[down_id] not in impacted:
                        impacted.append(self.nodes[down_id])
        return impacted

    def get_dirty_nodes(self) -> List[DependencyNode]:
        """Returns all nodes that require recalculation."""
        return [n for n in self.nodes.values() if n.is_dirty]

    def clear_dirty(self, node_id: str) -> None:
        if node_id in self.nodes:
            self.nodes[node_id].is_dirty = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "nodes": {
                k: {
                    "node_id": v.node_id,
                    "node_type": v.node_type,
                    "label": v.label,
                    "is_dirty": v.is_dirty,
                    "user_locked": v.user_locked,
                    "data": v.data
                }
                for k, v in self.nodes.items()
            },
            "edges": [
                {"from": up, "to": down}
                for up, downs in self._downstream.items()
                for down in downs
            ]
        }

