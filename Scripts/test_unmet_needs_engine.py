import sys
import os
import json
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__)))

from unmet_needs_engine import detect_unmet_needs
from insights_synthesis_engine import GroundedSynthesisEngine

class TestUnmetNeedsEngine(unittest.TestCase):

    def test_unmet_needs_detection_output(self):
        res = detect_unmet_needs()
        self.assertIn("summary", res)
        self.assertIn("ranked_unmet_needs", res)
        
        needs = res["ranked_unmet_needs"]
        self.assertGreater(len(needs), 0)
        
        for item in needs:
            self.assertIn("rank", item)
            self.assertIn("title", item)
            self.assertIn("statement", item)
            self.assertIn("strength", item)
            self.assertIn("evidence_count", item)
            self.assertIn("unique_datasets_count", item)
            self.assertIn("unique_channels_count", item)
            self.assertIn("share_pct", item)
            self.assertIn("associated_purchase_barrier", item)
            self.assertIn("associated_purchase_behavior", item)
            self.assertIn("representative_evidence", item)
            self.assertGreater(item["evidence_count"], 0)
            self.assertGreater(item["unique_datasets_count"], 0)
            self.assertGreater(item["unique_channels_count"], 0)

    def test_high_strength_criteria(self):
        res = detect_unmet_needs()
        high_needs = [n for n in res["ranked_unmet_needs"] if n["strength"] == "High"]
        self.assertGreater(len(high_needs), 0)
        for n in high_needs:
            self.assertGreaterEqual(n["evidence_count"], 100)
            self.assertGreaterEqual(n["unique_datasets_count"], 3)

    def test_synthesis_unmet_needs_query(self):
        engine = GroundedSynthesisEngine()
        q = "What unmet needs emerge consistently across user conversations?"
        report = engine.generate_executive_report(q)
        
        self.assertIn("EXECUTIVE INSIGHT", report)
        self.assertIn("QUANTIFIED FINDINGS", report)
        self.assertIn("Price & Value Confidence", report)
        self.assertIn("Tactile Quality & Fabric Feel Verification", report)
        self.assertIn("Fit & Sizing Confidence", report)
        self.assertIn("REPRESENTATIVE GROUNDED EVIDENCE", report)

if __name__ == "__main__":
    unittest.main()
