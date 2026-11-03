import re
from typing import List, Tuple
from models.scene_plan import Scene, SceneState

class ScriptSegmenter:
    """
    Parses scripts into structured scenes. Supports both structured
    format (CENA 01 / NARRAÇÃO / DESCRIÇÃO VISUAL) and continuous raw text.
    """

    # Regex patterns for structured script tags
    SCENE_HEADER_PATTERN = re.compile(r'^\s*(?:CENA|SCENE)\s*(\d+)?\b', re.IGNORECASE)
    NARRATION_PATTERN = re.compile(r'^\s*(?:NARRAÇÃO|NARRACAO|NARRAÇAO|VOZ|FALA|SPEECH|VOICEOVER)\s*:\s*(.*)', re.IGNORECASE)
    VISUAL_PATTERN = re.compile(r'^\s*(?:DESCRIÇÃO\s*VISUAL|DESCRICAO\s*VISUAL|VISUAL|CENA\s*VISUAL|IMAGEM|VIDEO)\s*:\s*(.*)', re.IGNORECASE)
    DURATION_PATTERN = re.compile(r'^\s*(?:DURAÇÃO|DURACAO|DURATION|TEMPO)\s*:\s*(.*)', re.IGNORECASE)

    # Sentence boundary regex for continuous text
    SENTENCE_END_PATTERN = re.compile(r'(?<=[.!?…])\s+(?=[A-ZÀ-Ú"\'\d])')

    @classmethod
    def is_structured(cls, script_text: str) -> bool:
        """Determines if the text follows the structured scene format."""
        lines = script_text.splitlines()
        structured_matches = 0
        for line in lines:
            line_s = line.strip()
            if cls.SCENE_HEADER_PATTERN.match(line_s) or cls.NARRATION_PATTERN.match(line_s):
                structured_matches += 1
                if structured_matches >= 2:
                    return True
        return False

    @classmethod
    def parse(cls, script_text: str, default_language: str = "pt", default_voice: str = "default") -> List[Scene]:
        """
        Parses script text into a list of Scene objects.
        """
        script_text = script_text.strip()
        if not script_text:
            return []

        if cls.is_structured(script_text):
            return cls._parse_structured(script_text, default_language, default_voice)
        else:
            return cls._parse_continuous(script_text, default_language, default_voice)

    @classmethod
    def _parse_structured(cls, script_text: str, language: str, voice_id: str) -> List[Scene]:
        scenes: List[Scene] = []
        blocks = re.split(r'(?i)^\s*(?:CENA|SCENE)\s*\d*.*$', script_text, flags=re.MULTILINE)
        
        # If headers were matched, the first element might be text before CENA 01
        header_matches = list(cls.SCENE_HEADER_PATTERN.finditer(script_text))
        
        current_scene: Scene | None = None
        current_order = 1

        lines = script_text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            header_match = cls.SCENE_HEADER_PATTERN.match(line)
            if header_match:
                if current_scene and current_scene.narration_text.strip():
                    scenes.append(current_scene)
                current_scene = Scene(
                    order=current_order,
                    language=language,
                    voice_id=voice_id,
                    state=SceneState.PENDING
                )
                current_order += 1
                i += 1
                continue

            narration_match = cls.NARRATION_PATTERN.match(line)
            if narration_match:
                if current_scene is None:
                    current_scene = Scene(order=current_order, language=language, voice_id=voice_id)
                    current_order += 1
                
                content = [narration_match.group(1).strip()]
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if (cls.SCENE_HEADER_PATTERN.match(next_line) or 
                        cls.NARRATION_PATTERN.match(next_line) or 
                        cls.VISUAL_PATTERN.match(next_line) or 
                        cls.DURATION_PATTERN.match(next_line)):
                        break
                    if next_line:
                        content.append(next_line)
                    i += 1
                current_scene.narration_text = " ".join(content)
                continue

            visual_match = cls.VISUAL_PATTERN.match(line)
            if visual_match:
                if current_scene is None:
                    current_scene = Scene(order=current_order, language=language, voice_id=voice_id)
                    current_order += 1
                
                content = [visual_match.group(1).strip()]
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if (cls.SCENE_HEADER_PATTERN.match(next_line) or 
                        cls.NARRATION_PATTERN.match(next_line) or 
                        cls.VISUAL_PATTERN.match(next_line) or 
                        cls.DURATION_PATTERN.match(next_line)):
                        break
                    if next_line:
                        content.append(next_line)
                    i += 1
                current_scene.visual_description = " ".join(content)
                continue

            duration_match = cls.DURATION_PATTERN.match(line)
            if duration_match:
                dur_str = duration_match.group(1).strip()
                # Check if it has a numeric value like "5s" or "5.2"
                num_match = re.search(r'(\d+(?:\.\d+)?)', dur_str)
                if num_match and "auto" not in dur_str.lower():
                    if current_scene:
                        current_scene.duration = float(num_match.group(1))
                i += 1
                continue

            # Fallback text inside an existing scene block
            if current_scene and not current_scene.narration_text:
                current_scene.narration_text = line
            i += 1

        if current_scene and (current_scene.narration_text.strip() or current_scene.visual_description.strip()):
            scenes.append(current_scene)

        # Normalize indices
        for idx, s in enumerate(scenes, 1):
            s.order = idx

        return scenes

    @classmethod
    def _parse_continuous(cls, script_text: str, language: str, voice_id: str) -> List[Scene]:
        """
        Breaks continuous prose into balanced, semantically sound scenes.
        """
        scenes: List[Scene] = []
        # Split by blank lines (paragraphs) first
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', script_text) if p.strip()]

        current_order = 1
        for paragraph in paragraphs:
            # Within each paragraph, split into complete sentences
            sentences = cls.SENTENCE_END_PATTERN.split(paragraph)
            for sentence in sentences:
                sentence_clean = sentence.strip()
                if not sentence_clean:
                    continue

                scene = Scene(
                    order=current_order,
                    narration_text=sentence_clean,
                    language=language,
                    voice_id=voice_id,
                    state=SceneState.PENDING
                )
                scenes.append(scene)
                current_order += 1

        return scenes

