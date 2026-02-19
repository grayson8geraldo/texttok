"""Transforms text to meet TikTok platform requirements while preserving meaning."""

import random
import re

from . import rules
from .analyzer import AnalysisReport, TextAnalyzer


class TextTransformer:
    """Transforms input text into TikTok-optimized format."""

    def __init__(self):
        self.analyzer = TextAnalyzer()

    def optimize(self, text: str, topic: str = "default") -> dict:
        """Optimize text for TikTok.

        Returns a dict with:
            - original: the original text
            - optimized: the optimized text
            - before_report: analysis of the original
            - after_report: analysis of the result
        """
        before_report = self.analyzer.analyze(text)
        language = before_report.language

        result = text

        # Step 1: Simplify complex phrases
        result = self._simplify_phrases(result, language)

        # Step 2: Break long sentences
        result = self._break_long_sentences(result, language)

        # Step 3: Add line breaks for readability
        result = self._add_line_breaks(result)

        # Step 4: Add hook if missing
        if not before_report.has_hook:
            result = self._add_hook(result, language)

        # Step 5: Add CTA if missing
        if not before_report.has_cta:
            result = self._add_cta(result, language)

        # Step 6: Add emojis if missing
        if before_report.emoji_count == 0:
            result = self._add_emojis(result)

        # Step 7: Add hashtags if insufficient
        if before_report.hashtag_count < rules.HASHTAGS_MIN:
            needed = rules.HASHTAGS_MIN - before_report.hashtag_count
            result = self._add_hashtags(result, topic, needed, before_report.existing_hashtags)

        # Step 8: Trim if too long
        result = self._trim_to_limit(result)

        # Clean up whitespace
        result = self._clean_whitespace(result)

        after_report = self.analyzer.analyze(result)

        return {
            "original": text,
            "optimized": result,
            "before_report": before_report,
            "after_report": after_report,
        }

    def _simplify_phrases(self, text: str, language: str) -> str:
        simplify_map = rules.SIMPLIFY_MAP_RU if language == "ru" else rules.SIMPLIFY_MAP_EN
        result = text
        for complex_phrase, simple_phrase in simplify_map.items():
            pattern = re.compile(re.escape(complex_phrase), re.IGNORECASE)
            result = pattern.sub(simple_phrase, result)
        return result

    def _break_long_sentences(self, text: str, language: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        result_sentences = []

        for sentence in sentences:
            words = sentence.split()
            if len(words) > rules.SENTENCE_MAX_WORDS:
                # Try to split at conjunctions
                if language == "ru":
                    split_words = [
                        "который", "которая", "которое", "которые",
                        "потому что", "поэтому", "однако", "но",
                        "а также", "при этом", "причём", "когда",
                        "где", "хотя", "если", "так как",
                    ]
                else:
                    split_words = [
                        "which", "because", "however", "but",
                        "although", "while", "when", "where",
                        "since", "therefore", "moreover", "and",
                    ]

                broken = self._split_at_conjunction(sentence, split_words)
                result_sentences.extend(broken)
            else:
                result_sentences.append(sentence)

        return " ".join(result_sentences)

    def _split_at_conjunction(self, sentence: str, conjunctions: list) -> list:
        best_split = None
        best_balance = float("inf")
        words = sentence.split()
        total = len(words)

        for conj in conjunctions:
            conj_words = conj.split()
            conj_len = len(conj_words)
            for i in range(1, total - conj_len):
                segment = " ".join(words[i : i + conj_len]).lower()
                if segment == conj:
                    balance = abs((total / 2) - i)
                    if balance < best_balance:
                        best_balance = balance
                        best_split = i

        if best_split and best_split > 2:
            part1 = " ".join(words[:best_split]).rstrip(",;:")
            if not part1.endswith((".", "!", "?")):
                part1 += "."
            part2 = " ".join(words[best_split:])
            # Capitalize first letter of second part
            if part2:
                part2 = part2[0].upper() + part2[1:]
            return [part1, part2]

        # Fallback: split roughly in half
        mid = total // 2
        part1 = " ".join(words[:mid]).rstrip(",;:")
        if not part1.endswith((".", "!", "?")):
            part1 += "."
        part2 = " ".join(words[mid:])
        if part2:
            part2 = part2[0].upper() + part2[1:]
        return [part1, part2]

    def _add_line_breaks(self, text: str) -> str:
        # Don't re-add if already has breaks
        if "\n" in text:
            return text

        sentences = re.split(r"(?<=[.!?])\s+", text)
        if len(sentences) <= 2:
            return text

        lines = []
        current_line = []
        for sentence in sentences:
            current_line.append(sentence)
            if len(current_line) >= rules.OPTIMAL_SENTENCES_PER_PARAGRAPH:
                lines.append(" ".join(current_line))
                current_line = []
        if current_line:
            lines.append(" ".join(current_line))

        return "\n\n".join(lines)

    def _add_hook(self, text: str, language: str) -> str:
        first_line = text.split("\n")[0].strip() if text.strip() else ""

        # Try to convert the first sentence into a hook
        if language == "ru":
            hooks = [
                "Вот что важно знать 👇",
                "Об этом мало кто говорит 👇",
                "Задумайтесь об этом 👇",
            ]
        else:
            hooks = [
                "Here's what you need to know 👇",
                "No one talks about this 👇",
                "Think about this 👇",
            ]

        # If first line is already short and punchy, just add emoji
        if len(first_line) < rules.HOOK_MAX_LENGTH and first_line.endswith(("!", "?")):
            return text

        hook = random.choice(hooks)
        return hook + "\n\n" + text

    def _add_cta(self, text: str, language: str) -> str:
        if language == "ru":
            ctas = [
                "А что думаете вы? 👇",
                "Согласны? Пишите в комментарии!",
                "Сохраняйте, чтобы не потерять! 📌",
            ]
        else:
            ctas = [
                "What do you think? 👇",
                "Do you agree? Drop a comment!",
                "Save this for later! 📌",
            ]

        cta = random.choice(ctas)

        # Add after the main text but before hashtags
        parts = text.rsplit("\n", 1)
        last_part = parts[-1] if parts else ""
        hashtags_in_last = re.findall(r"#\w+", last_part)

        if hashtags_in_last:
            # Insert CTA before hashtag block
            hashtag_block = " ".join(hashtags_in_last)
            text_without_hashtags = re.sub(r"\s*#\w+", "", text).rstrip()
            return text_without_hashtags + "\n\n" + cta + "\n\n" + hashtag_block
        else:
            return text.rstrip() + "\n\n" + cta

    def _add_emojis(self, text: str) -> str:
        # Add subtle emojis at line breaks
        lines = text.split("\n")
        if len(lines) == 1:
            return text

        emojis = ["✨", "💡", "🔥", "👀", "💯"]
        result_lines = []
        emoji_idx = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                # Add emoji to end of content lines (not every line)
                if i > 0 and emoji_idx < len(emojis) and i % 2 == 0:
                    line = line.rstrip() + " " + emojis[emoji_idx]
                    emoji_idx += 1
            result_lines.append(line)

        return "\n".join(result_lines)

    def _add_hashtags(self, text: str, topic: str, count: int, existing: list) -> str:
        topic_key = topic.lower() if topic.lower() in rules.TOPIC_HASHTAGS else "default"
        available = [
            h for h in rules.TOPIC_HASHTAGS[topic_key]
            if h not in existing
        ]
        # Also add default FYP tags
        if topic_key != "default":
            available.extend(
                h for h in rules.TOPIC_HASHTAGS["default"]
                if h not in existing and h not in available
            )

        selected = available[:count]
        hashtag_str = " ".join(selected)
        return text.rstrip() + "\n\n" + hashtag_str

    def _trim_to_limit(self, text: str) -> str:
        if len(text) <= rules.CAPTION_MAX_LENGTH:
            return text

        # Preserve hashtags at the end
        hashtags = re.findall(r"#\w+", text)
        hashtag_str = " ".join(hashtags[-rules.HASHTAGS_MAX:]) if hashtags else ""
        hashtag_len = len(hashtag_str) + 2  # +2 for \n\n

        content = re.sub(r"\s*#\w+", "", text).strip()
        max_content_len = rules.CAPTION_MAX_LENGTH - hashtag_len

        if len(content) > max_content_len:
            content = content[: max_content_len - 3].rsplit(" ", 1)[0] + "..."

        if hashtag_str:
            return content + "\n\n" + hashtag_str
        return content

    def _clean_whitespace(self, text: str) -> str:
        # Remove excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove trailing spaces on lines
        lines = [line.rstrip() for line in text.split("\n")]
        return "\n".join(lines).strip()
