"""UGC voiceover text generator based on product templates.

Generates clean voiceover text for TikTok videos:
- Text you can directly use as speech / subtitles in your video
- Organized by sections: Hook → Action → Rewards → Safety → CTA
- Three styles: full (all sections), short (hook+action+cta), caption (one paragraph)
- Moderation-safe: no banned words or financial promises
"""

import random
import re
from typing import Optional

from .templates import BANNED_PATTERNS, BANNED_WORDS, HASHTAGS, TEMPLATES

# Section order — maps internal names to display labels
SECTIONS_FULL = ["hook", "action", "rewards", "safety", "cta"]
SECTIONS_SHORT = ["hook", "action", "cta"]

# Template key mapping: section name → template pool key
POOL_KEY = {
    "hook": "hooks",
    "action": "actions",
    "rewards": "rewards",
    "safety": "safety",
    "cta": "ctas",
}


class UGCGenerator:
    """Generates clean voiceover text from templates."""

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
        """Generate voiceover texts.

        Args:
            template_id: "snell" or "tube"
            count: number of unique texts to generate
            style: "full" (all 5 sections), "short" (hook+action+cta), "caption" (single paragraph)
            add_hashtags: append relevant hashtags at the end
            add_emojis: add emojis between sections
            seed: optional random seed for reproducibility

        Returns:
            List of dicts with keys: text, sections, style, template, warnings
        """
        if template_id not in TEMPLATES:
            raise ValueError(f"Unknown template: {template_id}. Available: {list(TEMPLATES.keys())}")

        if style not in ("full", "short", "caption"):
            raise ValueError(f"Unknown style: {style}. Use: full, short, caption")

        if seed is not None:
            random.seed(seed)

        template = TEMPLATES[template_id]
        results = []
        used_combos = set()

        attempts = 0
        max_attempts = count * 20

        while len(results) < count and attempts < max_attempts:
            attempts += 1

            # Pick one random text from each section pool
            sections = self._pick_sections(template)

            # Deduplicate by combo of picked texts
            combo_key = tuple(sections[s] for s in SECTIONS_FULL)
            if combo_key in used_combos:
                continue
            used_combos.add(combo_key)

            # Build the voiceover text
            text = self._format_text(sections, style, add_emojis)

            # Add hashtags
            if add_hashtags:
                tags = self._pick_hashtags(template["type"])
                text = text + "\n\n" + tags

            # Moderation check
            warnings = self._check_moderation(text)

            results.append({
                "text": text,
                "sections": sections,
                "style": style,
                "template": template_id,
                "warnings": warnings,
            })

        return results

    def generate_batch(
        self,
        template_id: str,
        count: int = 9,
        add_hashtags: bool = True,
        add_emojis: bool = True,
        seed: Optional[int] = None,
    ) -> list:
        """Generate a mixed batch of texts in all three styles.

        Distributes count evenly across full, short, caption styles.
        """
        per_style = max(1, count // 3)
        remainder = count - per_style * 3

        results = []
        for i, style in enumerate(["full", "short", "caption"]):
            n = per_style + (1 if i < remainder else 0)
            results.extend(
                self.generate(
                    template_id=template_id,
                    count=n,
                    style=style,
                    add_hashtags=add_hashtags,
                    add_emojis=add_emojis,
                    seed=seed,
                )
            )
            # Reset seed so next style gets different combos
            seed = None

        return results

    def _pick_sections(self, template: dict) -> dict:
        """Pick one random text from each section pool."""
        return {
            section: random.choice(template[POOL_KEY[section]])
            for section in SECTIONS_FULL
        }

    def _format_text(self, sections: dict, style: str, add_emojis: bool) -> str:
        """Format picked sections into clean voiceover text."""
        if style == "full":
            order = SECTIONS_FULL
        elif style == "short":
            order = SECTIONS_SHORT
        else:  # caption
            order = SECTIONS_FULL

        parts = [sections[s] for s in order]

        if style == "caption":
            # Single paragraph — join with spaces
            return " ".join(parts)

        if add_emojis:
            # Add subtle emojis at the start of each section
            emoji_map = {
                "hook": "",      # hook is clean — no emoji needed
                "action": "",
                "rewards": "",
                "safety": "",
                "cta": "",
            }
            decorated = []
            for s in order:
                prefix = emoji_map.get(s, "")
                decorated.append(prefix + sections[s])
            return "\n\n".join(decorated)

        # No emojis — just separate sections with blank lines
        return "\n\n".join(parts)

    def _pick_hashtags(self, template_type: str, count: int = 5) -> str:
        """Pick random hashtags for the template type."""
        pool = HASHTAGS.get(template_type, HASHTAGS["clicker"])
        tags = random.sample(pool, min(count, len(pool)))
        return " ".join(tags)

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
