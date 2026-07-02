"""Contrôles réglementaires douaniers et produit.

Chaque contrôle cite une source officielle via l'interface ``RegulatorySource``.
Les résultats sont prudents : en cas d'incertitude, le statut est ``unknown`` ou
``requires_expert`` plutôt qu'un faux ``pass``.
"""

from __future__ import annotations

import asyncio

from .models import (
    LEGAL_DISCLAIMER,
    ClassificationProposal,
    ComplianceArea,
    ComplianceCheck,
    ComplianceStatus,
    OfficialSource,
    ProductDescription,
    SourceKind,
)
from .sources import RegulatoryQuery, SourceRegistry


async def check_ce_marking(
    product: ProductDescription,
    *,
    source_registry: SourceRegistry | None = None,
) -> ComplianceCheck:
    """Vérifie si le marquage CE semble obligatoire et documenté."""
    registry = source_registry or SourceRegistry.default()
    response = await registry.query("eur_lex", RegulatoryQuery(area="CE", product=product))
    text = product.all_text()
    ce_required = bool(response.data.get("ce_likely_required")) or _contains_any(
        text,
        ["climatiseur", "machine", "électrique", "electrical", "jouet", "radio", "batterie", "led"],
    )
    has_ce = _has_certification(product, ["ce", "déclaration ue de conformité", "declaration of conformity", "doc"])

    if ce_required and has_ce:
        status = ComplianceStatus.PASS
        recommendation = "Conserver la déclaration UE de conformité, le dossier technique et les rapports d'essai."
        details = "Signal CE obligatoire détecté et certification/document CE déclaré par l'utilisateur."
    elif ce_required:
        status = ComplianceStatus.REQUIRES_EXPERT
        recommendation = (
            "Obtenir la déclaration UE de conformité, identifier les directives/règlements applicables "
            "et vérifier l'étiquetage CE avant importation."
        )
        details = "Le produit semble relever d'une ou plusieurs législations CE, mais le dossier CE n'est pas fourni."
    else:
        status = ComplianceStatus.UNKNOWN
        recommendation = (
            "Aucun signal CE évident avec les données fournies ; confirmer par analyse produit, usage et secteur."
        )
        details = "Le champ d'application CE ne peut pas être exclu sans fiche technique complète."

    return ComplianceCheck(
        area=ComplianceArea.CE_MARKING,
        status=status,
        source_officielle=response.source,
        recommendation=recommendation,
        details=details,
        applicable_regulations=response.references,
        disclaimer=LEGAL_DISCLAIMER,
    )


async def check_rohs(
    product: ProductDescription,
    *,
    source_registry: SourceRegistry | None = None,
) -> ComplianceCheck:
    """Vérifie le risque RoHS pour équipements électriques et électroniques."""
    registry = source_registry or SourceRegistry.default()
    response = await registry.query("eur_lex", RegulatoryQuery(area="RoHS", product=product))
    eee_scope = bool(response.data.get("eee_scope_signal")) or _is_electrical_or_electronic(product)
    has_rohs = _has_certification(product, ["rohs", "directive 2011/65", "2015/863"])

    if eee_scope and has_rohs:
        status = ComplianceStatus.PASS
        recommendation = "Archiver la déclaration RoHS, les rapports matière et la traçabilité fournisseur."
        details = "Produit dans le champ EEE avec conformité RoHS déclarée."
    elif eee_scope:
        status = ComplianceStatus.REQUIRES_EXPERT
        recommendation = (
            "Exiger une déclaration RoHS conforme, nomenclature matière et preuves d'essai pour plomb, mercure, "
            "cadmium, chrome VI, PBB, PBDE et phtalates restreints."
        )
        details = "Produit probablement EEE, mais conformité RoHS non documentée."
    else:
        status = ComplianceStatus.PASS
        recommendation = "RoHS ne semble pas applicable selon les informations fournies ; conserver l'analyse d'exclusion."
        details = "Aucun signal d'équipement électrique ou électronique."

    return ComplianceCheck(
        area=ComplianceArea.ROHS,
        status=status,
        source_officielle=response.source,
        recommendation=recommendation,
        details=details,
        applicable_regulations=response.references,
    )


async def check_reach(
    product: ProductDescription,
    *,
    source_registry: SourceRegistry | None = None,
) -> ComplianceCheck:
    """Vérifie les obligations REACH connues ou suspectées."""
    registry = source_registry or SourceRegistry.default()
    response = await registry.query("eur_lex", RegulatoryQuery(area="REACH", product=product))
    chemical_signal = bool(response.data.get("chemical_signal"))
    has_reach = _has_certification(product, ["reach", "svhc", "echa"])

    if has_reach:
        status = ComplianceStatus.PASS
        recommendation = (
            "Conserver déclaration REACH/SVHC, date de la liste candidate utilisée et preuves fournisseur."
        )
        details = "Conformité REACH/SVHC déclarée par l'utilisateur."
    elif chemical_signal:
        status = ComplianceStatus.REQUIRES_EXPERT
        recommendation = (
            "Analyser substances, mélanges, articles et SVHC. Vérifier obligations d'enregistrement, "
            "restriction annexe XVII et communication SCIP si applicable."
        )
        details = "Signal chimique ou substance sensible détecté."
    elif not product.material_composition:
        status = ComplianceStatus.UNKNOWN
        recommendation = (
            "Obtenir la composition matière/substances et une déclaration SVHC à jour du fournisseur."
        )
        details = "REACH s'applique largement aux substances et articles ; composition absente."
    else:
        status = ComplianceStatus.UNKNOWN
        recommendation = (
            "Vérifier auprès du fournisseur l'absence de SVHC au-dessus de 0,1 % masse/masse et restrictions annexe XVII."
        )
        details = "Pas de signal chimique majeur, mais REACH ne peut pas être écarté pour un article importé."

    return ComplianceCheck(
        area=ComplianceArea.REACH,
        status=status,
        source_officielle=response.source,
        recommendation=recommendation,
        details=details,
        applicable_regulations=response.references,
    )


async def check_sanctions(
    product: ProductDescription,
    *,
    source_registry: SourceRegistry | None = None,
) -> ComplianceCheck:
    """Vérifie les signaux pays liés aux sanctions commerciales UE."""
    registry = source_registry or SourceRegistry.default()
    response = await registry.query(
        "sanctions_eu",
        RegulatoryQuery(
            area="sanctions",
            product=product,
            country_origin=product.country_origin,
            country_import=product.country_import,
        ),
    )
    restricted_country_signal = bool(response.data.get("restricted_country_signal"))

    if restricted_country_signal:
        status = ComplianceStatus.REQUIRES_EXPERT
        recommendation = (
            "Effectuer un filtrage sanctions complet : pays, contreparties, bénéficiaires effectifs, banques, "
            "transporteurs, route logistique et interdictions sectorielles."
        )
        details = "Signal pays sensible détecté par le bouchon sanctions UE."
    else:
        status = ComplianceStatus.PASS
        recommendation = (
            "Aucun signal pays sensible détecté ; réaliser malgré tout le filtrage nominatif des parties et banques."
        )
        details = "Le contrôle pays ne remplace pas le screening des entités listées."

    return ComplianceCheck(
        area=ComplianceArea.SANCTIONS,
        status=status,
        source_officielle=response.source,
        recommendation=recommendation,
        details=details,
        applicable_regulations=response.references,
    )


async def check_quotas_licenses(
    product: ProductDescription,
    *,
    classification: ClassificationProposal | None = None,
    source_registry: SourceRegistry | None = None,
) -> ComplianceCheck:
    """Vérifie les signaux de quotas, contingents ou licences d'importation."""
    registry = source_registry or SourceRegistry.default()
    hs_code = classification.hs_code if classification else None
    taric_response, a2m_response = await asyncio.gather(
        registry.query("taric", RegulatoryQuery(area="quotas_licenses", product=product, hs_code=hs_code)),
        registry.query("access2markets", RegulatoryQuery(area="quotas_licenses", product=product, hs_code=hs_code)),
    )

    text = product.all_text()
    risk_signals: list[str] = []
    risk_signals.extend(taric_response.data.get("measures_to_verify", []))
    risk_signals.extend(a2m_response.data.get("signals", []))

    if _contains_any(text, ["r410a", "réfrigérant", "refrigerant", "gaz fluoré", "hfc"]):
        risk_signals.append("F-gas : vérifier quotas, autorisations et déclarations pour équipements préchargés.")
    if _contains_any(text, ["acier", "steel", "textile", "agricole", "dual-use", "double usage"]):
        risk_signals.append("Famille produit connue pour mesures quantitatives, surveillance ou licences possibles.")

    if risk_signals:
        status = ComplianceStatus.REQUIRES_EXPERT
        recommendation = (
            "Vérifier dans TARIC/Access2Markets les mesures au code NC/TARIC exact, la date d'importation, "
            "le pays d'origine et le régime douanier. Ne pas expédier avant confirmation."
        )
        details = "Signaux quotas/licences : " + " | ".join(_deduplicate(risk_signals))
    elif hs_code:
        status = ComplianceStatus.UNKNOWN
        recommendation = (
            "Aucun signal déterministe détecté par les bouchons ; confirmer les mesures TARIC au code exact avant déclaration."
        )
        details = "Le contrôle dépend du code TARIC complet, de la date et du pays d'origine."
    else:
        status = ComplianceStatus.UNKNOWN
        recommendation = (
            "Code NC/TARIC absent ou non validé : impossible de conclure sur quotas/licences. Finaliser la classification."
        )
        details = "La plupart des mesures quantitatives sont indexées par code et origine."

    source = _merge_sources(
        primary=taric_response.source,
        secondary=a2m_response.source,
        reference="; ".join(_deduplicate(taric_response.references + a2m_response.references)),
    )
    return ComplianceCheck(
        area=ComplianceArea.QUOTAS_LICENSES,
        status=status,
        source_officielle=source,
        recommendation=recommendation,
        details=details,
        applicable_regulations=_deduplicate(taric_response.references + a2m_response.references),
    )


async def check_documents_required(
    product: ProductDescription,
    *,
    classification: ClassificationProposal | None = None,
    source_registry: SourceRegistry | None = None,
) -> ComplianceCheck:
    """Liste les documents minimaux requis ou généralement attendus."""
    registry = source_registry or SourceRegistry.default()
    response = await registry.query(
        "access2markets",
        RegulatoryQuery(
            area="documents",
            product=product,
            hs_code=classification.hs_code if classification else None,
            country_origin=product.country_origin,
            country_import=product.country_import,
        ),
    )

    docs = response.data.get("baseline_documents", [])
    extra = response.data.get("signals", [])
    status = ComplianceStatus.UNKNOWN
    recommendation = (
        "Préparer au minimum : "
        + ", ".join(docs)
        + ". Ajouter certificats sectoriels et preuves d'origine selon le code, l'origine et l'accord commercial."
    )
    if extra:
        recommendation += " Points spécifiques à vérifier : " + " | ".join(extra)

    return ComplianceCheck(
        area=ComplianceArea.DOCUMENTS,
        status=status,
        source_officielle=response.source,
        recommendation=recommendation,
        details="La présence effective des documents n'est pas contrôlée par ce module ; il liste les exigences à préparer.",
        applicable_regulations=response.references,
    )


async def run_all_compliance_checks(
    product: ProductDescription,
    *,
    classification: ClassificationProposal | None = None,
    source_registry: SourceRegistry | None = None,
) -> list[ComplianceCheck]:
    """Exécute l'ensemble des contrôles réglementaires disponibles."""
    registry = source_registry or SourceRegistry.default()
    return await asyncio.gather(
        check_ce_marking(product, source_registry=registry),
        check_rohs(product, source_registry=registry),
        check_reach(product, source_registry=registry),
        check_sanctions(product, source_registry=registry),
        check_quotas_licenses(product, classification=classification, source_registry=registry),
        check_documents_required(product, classification=classification, source_registry=registry),
    )


def _contains_any(text: str, needles: list[str]) -> bool:
    return any(needle.lower() in text for needle in needles)


def _is_electrical_or_electronic(product: ProductDescription) -> bool:
    text = product.all_text()
    return _contains_any(
        text,
        [
            "électrique",
            "electrical",
            "électronique",
            "electronique",
            "battery",
            "batterie",
            "circuit",
            "led",
            "chargeur",
            "smartphone",
            "climatiseur",
            "compresseur",
            "moteur",
        ],
    )


def _has_certification(product: ProductDescription, needles: list[str]) -> bool:
    cert_text = " ".join(product.known_certifications).lower()
    specs_text = " ".join(f"{k} {v}" for k, v in product.technical_specs.items()).lower()
    return any(needle.lower() in cert_text or needle.lower() in specs_text for needle in needles)


def _deduplicate(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = " ".join(str(item).strip().split()).lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(str(item).strip())
    return result


def _merge_sources(primary: OfficialSource, secondary: OfficialSource, reference: str) -> OfficialSource:
    return OfficialSource(
        name=f"{primary.name} + {secondary.name}",
        url=primary.url,
        source_type=primary.source_type if primary.source_type != SourceKind.OTHER else secondary.source_type,
        reference=reference or primary.reference or secondary.reference,
        excerpt=f"{primary.excerpt or ''} | Source complémentaire : {secondary.url}".strip(),
    )
