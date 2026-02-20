"""Tests for UGC generator and moderation compliance."""

import unittest

from optimizer.generator import UGCGenerator
from optimizer.templates import BANNED_WORDS, BANNED_PATTERNS, TEMPLATES


class TestGeneratorBasics(unittest.TestCase):

    def setUp(self):
        self.gen = UGCGenerator()

    def test_list_templates(self):
        templates = self.gen.list_templates()
        self.assertEqual(len(templates), 2)
        ids = [t["id"] for t in templates]
        self.assertIn("snell", ids)
        self.assertIn("tube", ids)

    def test_unknown_template_raises(self):
        with self.assertRaises(ValueError):
            self.gen.generate("nonexistent")

    def test_generate_returns_list(self):
        results = self.gen.generate("snell", count=1)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)

    def test_generate_result_keys(self):
        results = self.gen.generate("snell", count=1)
        item = results[0]
        self.assertIn("text", item)
        self.assertIn("sections", item)
        self.assertIn("warnings", item)
        self.assertIn("template", item)
        self.assertIn("style", item)

    def test_generate_multiple(self):
        results = self.gen.generate("tube", count=5)
        self.assertEqual(len(results), 5)

    def test_texts_are_unique(self):
        results = self.gen.generate("snell", count=5)
        texts = [r["text"] for r in results]
        self.assertEqual(len(texts), len(set(texts)))

    def test_seed_reproducibility(self):
        r1 = self.gen.generate("snell", count=3, seed=42)
        r2 = self.gen.generate("snell", count=3, seed=42)
        for a, b in zip(r1, r2):
            self.assertEqual(a["text"], b["text"])


class TestGeneratorStyles(unittest.TestCase):

    def setUp(self):
        self.gen = UGCGenerator()

    def test_full_style_has_all_sections(self):
        results = self.gen.generate("snell", count=1, style="full", add_emojis=False)
        text = results[0]["text"]
        sections = results[0]["sections"]
        # All section texts should appear in the output
        self.assertIn(sections["hook"], text)
        self.assertIn(sections["cta"], text)

    def test_short_style_omits_rewards_and_safety(self):
        results = self.gen.generate("tube", count=1, style="short", add_emojis=False)
        text = results[0]["text"]
        sections = results[0]["sections"]
        # Should have hook and cta
        self.assertIn(sections["hook"], text)
        self.assertIn(sections["cta"], text)
        # Should NOT have rewards and safety
        self.assertNotIn(sections["rewards"], text)
        self.assertNotIn(sections["safety"], text)

    def test_caption_style_is_single_paragraph(self):
        results = self.gen.generate("snell", count=1, style="caption", add_emojis=False, add_hashtags=False)
        text = results[0]["text"]
        # Caption should not have double newlines (it's a single paragraph)
        self.assertNotIn("\n\n", text)


class TestGeneratorHashtags(unittest.TestCase):

    def setUp(self):
        self.gen = UGCGenerator()

    def test_hashtags_included_by_default(self):
        results = self.gen.generate("snell", count=1)
        self.assertIn("#", results[0]["text"])

    def test_no_hashtags_flag(self):
        results = self.gen.generate("snell", count=1, add_hashtags=False)
        self.assertNotIn("#", results[0]["text"])

    def test_snell_gets_gaming_hashtags(self):
        results = self.gen.generate("snell", count=1, seed=1)
        text = results[0]["text"]
        has_gaming = any(tag in text for tag in ["#TelegramGame", "#ClickerGame", "#MobileGame", "#Gaming", "#TelegramBot"])
        self.assertTrue(has_gaming)

    def test_tube_gets_task_hashtags(self):
        results = self.gen.generate("tube", count=1, seed=1)
        text = results[0]["text"]
        has_task = any(tag in text for tag in ["#Bijbaan", "#MicroTaken", "#Telefoon", "#TelegramBot", "#VideoReview"])
        self.assertTrue(has_task)


class TestModerationCompliance(unittest.TestCase):
    """Ensure generated texts don't contain banned content."""

    def setUp(self):
        self.gen = UGCGenerator()

    def test_snell_no_banned_words(self):
        results = self.gen.generate("snell", count=10, seed=123)
        for r in results:
            self.assertEqual(r["warnings"], [], f"Warnings found in: {r['text'][:80]}")

    def test_tube_no_banned_words(self):
        results = self.gen.generate("tube", count=10, seed=456)
        for r in results:
            self.assertEqual(r["warnings"], [], f"Warnings found in: {r['text'][:80]}")

    def test_templates_dont_contain_currency_symbols(self):
        """Verify raw template pools don't have $ / euro / etc."""
        for name, tmpl in TEMPLATES.items():
            for section in ["hooks", "actions", "rewards", "safety", "ctas"]:
                for text in tmpl[section]:
                    for symbol in ["$", "€", "₽"]:
                        self.assertNotIn(
                            symbol, text,
                            f"Currency symbol '{symbol}' in {name}.{section}: {text}"
                        )

    def test_templates_dont_promise_earnings(self):
        """Verify raw templates don't use earning-related words."""
        earning_words = ["verdienen", "salaris", "inkomen", "winst", "geld"]
        for name, tmpl in TEMPLATES.items():
            for section in ["hooks", "actions", "rewards", "safety", "ctas"]:
                for text in tmpl[section]:
                    text_lower = text.lower()
                    for word in earning_words:
                        self.assertNotIn(
                            word, text_lower,
                            f"Earning word '{word}' in {name}.{section}: {text}"
                        )


class TestGeneratorBatch(unittest.TestCase):

    def setUp(self):
        self.gen = UGCGenerator()

    def test_batch_generates_correct_count(self):
        results = self.gen.generate_batch("snell", count=6)
        self.assertEqual(len(results), 6)

    def test_batch_mixes_styles(self):
        results = self.gen.generate_batch("tube", count=9)
        styles = set(r["style"] for r in results)
        self.assertTrue(len(styles) >= 2)


class TestSnellTemplate(unittest.TestCase):
    """Verify Snell template content quality."""

    def test_all_sections_populated(self):
        tmpl = TEMPLATES["snell"]
        self.assertGreater(len(tmpl["hooks"]), 5)
        self.assertGreater(len(tmpl["actions"]), 3)
        self.assertGreater(len(tmpl["rewards"]), 3)
        self.assertGreater(len(tmpl["safety"]), 3)
        self.assertGreater(len(tmpl["ctas"]), 3)

    def test_hooks_are_dutch(self):
        tmpl = TEMPLATES["snell"]
        dutch_words = ["je", "een", "de", "het", "van", "in", "die", "dit", "voor", "er", "echt", "deze", "al", "mijn", "nieuwe"]
        for hook in tmpl["hooks"]:
            words = hook.lower().split()
            has_dutch = any(w in dutch_words for w in words)
            self.assertTrue(has_dutch, f"Hook doesn't look Dutch: {hook}")


class TestTubeTemplate(unittest.TestCase):
    """Verify Tube template content quality."""

    def test_all_sections_populated(self):
        tmpl = TEMPLATES["tube"]
        self.assertGreater(len(tmpl["hooks"]), 5)
        self.assertGreater(len(tmpl["actions"]), 3)
        self.assertGreater(len(tmpl["rewards"]), 3)
        self.assertGreater(len(tmpl["safety"]), 3)
        self.assertGreater(len(tmpl["ctas"]), 3)

    def test_rewards_are_modest(self):
        """Tube rewards should use modest language."""
        tmpl = TEMPLATES["tube"]
        modest_terms = ["kleine", "micro", "bescheiden", "niet", "geen"]
        for reward in tmpl["rewards"]:
            text_lower = reward.lower()
            has_modest = any(t in text_lower for t in modest_terms)
            self.assertTrue(has_modest, f"Reward not modest enough: {reward}")


if __name__ == "__main__":
    unittest.main()
