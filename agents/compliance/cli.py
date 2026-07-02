"""Interface en ligne de commande du module conformité.

Exemple :
    python -m agents.compliance "Climatiseur portable, compresseur R410A, usage domestique, origine Chine, import France"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any

from .classifier import classify_product
from .compliance_checks import run_all_compliance_checks
from .journal import AuditJournal
from .models import LEGAL_DISCLAIMER, ActorType, ClassificationOutcome, ComplianceCheck, ProductDescription
from .sources import SourceRegistry


def parse_product_description(raw: str) -> ProductDescription:
    """Transforme une description libre CLI en ``ProductDescription`` structurée.

    Le parsing est volontairement conservateur : il extrait uniquement des
    signaux simples et laisse le reste dans ``raw_description``.
    """
    raw = raw.strip()
    if not raw:
        raise ValueError("La description produit ne peut pas être vide.")

    parts = [part.strip() for part in raw.split(",") if part.strip()]
    name = parts[0] if parts else raw

    primary_use = _extract_after_keywords(raw, ["usage", "utilisation", "use"])
    country_origin = _extract_after_keywords(raw, ["origine", "origin", "pays d'origine"])
    country_import = _extract_after_keywords(raw, ["import", "importation", "destination"])

    material_composition = _extract_materials(raw)
    components = _extract_components(raw)
    known_certifications = _extract_certifications(raw)
    technical_specs = _extract_technical_specs(raw)

    return ProductDescription(
        name=name,
        material_composition=material_composition,
        primary_use=primary_use,
        country_origin=country_origin,
        country_import=country_import,
        images=[],
        known_certifications=known_certifications,
        components=components,
        technical_specs=technical_specs,
        raw_description=raw,
    )


async def run_cli_async(args: argparse.Namespace) -> int:
    """Exécute la chaîne complète classification + conformité et affiche le rapport."""
    product = parse_product_description(args.description)
    registry = SourceRegistry.default()
    journal = None if args.no_journal else AuditJournal(args.journal_path)

    if journal is not None:
        journal.append(
            actor=ActorType.IMPORTATEUR,
            action="cli.product_submitted",
            payload={"raw_description": args.description, "product": product.model_dump(mode="json")},
        )

    outcome = await classify_product(product, source_registry=registry, audit_journal=journal)
    checks = await run_all_compliance_checks(
        product,
        classification=outcome.selected_proposal,
        source_registry=registry,
    )

    outcome.decision_chain.compliance_checks = checks
    outcome.decision_chain.add_step(
        actor=ActorType.MACHINE,
        action="compliance_checks_completed",
        summary="Contrôles réglementaires exécutés via sources injectées.",
        outputs={"checks": [check.model_dump(mode="json") for check in checks]},
        sources=[check.source_officielle for check in checks],
    )

    if journal is not None:
        journal.append(
            actor=ActorType.MACHINE,
            action="cli.compliance_report_generated",
            payload={
                "chain_id": outcome.decision_chain.chain_id,
                "checks": [check.model_dump(mode="json") for check in checks],
                "journal_integrity": journal.verify_integrity(),
            },
            sources=[check.source_officielle for check in checks],
        )

    if args.json:
        print(
            json.dumps(
                {
                    "classification": outcome.model_dump(mode="json"),
                    "compliance_checks": [check.model_dump(mode="json") for check in checks],
                    "disclaimer": LEGAL_DISCLAIMER,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(_format_report(outcome, checks, journal_path=None if journal is None else Path(args.journal_path)))

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construit le parseur d'arguments CLI."""
    parser = argparse.ArgumentParser(
        prog="python -m agents.compliance",
        description="Chaîne assistée de classification douanière et conformité réglementaire.",
    )
    parser.add_argument("description", help="Description libre du produit.")
    parser.add_argument("--json", action="store_true", help="Afficher le rapport en JSON.")
    parser.add_argument(
        "--journal-path",
        default="audit/compliance_journal.jsonl",
        help="Chemin du journal d'audit append-only JSONL.",
    )
    parser.add_argument("--no-journal", action="store_true", help="Désactiver l'écriture du journal d'audit.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Point d'entrée CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return asyncio.run(run_cli_async(args))
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"Erreur conformité: {exc}", file=sys.stderr)
        return 1


def _format_report(
    outcome: ClassificationOutcome,
    checks: list[ComplianceCheck],
    *,
    journal_path: Path | None,
) -> str:
    """Formate un rapport texte structuré."""
    lines: list[str] = []
    product = outcome.product

    lines.append("IMPORTEXPORT PRO — RAPPORT CONFORMITÉ DOUANIÈRE")
    lines.append("=" * 58)
    lines.append(f"DISCLAIMER: {LEGAL_DISCLAIMER}")
    lines.append("")
    lines.append("PRODUIT")
    lines.append(f"- Nom: {product.name}")
    lines.append(f"- Usage principal: {product.primary_use or 'INCONNU'}")
    lines.append(f"- Composition: {', '.join(product.material_composition) if product.material_composition else 'INCONNUE'}")
    lines.append(f"- Origine: {product.country_origin or 'INCONNUE'}")
    lines.append(f"- Import: {product.country_import or 'INCONNU'}")
    if product.components:
        lines.append(f"- Composants: {', '.join(product.components)}")
    if product.technical_specs:
        lines.append(f"- Spécifications: {json.dumps(product.technical_specs, ensure_ascii=False)}")

    lines.append("")
    lines.append("CLASSIFICATION ASSISTÉE")
    lines.append(f"- Recommandation: {outcome.recommendation}")

    if outcome.selected_proposal is not None:
        proposal = outcome.selected_proposal
        lines.append(f"- Proposition retenue: {proposal.hs_code} — {proposal.title or 'libellé à vérifier'}")
        lines.append(f"- Confiance: {proposal.confidence_level.value} ({proposal.confidence_score:.2f})")
        lines.append(f"- Justification: {proposal.justification}")
        if proposal.assumptions:
            lines.append("- Hypothèses:")
            lines.extend(f"  • {item}" for item in proposal.assumptions)
        if proposal.risk_flags:
            lines.append("- Risques / vigilances:")
            lines.extend(f"  • {item}" for item in proposal.risk_flags)
        if proposal.missing_data:
            lines.append("- Données manquantes améliorant la confiance:")
            lines.extend(f"  • {item}" for item in proposal.missing_data)
        lines.append("- Sources citées:")
        for source in proposal.sources:
            lines.append(f"  • {source.name}: {source.url} ({source.reference or 'référence générale'})")
    else:
        lines.append("- Aucun code utilisable n'est fourni.")
        if outcome.escalation_ticket:
            lines.append(f"- Ticket escalade: {outcome.escalation_ticket.ticket_id}")
            lines.append(f"- Motif: {outcome.escalation_ticket.reason}")
            lines.append("- Données à collecter:")
            lines.extend(f"  • {item}" for item in outcome.escalation_ticket.missing_data)

    if outcome.proposals and outcome.selected_proposal is None:
        lines.append("- Candidats non utilisables sans expert:")
        for proposal in outcome.proposals:
            lines.append(f"  • {proposal.hs_code}: confiance {proposal.confidence_level.value} ({proposal.confidence_score:.2f})")

    lines.append("")
    lines.append("CONTRÔLES RÉGLEMENTAIRES")
    for check in checks:
        lines.append(f"- {check.area.value}: {check.status.value}")
        lines.append(f"  Recommandation: {check.recommendation}")
        lines.append(f"  Source: {check.source_officielle.name} — {check.source_officielle.url}")
        if check.applicable_regulations:
            lines.append(f"  Références: {'; '.join(check.applicable_regulations)}")

    lines.append("")
    lines.append("AUDIT TRAIL")
    lines.append(f"- Decision chain: {outcome.decision_chain.chain_id}")
    lines.append(f"- Étapes tracées: {len(outcome.decision_chain.steps)}")
    if journal_path is not None:
        lines.append(f"- Journal: {journal_path}")
    lines.append("")
    lines.append(f"DISCLAIMER FINAL: {LEGAL_DISCLAIMER}")
    return "\n".join(lines)


def _extract_after_keywords(raw: str, keywords: list[str]) -> str | None:
    pattern = r"(?:^|[,;])\s*(?:" + "|".join(re.escape(keyword) for keyword in keywords) + r")\s*[:=]?\s*([^,;]+)"
    match = re.search(pattern, raw, flags=re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip()
    value = re.sub(r"^(de|du|en|vers|pour)\s+", "", value, flags=re.IGNORECASE).strip()
    return value or None


def _extract_materials(raw: str) -> list[str]:
    materials: list[str] = []
    known = [
        "coton",
        "polyester",
        "polyamide",
        "acier",
        "aluminium",
        "cuir",
        "plastique",
        "pvc",
        "bois",
        "verre",
        "caoutchouc",
        "silicone",
        "r410a",
    ]
    lower = raw.lower()
    for material in known:
        if material in lower:
            percent_match = re.search(rf"(\d{{1,3}}\s*%\s*)?{re.escape(material)}", raw, flags=re.IGNORECASE)
            materials.append(percent_match.group(0).strip() if percent_match else material)
    return _deduplicate(materials)


def _extract_components(raw: str) -> list[str]:
    components: list[str] = []
    known = [
        "compresseur",
        "batterie",
        "moteur",
        "circuit",
        "carte électronique",
        "écran",
        "chargeur",
        "télécommande",
        "pompe",
        "ventilateur",
        "filtre",
    ]
    lower = raw.lower()
    for component in known:
        if component in lower:
            components.append(component)
    return _deduplicate(components)


def _extract_certifications(raw: str) -> list[str]:
    certifications: list[str] = []
    for token in ["CE", "RoHS", "REACH", "RTC", "BTI", "FCC", "EN "]:
        if token.lower() in raw.lower():
            certifications.append(token.strip())
    return _deduplicate(certifications)


def _extract_technical_specs(raw: str) -> dict[str, str]:
    specs: dict[str, str] = {}
    refrigerant = re.search(r"\bR\d{2,4}[A-Z]?\b", raw, flags=re.IGNORECASE)
    if refrigerant:
        specs["fluide_frigorigene"] = refrigerant.group(0).upper()

    voltage = re.search(r"\b(\d{2,4})\s?V\b", raw, flags=re.IGNORECASE)
    if voltage:
        specs["tension"] = voltage.group(0).upper().replace(" ", "")

    power = re.search(r"\b(\d+(?:[.,]\d+)?)\s?(W|kW)\b", raw, flags=re.IGNORECASE)
    if power:
        specs["puissance"] = power.group(0).replace(",", ".")

    return specs


def _deduplicate(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = " ".join(item.strip().split()).lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(item.strip())
    return result


if __name__ == "__main__":
    raise SystemExit(main())
