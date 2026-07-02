"""Chaîne de classification douanière assistée.

Le classificateur ne prétend jamais « donner le bon code HS ». Il génère des
propositions candidates, calcule une confiance explicable, cite les sources et
escalade lorsque les données sont insuffisantes ou le risque trop élevé.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any

from .models import (
    LEGAL_DISCLAIMER,
    ActorType,
    ClassificationOutcome,
    ClassificationProposal,
    ConfidenceLevel,
    DecisionChain,
    EscalationTicket,
    OfficialSource,
    ProductDescription,
    SourceKind,
)
from .sources import RegulatoryQuery, SourceRegistry


class LLMProvider(ABC):
    """Interface d'injection pour un fournisseur LLM.

    Une implémentation de production peut appeler un LLM, un RAG validé ou un
    moteur interne, mais elle doit rester injectée et testable.
    """

    @abstractmethod
    async def generate_classification_candidates(
        self,
        product: ProductDescription,
        *,
        max_candidates: int = 3,
    ) -> list[ClassificationProposal]:
        """Génère entre zéro et ``max_candidates`` propositions candidates."""


class HeuristicLLMProvider(LLMProvider):
    """Fournisseur déterministe local utilisé par défaut.

    Il simule le point d'injection LLM sans appel externe. Les règles sont
    volontairement prudentes et produisent des candidats seulement lorsque des
    familles de produits reconnaissables existent.
    """

    async def generate_classification_candidates(
        self,
        product: ProductDescription,
        *,
        max_candidates: int = 3,
    ) -> list[ClassificationProposal]:
        await asyncio.sleep(0)
        text = product.all_text()
        candidates: list[ClassificationProposal] = []

        if _contains_any(text, ["climatiseur", "air conditioner", "conditionnement d'air", "pompe à chaleur"]):
            candidates.extend(
                [
                    ClassificationProposal(
                        hs_code="841510",
                        title="Machines de conditionnement d'air de type fenêtre/mur ou systèmes autonomes similaires",
                        confidence_level=ConfidenceLevel.MEDIUM,
                        confidence_score=0.52,
                        source=SourceKind.WCO,
                        justification=(
                            "Le produit semble être une machine de conditionnement d'air avec ventilation et "
                            "éléments de modification de la température/humidité. La sous-position dépend de "
                            "la construction exacte : monobloc, split, fenêtre/mur, autre."
                        ),
                        assumptions=[
                            "l'appareil incorpore un groupe frigorifique complet",
                            "l'usage principal est le conditionnement d'air",
                            "le modèle portable est assimilable à un appareil autonome uniquement si la conception le confirme",
                        ],
                        risk_flags=[
                            "distinction sensible entre 8415.10 et autres sous-positions 8415",
                            "présence de fluide frigorigène pouvant déclencher exigences F-gas",
                        ],
                    ),
                    ClassificationProposal(
                        hs_code="841582",
                        title="Autres machines de conditionnement d'air incorporant un dispositif de réfrigération",
                        confidence_level=ConfidenceLevel.MEDIUM,
                        confidence_score=0.47,
                        source=SourceKind.WCO,
                        justification=(
                            "Alternative si l'appareil n'entre pas dans les formes spécifiques fenêtre/mur ou "
                            "systèmes explicitement couverts par une sous-position plus précise."
                        ),
                        assumptions=[
                            "l'appareil incorpore un dispositif frigorifique",
                            "la documentation technique ne justifie pas une sous-position plus spécifique",
                        ],
                        risk_flags=["classification dépendante de la note technique et de la configuration physique"],
                    ),
                ]
            )

        elif _contains_any(text, ["t-shirt", "tee shirt", "maillot de corps"]):
            knitted = _contains_any(text, ["tricot", "bonneterie", "knitted", "jersey"])
            cotton = _contains_any(text, ["coton", "cotton"])
            synthetic = _contains_any(text, ["polyester", "polyamide", "synthetic", "synthétique"])
            if knitted and cotton:
                code = "610910"
                title = "T-shirts et maillots de corps, en bonneterie, de coton"
            elif knitted and synthetic:
                code = "610990"
                title = "T-shirts et maillots de corps, en bonneterie, d'autres matières textiles"
            else:
                code = "610990"
                title = "T-shirts et maillots de corps, composition ou construction à confirmer"
            candidates.append(
                ClassificationProposal(
                    hs_code=code,
                    title=title,
                    confidence_level=ConfidenceLevel.MEDIUM,
                    confidence_score=0.62 if knitted and (cotton or synthetic) else 0.50,
                    source=SourceKind.WCO,
                    justification=(
                        "Le libellé et l'usage indiquent un t-shirt. Le classement textile dépend de la "
                        "construction bonneterie/non bonneterie, de la composition majoritaire et du type de vêtement."
                    ),
                    assumptions=[
                        "le produit est un vêtement fini",
                        "la matière déclarée correspond à la composition réelle",
                        "absence d'éléments transformant la fonction principale du vêtement",
                    ],
                )
            )

        elif _contains_any(text, ["chemise", "shirt"]) and _contains_any(text, ["coton", "cotton"]):
            candidates.append(
                ClassificationProposal(
                    hs_code="620520",
                    title="Chemises pour hommes ou garçonnets, de coton, hors bonneterie",
                    confidence_level=ConfidenceLevel.MEDIUM,
                    confidence_score=0.50,
                    source=SourceKind.WCO,
                    justification=(
                        "La présence du terme chemise et coton suggère une position textile, mais le genre, "
                        "la coupe et la construction bonneterie/non bonneterie doivent être confirmés."
                    ),
                    assumptions=["chemise non en bonneterie", "chemise destinée aux hommes ou garçonnets"],
                    risk_flags=["le classement varie selon genre, bonneterie et caractéristiques du vêtement"],
                )
            )

        elif _contains_any(text, ["lampe led", "led lamp", "luminaire", "lighting fixture"]):
            candidates.append(
                ClassificationProposal(
                    hs_code="940540",
                    title="Appareils d'éclairage électriques, autres appareils d'éclairage",
                    confidence_level=ConfidenceLevel.MEDIUM,
                    confidence_score=0.50,
                    source=SourceKind.WCO,
                    justification=(
                        "Le produit semble avoir pour fonction principale l'éclairage. Le classement dépend "
                        "de la forme, du montage, de l'alimentation et des composants."
                    ),
                    assumptions=["fonction principale d'éclairage", "produit fini et non simple composant LED"],
                    risk_flags=["distinction entre composant électrique et luminaire complet"],
                )
            )

        elif _contains_any(text, ["smartphone", "téléphone mobile", "telephone mobile", "mobile phone"]):
            candidates.append(
                ClassificationProposal(
                    hs_code="851713",
                    title="Smartphones pour réseaux cellulaires ou autres réseaux sans fil",
                    confidence_level=ConfidenceLevel.MEDIUM,
                    confidence_score=0.58,
                    source=SourceKind.WCO,
                    justification=(
                        "La fonction principale semble être la téléphonie mobile intelligente. Les caractéristiques "
                        "radio, modem et connectivité doivent être documentées."
                    ),
                    assumptions=["appareil complet", "fonction principale de téléphonie mobile"],
                    risk_flags=["contrôles radio, batteries, chargeurs et conformité CE/RoHS associés"],
                )
            )

        elif _contains_any(text, ["jouet", "toy"]):
            candidates.append(
                ClassificationProposal(
                    hs_code="950300",
                    title="Tricycles, trottinettes, jouets et modèles réduits",
                    confidence_level=ConfidenceLevel.MEDIUM,
                    confidence_score=0.48,
                    source=SourceKind.WCO,
                    justification=(
                        "Le produit est décrit comme jouet. Le classement exige de confirmer qu'il est conçu "
                        "principalement pour l'amusement des enfants et non comme article fonctionnel."
                    ),
                    assumptions=["fonction principale ludique", "produit destiné aux enfants"],
                    risk_flags=["sécurité jouets, marquage CE et restrictions chimiques"],
                )
            )

        elif _contains_any(text, ["chaussure", "shoe", "sneaker", "basket"]):
            candidates.extend(
                [
                    ClassificationProposal(
                        hs_code="640419",
                        title="Chaussures à semelles extérieures en caoutchouc/plastique et dessus textile",
                        confidence_level=ConfidenceLevel.MEDIUM,
                        confidence_score=0.46,
                        source=SourceKind.WCO,
                        justification="Famille chaussure détectée ; le classement dépend des matériaux semelle/dessus.",
                        assumptions=["dessus textile", "semelle extérieure caoutchouc ou plastique"],
                        risk_flags=["composition semelle/dessus indispensable"],
                    ),
                    ClassificationProposal(
                        hs_code="640399",
                        title="Chaussures à semelles extérieures caoutchouc/plastique/cuir et dessus cuir",
                        confidence_level=ConfidenceLevel.LOW,
                        confidence_score=0.42,
                        source=SourceKind.WCO,
                        justification="Alternative si le dessus est en cuir naturel.",
                        assumptions=["dessus en cuir naturel"],
                        risk_flags=["matière du dessus non confirmée"],
                    ),
                ]
            )

        elif _contains_any(text, ["article plastique", "plastique", "plastic"]) and _contains_any(
            text, ["accessoire", "support", "boîtier", "case", "holder"]
        ):
            candidates.append(
                ClassificationProposal(
                    hs_code="392690",
                    title="Autres ouvrages en matières plastiques",
                    confidence_level=ConfidenceLevel.LOW,
                    confidence_score=0.38,
                    source=SourceKind.WCO,
                    justification=(
                        "Un ouvrage plastique générique est possible, mais ce code résiduel ne doit pas être "
                        "utilisé sans confirmer qu'aucune position plus spécifique ne couvre la fonction."
                    ),
                    assumptions=["matière principale plastique", "aucune fonction mécanique/électrique spécifique"],
                    risk_flags=["code résiduel à haut risque", "fonction principale non suffisamment documentée"],
                )
            )

        return candidates[:max_candidates]


async def classify_product(
    product: ProductDescription,
    *,
    llm_provider: LLMProvider | None = None,
    source_registry: SourceRegistry | None = None,
    high_threshold: float = 0.78,
    low_threshold: float = 0.45,
    audit_journal: Any | None = None,
) -> ClassificationOutcome:
    """Exécute la chaîne de classification assistée.

    La fonction retourne toujours un disclaimer légal et n'affirme jamais qu'un
    code proposé est définitivement correct.
    """
    if not 0.0 <= low_threshold < high_threshold <= 1.0:
        raise ValueError("Les seuils doivent respecter 0 <= low_threshold < high_threshold <= 1.")

    provider = llm_provider or HeuristicLLMProvider()
    registry = source_registry or SourceRegistry.default()
    decision_chain = DecisionChain(product=product)

    decision_chain.add_step(
        actor=ActorType.MACHINE,
        action="ingestion_product_description",
        summary="Description produit structurée reçue pour classification assistée.",
        inputs={"product": product.model_dump(mode="json")},
        outputs={"missing_critical_fields": product.critical_missing_fields()},
    )
    _journal_append(
        audit_journal,
        actor=ActorType.MACHINE,
        action="classification.ingestion",
        payload={"chain_id": decision_chain.chain_id, "product": product.model_dump(mode="json")},
    )

    raw_candidates = await provider.generate_classification_candidates(product, max_candidates=3)
    decision_chain.add_step(
        actor=ActorType.MACHINE,
        action="generate_classification_candidates",
        summary=f"{len(raw_candidates)} proposition(s) candidate(s) générée(s) par le fournisseur injecté.",
        outputs={"candidate_count": len(raw_candidates)},
    )

    if not raw_candidates:
        missing_data = _deduplicate(
            product.critical_missing_fields()
            + [
                "description fonctionnelle détaillée",
                "matière principale et composants",
                "photos et fiche technique du fabricant",
            ]
        )
        ticket = _build_escalation_ticket(
            product=product,
            proposals=[],
            missing_data=missing_data,
            reason=(
                "Informations insuffisantes pour générer une proposition de code sans risque excessif. "
                "Le module refuse de fournir un code exploitable."
            ),
            priority="high",
        )
        decision_chain.escalation_ticket = ticket
        decision_chain.add_step(
            actor=ActorType.MACHINE,
            action="escalate_no_candidate",
            summary="Aucune proposition fiable ne peut être générée ; escalade obligatoire.",
            outputs={"ticket": ticket.model_dump(mode="json")},
        )
        _journal_append(
            audit_journal,
            actor=ActorType.MACHINE,
            action="classification.escalation",
            payload={"chain_id": decision_chain.chain_id, "ticket": ticket.model_dump(mode="json")},
        )
        return ClassificationOutcome(
            product=product,
            decision_chain=decision_chain,
            proposals=[],
            selected_proposal=None,
            escalation_ticket=ticket,
            missing_data=missing_data,
            recommendation=(
                "Classification refusée : transmettez le dossier à un expert douane, un transitaire ou un "
                "courtier en douane. Préparez les données manquantes et envisagez une demande de RTC."
            ),
            disclaimer=LEGAL_DISCLAIMER,
        )

    enriched_candidates: list[ClassificationProposal] = []
    for candidate in raw_candidates:
        await _enrich_candidate_sources(candidate, product, registry)
        score, missing_data, risk_flags = _compute_confidence(
            product=product,
            proposal=candidate,
            candidate_count=len(raw_candidates),
        )
        candidate.confidence_score = score
        candidate.confidence_level = _confidence_level(score, high_threshold=high_threshold, low_threshold=low_threshold)
        candidate.missing_data = _deduplicate(candidate.missing_data + missing_data)
        candidate.risk_flags = _deduplicate(candidate.risk_flags + risk_flags)
        enriched_candidates.append(candidate)

    enriched_candidates.sort(key=lambda proposal: proposal.confidence_score, reverse=True)
    top = enriched_candidates[0]
    decision_chain.classification_proposals = enriched_candidates
    all_sources = _deduplicate_sources([source for proposal in enriched_candidates for source in proposal.sources])

    decision_chain.add_step(
        actor=ActorType.MACHINE,
        action="score_classification_candidates",
        summary="Scores de confiance calculés avec règles explicites.",
        outputs={
            "scores": [
                {
                    "hs_code": proposal.hs_code,
                    "confidence_score": proposal.confidence_score,
                    "confidence_level": proposal.confidence_level.value,
                    "missing_data": proposal.missing_data,
                    "risk_flags": proposal.risk_flags,
                }
                for proposal in enriched_candidates
            ],
            "high_threshold": high_threshold,
            "low_threshold": low_threshold,
        },
        sources=all_sources,
    )
    _journal_append(
        audit_journal,
        actor=ActorType.MACHINE,
        action="classification.scoring",
        payload={
            "chain_id": decision_chain.chain_id,
            "scores": [
                {
                    "hs_code": proposal.hs_code,
                    "confidence_score": proposal.confidence_score,
                    "confidence_level": proposal.confidence_level.value,
                }
                for proposal in enriched_candidates
            ],
        },
        sources=all_sources,
    )

    if top.confidence_score >= high_threshold:
        decision_chain.selected_proposal = top
        recommendation = (
            "Proposition de classification à confiance haute, utilisable comme aide documentée sous réserve de "
            "validation interne et conservation des sources. Ne pas la présenter comme vérité absolue."
        )
        decision_chain.add_step(
            actor=ActorType.MACHINE,
            action="classification_high_confidence",
            summary="Une proposition atteint le seuil haut de confiance.",
            outputs={"selected_proposal": top.model_dump(mode="json"), "disclaimer": LEGAL_DISCLAIMER},
            sources=top.sources,
        )
        return ClassificationOutcome(
            product=product,
            decision_chain=decision_chain,
            proposals=enriched_candidates,
            selected_proposal=top,
            escalation_ticket=None,
            missing_data=top.missing_data,
            recommendation=recommendation,
            disclaimer=LEGAL_DISCLAIMER,
        )

    if top.confidence_score >= low_threshold:
        recommendation = (
            "Confiance intermédiaire : ne pas figer le code sans compléter les données manquantes. "
            "Demander un RTC si l'enjeu financier, réglementaire ou opérationnel est significatif."
        )
        decision_chain.selected_proposal = top
        decision_chain.add_step(
            actor=ActorType.MACHINE,
            action="classification_medium_confidence",
            summary="Proposition(s) candidate(s) fournies avec données manquantes et recommandation RTC.",
            outputs={
                "top_proposal": top.model_dump(mode="json"),
                "missing_data": top.missing_data,
                "recommendation": recommendation,
            },
            sources=top.sources,
        )
        return ClassificationOutcome(
            product=product,
            decision_chain=decision_chain,
            proposals=enriched_candidates,
            selected_proposal=top,
            escalation_ticket=None,
            missing_data=top.missing_data,
            recommendation=recommendation,
            disclaimer=LEGAL_DISCLAIMER,
        )

    missing_data = _deduplicate(
        top.missing_data
        + product.critical_missing_fields()
        + [
            "notes explicatives SH applicables",
            "recherche RTC/BTI comparable",
            "avis d'un expert sur la fonction principale",
        ]
    )
    ticket = _build_escalation_ticket(
        product=product,
        proposals=enriched_candidates,
        missing_data=missing_data,
        reason=(
            "Score de confiance inférieur au seuil minimal. Le module refuse de fournir un code utilisable "
            "et escalade vers un expert."
        ),
        priority="high",
    )
    decision_chain.escalation_ticket = ticket
    decision_chain.add_step(
        actor=ActorType.MACHINE,
        action="classification_low_confidence_escalation",
        summary="Confiance insuffisante ; aucun code ne doit être utilisé sans expert.",
        outputs={"ticket": ticket.model_dump(mode="json")},
        sources=all_sources,
    )
    _journal_append(
        audit_journal,
        actor=ActorType.MACHINE,
        action="classification.escalation",
        payload={"chain_id": decision_chain.chain_id, "ticket": ticket.model_dump(mode="json")},
        sources=all_sources,
    )

    return ClassificationOutcome(
        product=product,
        decision_chain=decision_chain,
        proposals=enriched_candidates,
        selected_proposal=None,
        escalation_ticket=ticket,
        missing_data=missing_data,
        recommendation=(
            "Classification refusée en raison d'une confiance insuffisante. Escaladez vers un expert et "
            "complétez les informations listées. Envisagez une demande de RTC."
        ),
        disclaimer=LEGAL_DISCLAIMER,
    )


def classify_product_sync(
    product: ProductDescription,
    *,
    llm_provider: LLMProvider | None = None,
    source_registry: SourceRegistry | None = None,
    high_threshold: float = 0.78,
    low_threshold: float = 0.45,
    audit_journal: Any | None = None,
) -> ClassificationOutcome:
    """Version synchrone de commodité pour scripts et tests simples."""
    return asyncio.run(
        classify_product(
            product,
            llm_provider=llm_provider,
            source_registry=source_registry,
            high_threshold=high_threshold,
            low_threshold=low_threshold,
            audit_journal=audit_journal,
        )
    )


async def _enrich_candidate_sources(
    proposal: ClassificationProposal,
    product: ProductDescription,
    registry: SourceRegistry,
) -> None:
    """Ajoute les citations officielles pertinentes à une proposition."""
    query = RegulatoryQuery(
        area="classification",
        product=product,
        hs_code=proposal.hs_code,
        country_origin=product.country_origin,
        country_import=product.country_import,
    )
    responses = await registry.query_many(["wco_hs", "taric", "douane_fr"], query)
    sources: list[OfficialSource] = list(proposal.sources)

    for response in responses:
        source = response.source
        if response.references:
            source = source.model_copy(update={"reference": "; ".join(response.references[:3])})
        if response.summary:
            source = source.model_copy(update={"excerpt": response.summary})
        sources.append(source)

    if _has_rtc_signal(product):
        sources.append(
            OfficialSource(
                name="RTC/BTI fourni par l'utilisateur",
                url="https://www.douane.gouv.fr/",
                source_type=SourceKind.RTC,
                reference="Référence RTC/BTI déclarée - vérification officielle requise",
                excerpt="La présence d'un RTC/BTI augmente la confiance seulement si le produit est strictement identique.",
            )
        )

    proposal.sources = _deduplicate_sources(sources)


def _compute_confidence(
    *,
    product: ProductDescription,
    proposal: ClassificationProposal,
    candidate_count: int,
) -> tuple[float, list[str], list[str]]:
    """Calcule un score de confiance explicable.

    Facteurs pris en compte :
    - précision de la composition ;
    - clarté de l'usage principal ;
    - pays d'origine et d'importation ;
    - présence de composants, fiche technique, images ;
    - existence déclarée d'un RTC/BTI ou d'une jurisprudence comparable ;
    - nombre de candidats concurrents ;
    - signaux de vague, kit, assortiment ou produit composite.
    """
    score = proposal.confidence_score
    missing = product.critical_missing_fields()
    risks: list[str] = []

    text = product.all_text()

    if product.material_composition:
        score += 0.12
        if any(any(char.isdigit() for char in item) and "%" in item for item in product.material_composition):
            score += 0.05
    else:
        score -= 0.10

    if product.primary_use and len(product.primary_use.strip()) >= 8:
        score += 0.12
    else:
        score -= 0.08

    if product.country_import:
        score += 0.06
    else:
        score -= 0.06

    if product.country_origin:
        score += 0.04
    else:
        score -= 0.04

    if product.images:
        score += 0.03

    if product.components or product.technical_specs:
        score += 0.06
        if _technical_family_requires_specs(text) and product.technical_specs:
            score += 0.04
    elif _technical_family_requires_specs(text):
        score -= 0.08
        risks.append("produit technique sans fiche technique exploitable")

    if product.known_certifications:
        score += 0.02

    if _has_rtc_signal(product):
        score += 0.16
    else:
        risks.append("aucun RTC/BTI comparable fourni")

    if candidate_count > 1:
        penalty = min(0.12, 0.05 + 0.03 * (candidate_count - 2))
        score -= penalty
        risks.append("plusieurs positions candidates plausibles")

    if _contains_any(text, ["kit", "set", "assortiment", "multifonction", "accessoire universel", "multi-usage"]):
        score -= 0.12
        risks.append("description vague, kit, assortiment ou produit multifonction")

    if proposal.hs_code.startswith(("3926", "8543")):
        score -= 0.05
        risks.append("position potentiellement résiduelle : rechercher une position plus spécifique")

    if _contains_any(text, ["r410a", "réfrigérant", "refrigerant", "gaz fluoré"]):
        risks.append("gaz fluoré ou fluide frigorigène : conformité F-gas à contrôler séparément")

    if _contains_any(text, ["composite", "mélange", "assemblage", "avec accessoires"]):
        score -= 0.05
        risks.append("produit composite : appliquer les règles générales interprétatives, notamment RGI 3")

    score = max(0.0, min(1.0, round(score, 4)))
    return score, _deduplicate(missing), _deduplicate(risks)


def _confidence_level(score: float, *, high_threshold: float, low_threshold: float) -> ConfidenceLevel:
    if score >= high_threshold:
        return ConfidenceLevel.HIGH
    if score >= low_threshold:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def _build_escalation_ticket(
    *,
    product: ProductDescription,
    proposals: list[ClassificationProposal],
    missing_data: list[str],
    reason: str,
    priority: str,
) -> EscalationTicket:
    """Construit un ticket d'escalade complet."""
    return EscalationTicket(
        reason=reason,
        destination="expert_humain",
        product=product,
        proposals=proposals,
        missing_data=_deduplicate(missing_data),
        priority=priority,  # type: ignore[arg-type]
        recommended_actions=[
            "Collecter fiche technique fabricant, photos, schéma, manuel et composition exacte.",
            "Identifier la fonction principale et l'usage réel prévu à l'importation.",
            "Rechercher les notes explicatives SH, décisions de classement et RTC/BTI comparables.",
            "Consulter un expert douane, transitaire ou courtier en douane.",
            "Demander un RTC lorsque le risque financier ou réglementaire le justifie.",
        ],
    )


def _contains_any(text: str, needles: list[str]) -> bool:
    return any(needle.lower() in text for needle in needles)


def _technical_family_requires_specs(text: str) -> bool:
    return _contains_any(
        text,
        [
            "électrique",
            "electronique",
            "électronique",
            "machine",
            "moteur",
            "compresseur",
            "climatiseur",
            "smartphone",
            "batterie",
            "radio",
            "led",
            "réfrigérant",
            "r410a",
        ],
    )


def _has_rtc_signal(product: ProductDescription) -> bool:
    text = product.all_text()
    return _contains_any(text, ["rtc", "bti", "renseignement tarifaire contraignant", "binding tariff information"])


def _deduplicate(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        normalized = " ".join(item.strip().split()).lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            output.append(item.strip())
    return output


def _deduplicate_sources(sources: list[OfficialSource]) -> list[OfficialSource]:
    seen: set[tuple[str, str, str | None]] = set()
    output: list[OfficialSource] = []
    for source in sources:
        key = (source.name, source.url, source.reference)
        if key not in seen:
            seen.add(key)
            output.append(source)
    return output


def _journal_append(
    audit_journal: Any | None,
    *,
    actor: ActorType,
    action: str,
    payload: dict[str, Any],
    sources: list[OfficialSource] | None = None,
) -> None:
    """Ajoute au journal si une instance compatible est injectée."""
    if audit_journal is None:
        return
    append = getattr(audit_journal, "append", None)
    if append is None:
        raise TypeError("audit_journal doit exposer une méthode append(...).")
    append(actor=actor, action=action, payload=payload, sources=sources or [])
