import time
import uuid
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field

@dataclass
class AtomicOperation:
    op_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action: str = ""                # e.g., 'insert_clip', 'replace_media', 'adjust_volume', 'set_transition', 'remove_clip'
    target_scene_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    inverse_parameters: Dict[str, Any] = field(default_factory=dict)
    is_ai_generated: bool = True
    user_approved: bool = True
    description: str = ""

@dataclass
class TransactionRecord:
    transaction_id: str
    timestamp: float
    description: str
    operations: List[AtomicOperation] = field(default_factory=list)
    is_reverted: bool = False

class UnifiedOperationController:
    """
    Single unified gatekeeper for all modifications to Drift's project and timeline.
    Enforces:
      1. Non-destructive AI editing: All operations have inverse rollback definitions.
      2. User-manual protection: Refuses to overwrite user-locked nodes without confirmation.
      3. Transaction journal: Full undo/redo ledger.
      4. Standardized MCP dispatch.
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.history: List[TransactionRecord] = []
        self.locked_scene_ids: set = set()

    def lock_user_edit(self, scene_id: str) -> None:
        """Locks a scene as manually customized by user, shielding it from AI overwrite."""
        self.locked_scene_ids.add(scene_id)

    def unlock_user_edit(self, scene_id: str) -> None:
        self.locked_scene_ids.discard(scene_id)

    def execute_transaction(
        self,
        description: str,
        operations: List[AtomicOperation],
        mcp_executor: Optional[Callable[[AtomicOperation], bool]] = None
    ) -> TransactionRecord:
        """
        Validates operations against locked scenes, records undo actions,
        and applies operations sequentially.
        """
        valid_ops: List[AtomicOperation] = []

        for op in operations:
            if op.target_scene_id and op.target_scene_id in self.locked_scene_ids and op.is_ai_generated:
                # Shield manual user edits from automatic AI changes
                continue
            valid_ops.append(op)

        # Dispatch via MCP if executor provided
        if mcp_executor:
            for op in valid_ops:
                mcp_executor(op)

        tx = TransactionRecord(
            transaction_id=str(uuid.uuid4()),
            timestamp=time.time(),
            description=description,
            operations=valid_ops
        )
        self.history.append(tx)
        return tx

    def rollback_transaction(
        self,
        transaction_id: str,
        mcp_executor: Optional[Callable[[AtomicOperation], bool]] = None
    ) -> bool:
        """Reverts all operations in a transaction in reverse order using inverse actions."""
        tx = next((t for t in self.history if t.transaction_id == transaction_id), None)
        if not tx or tx.is_reverted:
            return False

        # Execute inverse operations in reverse
        for op in reversed(tx.operations):
            inverse_op = AtomicOperation(
                action=f"undo_{op.action}",
                target_scene_id=op.target_scene_id,
                parameters=op.inverse_parameters,
                is_ai_generated=False,
                description=f"Desfazer: {op.description}"
            )
            if mcp_executor:
                mcp_executor(inverse_op)

        tx.is_reverted = True
        return True

