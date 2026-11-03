"""
Context Pruner & Sliding Window Engine for CutWire Drift AI Agents.
Prevents context window bloat and memory spikes when communicating with LLMs
by pruning stale chat turns, compacting tool responses, and distilling memory capsules.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ChatTurn:
    role: str       # "user", "assistant", "system", "tool"
    content: str
    token_estimate: int = 0

@dataclass
class PrunedContext:
    messages: List[Dict[str, str]]
    total_tokens_estimated: int
    pruned_turns_count: int
    memory_capsule: Optional[str]

class ContextPruner:
    """
    Manages sliding window pruning and token budget enforcement for AI agents.
    """

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        # Standard fast approximation: ~4 characters per token
        return max(1, len(text) // 4)

    @classmethod
    def strip_tool_bloat(cls, raw_content: str, max_chars: int = 350) -> str:
        """
        Strips oversized JSON blobs, raw vector embeddings, or base64 data from tool outputs.
        """
        if len(raw_content) <= max_chars:
            return raw_content
        return raw_content[:max_chars] + f"... [Truncated {len(raw_content) - max_chars} chars of tool payload]"

    @classmethod
    def prune_history(
        cls,
        history: List[Dict[str, str]],
        max_turns: int = 8,
        max_token_budget: int = 2500,
        system_prompt: Optional[str] = None
    ) -> PrunedContext:
        """
        Executes a sliding window over conversation history:
        1. Always preserves the system prompt at index 0.
        2. Preserves the most recent N turns.
        3. Compacts older discarded turns into a single summary memory capsule.
        """
        if not history:
            msgs = [{"role": "system", "content": system_prompt}] if system_prompt else []
            return PrunedContext(msgs, cls.estimate_tokens(system_prompt or ""), 0, None)

        turns = []
        for item in history:
            content = item.get("content", "")
            role = item.get("role", "user")
            # If it's a tool output, prune bloated payload
            if role == "tool":
                content = cls.strip_tool_bloat(content)
            turns.append(ChatTurn(role=role, content=content, token_estimate=cls.estimate_tokens(content)))

        # If history exceeds max_turns, slice most recent turns
        pruned_count = 0
        memory_summary = None
        if len(turns) > max_turns:
            discarded = turns[:-max_turns]
            turns = turns[-max_turns:]
            pruned_count = len(discarded)
            # Build memory capsule of discarded turns
            topics = [f"{t.role}: {t.content[:40]}..." for t in discarded if t.role == "user"]
            if topics:
                memory_summary = f"[Memória de Contexto Anterior: {'; '.join(topics)}]"

        # Check token budget from newest to oldest
        final_turns: List[ChatTurn] = []
        accumulated_tokens = 0
        sys_tokens = cls.estimate_tokens(system_prompt) if system_prompt else 0
        budget_left = max_token_budget - sys_tokens

        for t in reversed(turns):
            if accumulated_tokens + t.token_estimate <= budget_left:
                final_turns.insert(0, t)
                accumulated_tokens += t.token_estimate
            else:
                pruned_count += 1

        result_messages: List[Dict[str, str]] = []
        if system_prompt:
            result_messages.append({"role": "system", "content": system_prompt})
        if memory_summary:
            result_messages.append({"role": "system", "content": memory_summary})
        for ft in final_turns:
            result_messages.append({"role": ft.role, "content": ft.content})

        total_est = sum(cls.estimate_tokens(m["content"]) for m in result_messages)

        return PrunedContext(
            messages=result_messages,
            total_tokens_estimated=total_est,
            pruned_turns_count=pruned_count,
            memory_capsule=memory_summary
        )

