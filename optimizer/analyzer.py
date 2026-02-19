"""Analyzes text against TikTok platform requirements and provides a report."""

import re
import unicodedata
from dataclasses import dataclass, field

from . import rules


@dataclass
class AnalysisReport:
    """Report of how well text meets TikTok requirements."""

    total_length: int = 0
    sentence_count: int = 0
    word_count: int = 0
    avg_sentence_length: int = 0
    long_sentences: list = field(default_factory=list)
    complex_phrases_found: list = field(default_factory=list)
    hashtag_count: int = 0
    existing_hashtags: list = field(default_factory=list)
    emoji_count: int = 0
    has_hook: bool = False
    has_cta: bool = False
    has_line_breaks: bool = False
    language: str = "unknown"
    score: int = 0  # 0-100
    issues: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)

    def summary(self) -> str:
        lines = []
        lines.append(f"  Length:            {self.total_length} chars")
        lines.append(f"  Words:             {self.word_count}")
        lines.append(f"  Sentences:         {self.sentence_count}")
        lines.append(f"  Avg sentence len:  {self.avg_sentence_length} words")
        lines.append(f"  Long sentences:    {len(self.long_sentences)}")
        lines.append(f"  Complex phrases:   {len(self.complex_phrases_found)}")
        lines.append(f"  Hashtags:          {self.hashtag_count}")
        lines.append(f"  Emojis:            {self.emoji_count}")
        lines.append(f"  Has hook:          {'Yes' if self.has_hook else 'No'}")
        lines.append(f"  Has CTA:           {'Yes' if self.has_cta else 'No'}")
        lines.append(f"  Line breaks:       {'Yes' if self.has_line_breaks else 'No'}")
        lines.append(f"  Language:          {self.language}")
        lines.append(f"  TikTok Score:      {self.score}/100")

        if self.issues:
            lines.append("\n  Issues:")
            for issue in self.issues:
                lines.append(f"    - {issue}")

        if self.suggestions:
            lines.append("\n  Suggestions:")
            for suggestion in self.suggestions:
                lines.append(f"    + {suggestion}")

        return "\n".join(lines)


class TextAnalyzer:
    """Analyzes text for TikTok compatibility."""

    def analyze(self, text: str) -> AnalysisReport:
        report = AnalysisReport()

        report.language = self._detect_language(text)
        report.total_length = len(text)
        report.existing_hashtags = self._extract_hashtags(text)
        report.hashtag_count = len(report.existing_hashtags)
        report.emoji_count = self._count_emojis(text)
        report.has_line_breaks = "\n" in text

        # Strip hashtags for content analysis
        content = self._strip_hashtags(text)
        sentences = self._split_sentences(content)
        report.sentence_count = len(sentences)
        report.word_count = len(content.split())
        report.avg_sentence_length = (
            report.word_count // report.sentence_count if report.sentence_count > 0 else 0
        )

        # Long sentences
        for s in sentences:
            wc = len(s.split())
            if wc > rules.SENTENCE_MAX_WORDS:
                report.long_sentences.append(s.strip())

        # Complex phrases
        report.complex_phrases_found = self._find_complex_phrases(content, report.language)

        # Hook detection
        first_line = text.split("\n")[0].strip() if text.strip() else ""
        report.has_hook = self._has_hook(first_line)

        # CTA detection
        report.has_cta = self._has_cta(text)

        # Score and suggestions
        report.score = self._calculate_score(report)
        report.issues = self._identify_issues(report)
        report.suggestions = self._generate_suggestions(report)

        return report

    def _detect_language(self, text: str) -> str:
        cyrillic = sum(1 for c in text if "\u0400" <= c <= "\u04FF")
        latin = sum(1 for c in text if "A" <= c <= "Z" or "a" <= c <= "z")
        if cyrillic > latin:
            return "ru"
        return "en"

    def _extract_hashtags(self, text: str) -> list:
        return re.findall(r"#\w+", text)

    def _strip_hashtags(self, text: str) -> str:
        return re.sub(r"#\w+", "", text).strip()

    def _count_emojis(self, text: str) -> int:
        count = 0
        for char in text:
            if unicodedata.category(char) in ("So", "Sk"):
                count += 1
        return count

    def _split_sentences(self, text: str) -> list:
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _find_complex_phrases(self, text: str, language: str) -> list:
        found = []
        text_lower = text.lower()
        simplify_map = rules.SIMPLIFY_MAP_RU if language == "ru" else rules.SIMPLIFY_MAP_EN
        for phrase in simplify_map:
            if phrase in text_lower:
                found.append(phrase)
        if language == "ru":
            for word in rules.COMPLEX_WORD_INDICATORS_RU:
                if word in text_lower and word not in found:
                    found.append(word)
        return found

    def _has_hook(self, first_line: str) -> bool:
        first_lower = first_line.lower()
        # Check known patterns
        for pattern in rules.HOOK_PATTERNS:
            if pattern.lower() in first_lower:
                return True
        # Short punchy first line = good hook
        if len(first_line) <= rules.HOOK_MAX_LENGTH and first_line:
            if first_line.endswith(("!", "?", "...")) or first_line.isupper():
                return True
        return False

    def _has_cta(self, text: str) -> bool:
        text_lower = text.lower()
        for cta in rules.CTA_PHRASES:
            if cta.lower() in text_lower:
                return True
        # Check generic CTA patterns
        cta_patterns = [
            r"подпис\w*", r"подпиш\w*", r"комментир\w*", r"комментар\w*",
            r"лайк\w*", r"сохран\w*",
            r"follow", r"subscribe", r"comment", r"like", r"share", r"save",
        ]
        for pattern in cta_patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    def _calculate_score(self, report: AnalysisReport) -> int:
        score = 50  # baseline

        # Length scoring
        if rules.CAPTION_OPTIMAL_MIN <= report.total_length <= rules.CAPTION_OPTIMAL_MAX:
            score += 15
        elif report.total_length <= rules.CAPTION_MAX_LENGTH:
            score += 5
        else:
            score -= 20

        # Sentence length
        if report.avg_sentence_length <= rules.SENTENCE_MAX_WORDS:
            score += 10
        else:
            score -= 10

        if not report.long_sentences:
            score += 5

        # Complex phrases penalty
        score -= min(len(report.complex_phrases_found) * 3, 15)

        # Hashtags
        if rules.HASHTAGS_MIN <= report.hashtag_count <= rules.HASHTAGS_MAX:
            score += 10
        elif report.hashtag_count > 0:
            score += 3

        # Emojis
        if report.emoji_count > 0:
            score += 5

        # Hook
        if report.has_hook:
            score += 10

        # CTA
        if report.has_cta:
            score += 5

        # Line breaks
        if report.has_line_breaks:
            score += 5

        return max(0, min(100, score))

    def _identify_issues(self, report: AnalysisReport) -> list:
        issues = []
        if report.total_length > rules.CAPTION_MAX_LENGTH:
            issues.append(
                f"Text exceeds TikTok limit ({report.total_length}/{rules.CAPTION_MAX_LENGTH} chars)"
            )
        if report.total_length > rules.CAPTION_OPTIMAL_MAX:
            issues.append(
                f"Text is longer than optimal ({report.total_length} > {rules.CAPTION_OPTIMAL_MAX} chars)"
            )
        if report.long_sentences:
            issues.append(
                f"{len(report.long_sentences)} sentence(s) are too long (>{rules.SENTENCE_MAX_WORDS} words)"
            )
        if report.complex_phrases_found:
            issues.append(
                f"{len(report.complex_phrases_found)} complex phrase(s) can be simplified"
            )
        if report.hashtag_count == 0:
            issues.append("No hashtags found")
        elif report.hashtag_count > rules.HASHTAGS_MAX:
            issues.append(f"Too many hashtags ({report.hashtag_count} > {rules.HASHTAGS_MAX})")
        if not report.has_hook:
            issues.append("First line is not a strong hook")
        if not report.has_cta:
            issues.append("No call-to-action found")
        if report.emoji_count == 0:
            issues.append("No emojis — adding emojis boosts engagement")
        if not report.has_line_breaks:
            issues.append("No line breaks — harder to read on mobile")
        return issues

    def _generate_suggestions(self, report: AnalysisReport) -> list:
        suggestions = []
        if not report.has_hook:
            suggestions.append("Add a hook as the first line (e.g. 'POV:', question, or bold statement)")
        if not report.has_cta:
            suggestions.append("Add a call-to-action at the end (e.g. 'What do you think?')")
        if report.hashtag_count < rules.HASHTAGS_MIN:
            suggestions.append(f"Add {rules.HASHTAGS_MIN - report.hashtag_count} more hashtag(s)")
        if report.emoji_count == 0:
            suggestions.append("Add 2-3 emojis to increase engagement")
        if report.complex_phrases_found:
            suggestions.append("Simplify complex phrases for a conversational tone")
        if not report.has_line_breaks:
            suggestions.append("Add line breaks every 1-2 sentences for mobile readability")
        if report.total_length > rules.CAPTION_OPTIMAL_MAX:
            suggestions.append("Shorten text to 100-300 characters for optimal engagement")
        return suggestions
