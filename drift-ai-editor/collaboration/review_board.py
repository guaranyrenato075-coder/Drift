"""
Review Board & Timecoded Comments Manager for CutWire Drift AI.
Collects review feedback tied to specific timeline timestamps,
and automatically parses comments into actionable AI Director revision tasks.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
import time
import uuid

class TaskType(str, Enum):
    SWAP_MEDIA = "swap_media"
    FIX_CAPTION = "fix_caption"
    ADJUST_VOLUME = "adjust_volume"
    TRIM_SCENE = "trim_scene"
    CHANGE_PACING = "change_pacing"
    GENERAL_NOTE = "general_note"

@dataclass
class ReviewComment:
    comment_id: str
    author: str
    timestamp_seconds: float
    text: str
    created_at: float = field(default_factory=time.time)
    is_resolved: bool = False

@dataclass
class DirectorRevisionTask:
    task_id: str
    source_comment_id: str
    timestamp_seconds: float
    task_type: TaskType
    action_prompt: str
    status: str = "pending"  # "pending", "in_progress", "completed", "rejected"

class ReviewBoard:
    """
    Manages reviewer comments and compiles them into execution directives.
    """

    def __init__(self):
        self.comments: List[ReviewComment] = []
        self.tasks: List[DirectorRevisionTask] = []

    def add_comment(self, author: str, timestamp_seconds: float, text: str) -> ReviewComment:
        c = ReviewComment(
            comment_id=str(uuid.uuid4())[:8],
            author=author,
            timestamp_seconds=round(timestamp_seconds, 2),
            text=text
        )
        self.comments.append(c)
        # Automatically derive task
        derived = self._parse_to_task(c)
        if derived:
            self.tasks.append(derived)
        return c

    def _parse_to_task(self, comment: ReviewComment) -> Optional[DirectorRevisionTask]:
        t = comment.text.lower()
        task_type = TaskType.GENERAL_NOTE
        action = comment.text

        if any(w in t for w in ["trocar imagem", "mudar vídeo", "swap", "trocar foto", "mudar mídia"]):
            task_type = TaskType.SWAP_MEDIA
            action = f"Replace visual media at {comment.timestamp_seconds}s per comment: '{comment.text}'"
        elif any(w in t for w in ["legenda", "ortografia", "erro de português", "typo", "subtitles"]):
            task_type = TaskType.FIX_CAPTION
            action = f"Fix caption around {comment.timestamp_seconds}s: '{comment.text}'"
        elif any(w in t for w in ["volume", "música alta", "baixo", "áudio estourando"]):
            task_type = TaskType.ADJUST_VOLUME
            action = f"Adjust audio balance at {comment.timestamp_seconds}s: '{comment.text}'"
        elif any(w in t for w in ["cortar", "encurtar", "muito longo", "trim"]):
            task_type = TaskType.TRIM_SCENE
            action = f"Trim scene duration around {comment.timestamp_seconds}s: '{comment.text}'"

        return DirectorRevisionTask(
            task_id=f"rev_{comment.comment_id}",
            source_comment_id=comment.comment_id,
            timestamp_seconds=comment.timestamp_seconds,
            task_type=task_type,
            action_prompt=action
        )

    def mark_resolved(self, comment_id: str):
        for c in self.comments:
            if c.comment_id == comment_id:
                c.is_resolved = True
        for t in self.tasks:
            if t.source_comment_id == comment_id:
                t.status = "completed"

