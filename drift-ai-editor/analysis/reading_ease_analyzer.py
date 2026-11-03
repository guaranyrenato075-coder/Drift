"""
Reading Ease & Cognitive Complexity Analyzer for CutWire Drift AI.
Evaluates narration scripts using the Flesch Reading Ease & Flesch-Kincaid Grade Level formulas,
estimating cognitive load, vocabulary complexity, and suitability for mass social media engagement.
"""
import re
from dataclasses import dataclass
from typing import List
from models.scene_plan import ProjectPlan

@dataclass
class ReadingEaseReport:
    total_words: int
    total_sentences: int
    total_syllables: int
    flesch_reading_ease: float     # 0 - 100 (higher = easier to understand, 60-80 optimal)
    flesch_kincaid_grade: float    # US school grade level (6-9 optimal for general public)
    reading_difficulty_label: str  # "Muito Fácil", "Padrão / Excelente", "Difícil / Acadêmico"
    is_optimal_for_retention: bool

class ReadingEaseAnalyzer:
    """
    Computes linguistic complexity metrics for video narrations.
    """

    @classmethod
    def count_syllables_in_word(cls, word: str) -> int:
        word = word.lower().strip(".,!?;:\"'()[]")
        if not word:
            return 1
        # Count vowel clusters
        vowels = "aeiouyáéíóúâêîôûãõà"
        count = 0
        in_vowel = False
        for char in word:
            if char in vowels:
                if not in_vowel:
                    count += 1
                    in_vowel = True
            else:
                in_vowel = False
        return max(1, count)

    @classmethod
    def analyze_text(cls, text: str) -> ReadingEaseReport:
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        total_sentences = max(1, len(sentences))
        words = [w.strip() for w in text.split() if w.strip()]
        total_words = max(1, len(words))

        total_syllables = sum(cls.count_syllables_in_word(w) for w in words)

        # Flesch Reading Ease: 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
        asl = total_words / total_sentences   # Average Sentence Length
        asw = total_syllables / total_words   # Average Syllables per Word

        fre = 206.835 - (1.015 * asl) - (84.6 * asw)
        fre = max(0.0, min(100.0, fre))

        # Flesch-Kincaid Grade Level: 0.39 * asl + 11.8 * asw - 15.59
        fkgl = (0.39 * asl) + (11.8 * asw) - 15.59
        fkgl = max(1.0, fkgl)

        if fre >= 70:
            label = "Muito Acessível / Dinâmico"
            optimal = True
        elif fre >= 50:
            label = "Padrão / Excelente"
            optimal = True
        else:
            label = "Complexo / Acadêmico"
            optimal = False

        return ReadingEaseReport(
            total_words=total_words,
            total_sentences=total_sentences,
            total_syllables=total_syllables,
            flesch_reading_ease=round(fre, 1),
            flesch_kincaid_grade=round(fkgl, 1),
            reading_difficulty_label=label,
            is_optimal_for_retention=optimal
        )

    @classmethod
    def analyze_project(cls, plan: ProjectPlan) -> ReadingEaseReport:
        full_text = " ".join(sc.narration_text for sc in plan.scenes if sc.narration_text)
        return cls.analyze_text(full_text)

