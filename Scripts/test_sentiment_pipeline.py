import sys
import os
import json
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__)))

from extract_behavioral_dimensions import analyze_sentiment_vader
from insights_synthesis_engine import GroundedSynthesisEngine

class TestVaderSentimentPipeline(unittest.TestCase):

    def test_positive_sentiment(self):
        text = "Amazing quality and perfect fit, totally worth it!"
        res = analyze_sentiment_vader(text)
        self.assertEqual(res["sentiment_label"], "Positive")
        self.assertGreater(res["sentiment_score"], 0.05)
        self.assertIsNotNone(res["sentiment_confidence"])

    def test_neutral_sentiment(self):
        text = "The package arrived on Monday."
        res = analyze_sentiment_vader(text)
        self.assertEqual(res["sentiment_label"], "Neutral")
        self.assertAlmostEqual(res["sentiment_score"], 0.0, delta=0.05)

    def test_negative_sentiment(self):
        text = "Terrible fabric, color bled in first wash, worst buy."
        res = analyze_sentiment_vader(text)
        self.assertEqual(res["sentiment_label"], "Negative")
        self.assertLess(res["sentiment_score"], -0.05)

    def test_mixed_sentiment(self):
        text = "I love the dress but the fit is confusing."
        res = analyze_sentiment_vader(text)
        self.assertIn(res["sentiment_label"], ["Mixed", "Positive"])
        self.assertGreater(res["components"]["pos"], 0.1)
        self.assertGreater(res["components"]["neg"], 0.1)

    def test_short_unusable_text(self):
        text = "k"
        res = analyze_sentiment_vader(text)
        self.assertEqual(res["sentiment_label"], "Unknown")
        self.assertIsNone(res["sentiment_score"])
        self.assertIsNone(res["sentiment_confidence"])

    def test_empty_null_text(self):
        for val in ["", None, "nan", "NULL"]:
            res = analyze_sentiment_vader(val)
            self.assertEqual(res["sentiment_label"], "Unknown")
            self.assertIsNone(res["sentiment_score"])
            self.assertIsNone(res["sentiment_confidence"])

    def test_enriched_dataset_sentiment_keys(self):
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Processed Data", "myntra_multidimensional_enriched.json")
        self.assertTrue(os.path.exists(json_path))
        with open(json_path, "r", encoding="utf-8") as f:
            records = json.load(f)
        self.assertGreater(len(records), 0)
        for r in records[:50]:
            self.assertIn("sentiment_analysis", r)
            sent = r["sentiment_analysis"]
            self.assertIn("sentiment_label", sent)
            self.assertIn("sentiment_score", sent)
            self.assertIn("sentiment_confidence", sent)

    def test_quantification_results_sentiment_keys(self):
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Processed Data", "quantification_results.json")
        self.assertTrue(os.path.exists(json_path))
        with open(json_path, "r", encoding="utf-8") as f:
            qdata = json.load(f)
        self.assertIn("sentiment_quantification", qdata)
        sq = qdata["sentiment_quantification"]
        self.assertIn("overall_sentiment_distribution", sq)
        self.assertIn("barrier_sentiment_breakdown", sq)

    def test_synthesis_engine_sentiment_output(self):
        engine = GroundedSynthesisEngine()
        q = "Why do users add fashion products to their wishlist?"
        report = engine.generate_executive_report(q)
        self.assertIn("EXECUTIVE INSIGHT", report)
        self.assertIn("QUANTIFIED FINDINGS", report)
        self.assertIn("REPRESENTATIVE GROUNDED EVIDENCE", report)

if __name__ == "__main__":
    unittest.main()
