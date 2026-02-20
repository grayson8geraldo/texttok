"""UGC marketing text generator based on product templates.

Generates varied Dutch TikTok-ready marketing texts that:
- Follow the template structure (hook → actions → rewards → safety → CTA)
- Stay compliant with moderation rules (no banned words/patterns)
- Apply Dutch TikTok slang and informal tone
- Can produce unlimited unique combinations
"""

import random
import re
from typing import Optional

from . import rules
from .templates import BANNED_PATTERNS, BANNED_WORDS, TEMPLATES
from .transformer import TextTransformer


class ModerationError(Exception):
    """Raised when generated text contains banned content."""
    pass


class UGCGenerator:
    """Generates TikTok UGC marketing text from templates."""

    def __init__(self):
        self.transformer = TextTransformer()

    def list_templates(self) -> list:
        """Return available template names and descriptions."""
        return [
            {"id": t["id"], "name": t["name"], "type": t["type"], "description": t["description"]}
            for t in TEMPLATES.values()
        ]

    def generate(
        self,
        template_id: str,
        count: int = 1,
        style: str = "full",
        add_hashtags: bool = True,
        add_emojis: bool = True,
        seed: Optional[int] = None,
    ) -> list:
        """Generate UGC marketing texts.

        Args:
            template_id: "snell" or "tube"
            count: number of unique texts to generate
            style: "full" (all sections), "short" (hook + action + CTA),
                   "caption" (compact single paragraph)
            add_hashtags: whether to append hashtags
            add_emojis: whether to sprinkle emojis
            seed: optional random seed for reproducibility

        Returns:
            List of dicts with keys: text, sections, warnings
        """
        if template_id not in TEMPLATES:
            raise ValueError(f"Unknown template: {template_id}. Available: {list(TEMPLATES.keys())}")

        if seed is not None:
            random.seed(seed)

        template = TEMPLATES[template_id]
        results = []
        used_combos = set()

        attempts = 0
        max_attempts = count * 10

        while len(results) < count and attempts < max_attempts:
            attempts += 1
            text, sections = self._build_text(template, style, add_emojis)

            # Deduplicate by hook+action combo
            combo_key = (sections["hook"], sections["actions"])
            if combo_key in used_combos:
                continue
            used_combos.add(combo_key)

            # Add hashtags
            if add_hashtags:
                hashtags = self._pick_hashtags(template)
                text = text.rstrip() + "\n\n" + " ".join(hashtags)

            # Moderation check
            warnings = self._check_moderation(text)

            results.append({
                "text": text,
                "sections": sections,
                "warnings": warnings,
                "template": template_id,
                "style": style,
            })

        return results

    def _build_text(self, template: dict, style: str, add_emojis: bool) -> tuple:
        """Build a single text from template sections. Returns (text, sections_dict)."""
        hook = random.choice(template["hooks"])
        actions = random.choice(template["actions"])
        rewards = random.choice(template["rewards"])
        safety = random.choice(template["safety"])
        cta = random.choice(template["ctas"])

        sections = {
            "hook": hook,
            "actions": actions,
            "rewards": rewards,
            "safety": safety,
            "cta": cta,
        }

        if style == "short":
            parts = [hook, "", actions, "", cta]
        elif style == "caption":
            parts = [f"{hook} {actions} {cta}"]
        else:  # full
            parts = [hook, "", actions, "", rewards, "", safety, "", cta]

        text = "\n".join(parts)

        # Apply slang
        text = self._apply_slang(text)

        # Add emojis between sections
        if add_emojis:
            text = self._sprinkle_emojis(text)

        return text, sections

    def _apply_slang(self, text: str) -> str:
        """Apply Dutch TikTok slang replacements."""
        result = text
        for formal, slang in rules.SLANG_MAP_NL.items():
            pattern = re.compile(re.escape(formal), re.IGNORECASE)
            result = pattern.sub(slang, result)
        return result

    def _sprinkle_emojis(self, text: str) -> str:
        """Add emojis at section breaks."""
        emojis_pool = ["🔥", "✨", "👀", "💯", "🎯", "📱", "⚡", "🚀", "💡", "👇"]
        lines = text.split("\n")
        result = []
        emoji_idx = 0

        for i, line in enumerate(lines):
            if line.strip() and not line.startswith("#"):
                # Add emoji at end of non-empty lines (not all, ~40% chance)
                if i > 0 and emoji_idx < len(emojis_pool) and random.random() < 0.4:
                    line = line.rstrip() + " " + emojis_pool[emoji_idx]
                    emoji_idx += 1
            result.append(line)

        return "\n".join(result)

    def _pick_hashtags(self, template: dict) -> list:
        """Pick relevant hashtags for the template."""
        base_tags = ["#FYP", "#ForYou", "#Viral"]

        type_tags = {
            "clicker": ["#TelegramGame", "#ClickerGame", "#MobileGame", "#Gaming", "#TelegramBot"],
            "video_tasks": ["#Bijbaan", "#MicroTaken", "#Telefoon", "#TelegramBot", "#VideoReview"],
        }

        pool = type_tags.get(template["type"], [])
        selected = random.sample(pool, min(2, len(pool)))
        return base_tags[:2] + selected

    def _check_moderation(self, text: str) -> list:
        """Check text against moderation rules. Returns list of warnings."""
        warnings = []
        text_lower = text.lower()

        for word in BANNED_WORDS:
            if word.lower() in text_lower:
                warnings.append(f"Banned word/phrase detected: '{word}'")

        for pattern in BANNED_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                warnings.append(f"Banned pattern detected: {pattern}")

        return warnings

    def generate_batch(
        self,
        template_id: str,
        count: int = 10,
        styles: Optional[list] = None,
    ) -> list:
        """Generate a mixed batch of texts in different styles.

        Args:
            template_id: "snell" or "tube"
            count: total number of texts
            styles: list of styles to cycle through (default: all three)

        Returns:
            List of generated text dicts
        """
        if styles is None:
            styles = ["full", "short", "caption"]

        results = []
        per_style = max(1, count // len(styles))
        remainder = count - per_style * len(styles)

        for i, style in enumerate(styles):
            n = per_style + (1 if i < remainder else 0)
            results.extend(self.generate(template_id, count=n, style=style))

        random.shuffle(results)
        return results[:count]
