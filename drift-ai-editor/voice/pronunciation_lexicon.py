import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

class PronunciationLexicon:
    """
    Persistent Pronunciation Dictionary:
    Allows overriding phonetic spelling for foreign philosopher names, scientific jargon,
    and acronyms once, ensuring consistent, flawless pronunciation across all video productions.
    """

    DEFAULT_RULES = {
        "Nietzsche": "Nit-che",
        "Schopenhauer": "Chopenráuer",
        "Marcus Aurelius": "Mar-cus Au-ré-li-us",
        "Epictetus": "Epictéto",
        "Seneca": "Sêneca",
        "Kierkegaard": "Kíer-kegor",
        "Heidegger": "Ráideguer",
        "AI": "Inteligência Artificial",
        "TTS": "Síntese de Voz",
        "NASA": "Náza"
    }

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            storage_path = Path(__file__).resolve().parent.parent / "storage" / "pronunciation_lexicon.json"
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.rules: Dict[str, str] = {}
        self._load()

    def _load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.rules = json.load(f)
            except Exception:
                self.rules = dict(self.DEFAULT_RULES)
        else:
            self.rules = dict(self.DEFAULT_RULES)
            self._save()

    def _save(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, indent=2, ensure_ascii=False)

    def add_rule(self, word_or_term: str, phonetic_spelling: str) -> None:
        """Adds or updates a persistent phonetic pronunciation rule."""
        self.rules[word_or_term.strip()] = phonetic_spelling.strip()
        self._save()

    def apply_to_text(self, text: str) -> str:
        """Substitutes terms in script text with their phonetic counterparts before TTS generation."""
        processed = text
        for term, phonetic in self.rules.items():
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            processed = pattern.sub(phonetic, processed)
        return processed

