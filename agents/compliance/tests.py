"""Tests unitaires minimaux du module conformité douanière."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .classifier import classify_product
from .journal import AuditJournal
from .models import ActorType, ConfidenceLevel, ProductDescription


class ComplianceClassifierTests(unittest.IsolatedAsyncioTestCase):
    """Tests de la chaîne de classification assistée."""

    async def test_classifier_high_confidence(self) -> None:
        product = ProductDescription(
            name="T-shirt tricoté à manches courtes 100% coton pour adulte",
            material_composition=["100% coton"],
            primary_use="vêtement porté à même la peau",
            country_origin="Chine",
            country_import="France",
            images=["photo-face.jpg", "etiquette-composition.jpg"],
            known_certifications=["RTC FR-RTC-2024-000001 à vérifier"],
            components=["étoffe en bonneterie", "manches courtes"],
            technical_specs={"construction": "bonneterie", "genre": "adulte unisexe"},
        )

        outcome = await classify_product(product)

        self.assertIsNone(outcome.escalation_ticket)
        self.assertIsNotNone(outcome.selected_proposal)
        self.assertEqual(outcome.selected_proposal.confidence_level, ConfidenceLevel.HIGH)
        self.assertGreaterEqual(outcome.selected_proposal.confidence_score, 0.78)
        self.assertIn("ASSISTE", outcome.disclaimer)
        self.assertTrue(outcome.selected_proposal.sources)

    async def test_classifier_medium_confidence_returns_missing_data(self) -> None:
        product = ProductDescription(
            name="Climatiseur portable avec compresseur R410A",
            material_composition=["métal", "plastique", "réfrigérant R410A"],
            primary_use="usage domestique pour refroidir une pièce",
            country_origin="Chine",
            country_import="France",
            components=["compresseur", "ventilateur"],
            technical_specs={"fluide_frigorigene": "R410A"},
        )

        outcome = await classify_product(product)

        self.assertIsNone(outcome.escalation_ticket)
        self.assertIsNotNone(outcome.selected_proposal)
        self.assertIn(outcome.selected_proposal.confidence_level, {ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH})
        self.assertTrue(outcome.proposals)
        self.assertTrue(outcome.selected_proposal.risk_flags)
        self.assertIn("RTC", outcome.recommendation.upper() + " " + " ".join(outcome.selected_proposal.risk_flags).upper())

    async def test_classifier_low_confidence_escalates(self) -> None:
        product = ProductDescription(
            name="Accessoire multifonction",
            raw_description="Accessoire multifonction pour usage divers",
        )

        outcome = await classify_product(product)

        self.assertIsNone(outcome.selected_proposal)
        self.assertIsNotNone(outcome.escalation_ticket)
        self.assertTrue(outcome.missing_data)
        self.assertIn("refus", outcome.recommendation.lower())


class AuditJournalTests(unittest.TestCase):
    """Tests d'intégrité du journal hash-chaîné."""

    def test_journal_integrity_success_and_tamper_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.jsonl"
            journal = AuditJournal(path)

            journal.append(
                actor=ActorType.MACHINE,
                action="test.first",
                payload={"value": 1},
            )
            journal.append(
                actor=ActorType.EXPERT,
                action="test.second",
                payload={"value": 2},
            )

            self.assertTrue(journal.verify_integrity())

            lines = path.read_text(encoding="utf-8").splitlines()
            tampered = json.loads(lines[0])
            tampered["payload"]["value"] = 999
            lines[0] = json.dumps(tampered, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")

            self.assertFalse(journal.verify_integrity())


if __name__ == "__main__":
    unittest.main()
