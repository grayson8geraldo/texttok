"""Tests for TextTok optimizer."""

import unittest

from optimizer.analyzer import TextAnalyzer
from optimizer.transformer import TextTransformer


class TestTextAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = TextAnalyzer()

    def test_detect_language_russian(self):
        report = self.analyzer.analyze("Привет, это тестовый текст на русском языке.")
        self.assertEqual(report.language, "ru")

    def test_detect_language_english(self):
        report = self.analyzer.analyze("Hello, this is a test text in English.")
        self.assertEqual(report.language, "en")

    def test_word_count(self):
        report = self.analyzer.analyze("One two three four five.")
        self.assertEqual(report.word_count, 5)

    def test_sentence_count(self):
        report = self.analyzer.analyze("First sentence. Second sentence. Third one!")
        self.assertEqual(report.sentence_count, 3)

    def test_hashtag_detection(self):
        report = self.analyzer.analyze("Some text #FYP #Viral #Trending")
        self.assertEqual(report.hashtag_count, 3)
        self.assertEqual(report.existing_hashtags, ["#FYP", "#Viral", "#Trending"])

    def test_no_hashtags(self):
        report = self.analyzer.analyze("Just plain text without any tags.")
        self.assertEqual(report.hashtag_count, 0)

    def test_hook_detection_question(self):
        report = self.analyzer.analyze("Did you know this?\nSome content here.")
        self.assertTrue(report.has_hook)

    def test_hook_detection_exclamation(self):
        report = self.analyzer.analyze("Stop scrolling!\nYou need to see this.")
        self.assertTrue(report.has_hook)

    def test_no_hook(self):
        report = self.analyzer.analyze(
            "This is a regular sentence that doesn't really grab attention in any meaningful way at all."
        )
        self.assertFalse(report.has_hook)

    def test_cta_detection_english(self):
        report = self.analyzer.analyze("Great content here. Follow for more!")
        self.assertTrue(report.has_cta)

    def test_cta_detection_russian(self):
        report = self.analyzer.analyze("Отличный контент. Подпишись на канал!")
        self.assertTrue(report.has_cta)

    def test_no_cta(self):
        report = self.analyzer.analyze("Just some regular text here. Nothing special.")
        self.assertFalse(report.has_cta)

    def test_complex_phrases_russian(self):
        text = "В настоящее время в связи с тем что это важно."
        report = self.analyzer.analyze(text)
        self.assertIn("в настоящее время", report.complex_phrases_found)
        self.assertIn("в связи с тем что", report.complex_phrases_found)

    def test_complex_phrases_english(self):
        text = "In order to achieve this, due to the fact that we need it."
        report = self.analyzer.analyze(text)
        self.assertIn("in order to", report.complex_phrases_found)
        self.assertIn("due to the fact that", report.complex_phrases_found)

    def test_line_break_detection(self):
        report = self.analyzer.analyze("Line one.\nLine two.")
        self.assertTrue(report.has_line_breaks)

    def test_no_line_breaks(self):
        report = self.analyzer.analyze("All on one line without any breaks at all.")
        self.assertFalse(report.has_line_breaks)

    def test_score_range(self):
        report = self.analyzer.analyze("Test text.")
        self.assertGreaterEqual(report.score, 0)
        self.assertLessEqual(report.score, 100)

    def test_long_sentence_detection(self):
        long = " ".join(["word"] * 25) + "."
        report = self.analyzer.analyze(long)
        self.assertEqual(len(report.long_sentences), 1)

    def test_emoji_counting(self):
        report = self.analyzer.analyze("Hello 🔥 world ✨ test 💯")
        self.assertEqual(report.emoji_count, 3)

    def test_summary_output(self):
        report = self.analyzer.analyze("Test text.")
        summary = report.summary()
        self.assertIn("Length:", summary)
        self.assertIn("TikTok Score:", summary)


class TestTextTransformer(unittest.TestCase):

    def setUp(self):
        self.transformer = TextTransformer()

    def test_optimize_returns_required_keys(self):
        result = self.transformer.optimize("Some test text for optimization.")
        self.assertIn("original", result)
        self.assertIn("optimized", result)
        self.assertIn("before_report", result)
        self.assertIn("after_report", result)

    def test_original_preserved(self):
        text = "My original text stays the same."
        result = self.transformer.optimize(text)
        self.assertEqual(result["original"], text)

    def test_simplifies_complex_phrases_russian(self):
        text = "В настоящее время необходимо отметить что это важно."
        result = self.transformer.optimize(text)
        self.assertNotIn("В настоящее время", result["optimized"])
        self.assertIn("сейчас", result["optimized"].lower())

    def test_simplifies_complex_phrases_english(self):
        text = "In order to achieve this goal, due to the fact that we need it."
        result = self.transformer.optimize(text)
        optimized_lower = result["optimized"].lower()
        self.assertNotIn("in order to", optimized_lower)
        self.assertNotIn("due to the fact that", optimized_lower)

    def test_adds_hashtags(self):
        text = "Simple text without any hashtags at all."
        result = self.transformer.optimize(text)
        self.assertIn("#", result["optimized"])

    def test_adds_hashtags_with_topic(self):
        text = "Learning something new today."
        result = self.transformer.optimize(text, topic="education")
        optimized = result["optimized"]
        has_edu_tag = any(
            tag in optimized
            for tag in ["#LearnOnTikTok", "#EduTok", "#KnowledgeIsPower"]
        )
        self.assertTrue(has_edu_tag)

    def test_score_improves_or_stays(self):
        text = (
            "In today's world it is important to note that a large number of "
            "people are struggling with various challenges that affect their daily lives "
            "and in spite of the fact that many solutions exist most people are not aware "
            "of them which is truly unfortunate."
        )
        result = self.transformer.optimize(text)
        self.assertGreaterEqual(
            result["after_report"].score,
            result["before_report"].score,
        )

    def test_respects_max_length(self):
        long_text = "Word " * 500
        result = self.transformer.optimize(long_text)
        self.assertLessEqual(len(result["optimized"]), 2200)

    def test_adds_line_breaks(self):
        text = "First sentence here. Second sentence here. Third sentence here. Fourth sentence here."
        result = self.transformer.optimize(text)
        self.assertIn("\n", result["optimized"])

    def test_preserves_existing_hashtags(self):
        text = "Some text. #MyCustomTag"
        result = self.transformer.optimize(text)
        self.assertIn("#MyCustomTag", result["optimized"])

    def test_clean_whitespace(self):
        result = self.transformer.optimize("Test text.")
        optimized = result["optimized"]
        self.assertNotIn("\n\n\n", optimized)
        self.assertFalse(optimized.startswith("\n"))
        self.assertFalse(optimized.endswith("\n"))


class TestRussianIntegration(unittest.TestCase):
    """Integration tests with realistic Russian text."""

    def setUp(self):
        self.transformer = TextTransformer()

    def test_formal_russian_text(self):
        text = (
            "В настоящее время в связи с тем что большинство людей проводят "
            "значительное количество времени в социальных сетях, представляется "
            "необходимым осуществлять деятельность по созданию качественного контента "
            "который будет оказывать воздействие на целевую аудиторию и формировать "
            "положительное восприятие бренда."
        )
        result = self.transformer.optimize(text, topic="business")
        optimized = result["optimized"]

        # Should simplify
        self.assertNotIn("в настоящее время", optimized.lower())
        self.assertNotIn("в связи с тем что", optimized.lower())
        self.assertNotIn("осуществлять деятельность", optimized.lower())
        self.assertNotIn("оказывать воздействие", optimized.lower())

        # Should have hashtags
        self.assertIn("#", optimized)

        # Score should improve
        self.assertGreater(result["after_report"].score, result["before_report"].score)


class TestEnglishIntegration(unittest.TestCase):
    """Integration tests with realistic English text."""

    def setUp(self):
        self.transformer = TextTransformer()

    def test_formal_english_text(self):
        text = (
            "In today's world, it is important to note that in order to achieve "
            "success in the vast majority of business endeavors, one must take into "
            "consideration the fact that due to the fact that social media plays a "
            "significant role, each and every entrepreneur should first and foremost "
            "focus on building a strong online presence."
        )
        result = self.transformer.optimize(text, topic="business")
        optimized = result["optimized"]

        # Should simplify
        self.assertNotIn("in order to", optimized.lower())
        self.assertNotIn("due to the fact that", optimized.lower())
        self.assertNotIn("each and every", optimized.lower())
        self.assertNotIn("first and foremost", optimized.lower())

        # Should have hashtags
        self.assertIn("#", optimized)

        # Score should improve
        self.assertGreater(result["after_report"].score, result["before_report"].score)


class TestDutchAnalyzer(unittest.TestCase):
    """Tests for Dutch language detection and analysis."""

    def setUp(self):
        self.analyzer = TextAnalyzer()

    def test_detect_language_dutch(self):
        text = "Dit is een heel belangrijk bericht voor iedereen die het niet weet."
        report = self.analyzer.analyze(text)
        self.assertEqual(report.language, "nl")

    def test_complex_phrases_dutch(self):
        text = "Met betrekking tot dit onderwerp zijn wij ook van mening dat het op dit moment niet heel goed gaat voor de mensen."
        report = self.analyzer.analyze(text)
        self.assertEqual(report.language, "nl")
        self.assertIn("met betrekking tot", report.complex_phrases_found)
        self.assertIn("op dit moment", report.complex_phrases_found)

    def test_cta_detection_dutch(self):
        report = self.analyzer.analyze("Geweldige content. Volg voor meer!")
        self.assertTrue(report.has_cta)

    def test_hook_detection_dutch(self):
        report = self.analyzer.analyze("Wist je dit?\nDit is belangrijk.")
        self.assertTrue(report.has_hook)


class TestDutchTransformer(unittest.TestCase):
    """Tests for Dutch text transformation and slang."""

    def setUp(self):
        self.transformer = TextTransformer()

    def test_simplifies_dutch_formal(self):
        text = "Op dit moment zijn wij van mening dat het met betrekking tot dit onderwerp heel belangrijk is."
        result = self.transformer.optimize(text)
        optimized_lower = result["optimized"].lower()
        self.assertNotIn("op dit moment", optimized_lower)
        self.assertNotIn("van mening zijn", optimized_lower)
        self.assertNotIn("met betrekking tot", optimized_lower)

    def test_applies_dutch_slang(self):
        text = "Dit is heel goed en ook heel leuk voor iedereen die het niet weet."
        result = self.transformer.optimize(text)
        optimized_lower = result["optimized"].lower()
        # Should convert "heel goed" -> "vet goed" or "heel leuk" -> "echt nice"
        has_slang = "vet goed" in optimized_lower or "echt nice" in optimized_lower
        self.assertTrue(has_slang)

    def test_dutch_hashtags(self):
        text = "Dit is een heel belangrijk bericht voor iedereen die het niet weet."
        result = self.transformer.optimize(text)
        self.assertIn("#", result["optimized"])

    def test_dutch_score_improves(self):
        text = (
            "Op dit moment is het van belang dat wij met betrekking tot de huidige "
            "situatie werkzaamheden verrichten die een bijdrage leveren aan het verbeteren "
            "van de kwaliteit van het onderwijs in Nederland want dat is heel erg belangrijk "
            "voor de toekomst van onze samenleving."
        )
        result = self.transformer.optimize(text, topic="education")
        self.assertGreater(result["after_report"].score, result["before_report"].score)


class TestDutchIntegration(unittest.TestCase):
    """Full integration test with realistic Dutch text."""

    def setUp(self):
        self.transformer = TextTransformer()

    def test_formal_dutch_text(self):
        text = (
            "Op dit moment is het van belang dat men met betrekking tot sociale media "
            "werkzaamheden verrichten om een bijdrage leveren aan de groei van het merk, "
            "want dat is desalniettemin heel erg belangrijk voor de toekomst."
        )
        result = self.transformer.optimize(text, topic="business")
        optimized = result["optimized"]
        optimized_lower = optimized.lower()

        # Should simplify formal phrases
        self.assertNotIn("op dit moment", optimized_lower)
        self.assertNotIn("met betrekking tot", optimized_lower)
        self.assertNotIn("werkzaamheden verrichten", optimized_lower)

        # Should apply slang
        self.assertNotIn("heel erg", optimized_lower)

        # Should have hashtags
        self.assertIn("#", optimized)

        # Score should improve
        self.assertGreater(result["after_report"].score, result["before_report"].score)


if __name__ == "__main__":
    unittest.main()
