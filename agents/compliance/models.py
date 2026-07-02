"""Modèles métier Pydantic v2 pour la conformité douanière.

Les modèles de ce module sont volontairement explicites : une classification
douanière n'est jamais représentée comme une vérité absolue, mais comme une
proposition documentée, sourcée, justifiée et assortie d'un niveau de confiance.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

LEGAL_DISCLAIMER = (
    "Cet outil ASSISTE la classification et la conformité. Il ne remplace pas "
    "l'expert humain. Toute décision douanière engage votre responsabilité."
)


def utc_now() -> datetime:
    """Retourne l'heure courante en UTC avec information de fuseau."""
    return datetime.now(timezone.utc)


class ConfidenceLevel(StrEnum):
    """Niveau de confiance d'une proposition de classification."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SourceKind(StrEnum):
    """Famille de source officielle ou experte citée dans la décision."""

    WCO = "WCO"
    TARIC = "TARIC"
    RTC = "RTC"
    EUR_LEX = "EUR-Lex"
    ACCESS2MARKETS = "Access2Markets"
    DOUANE_FR = "Douanes françaises"
    SANCTIONS_EU = "Sanctions UE"
    EXPERT = "Expert humain"
    TRANSITAIRE = "Transitaire"
    OTHER = "Autre"


class ComplianceStatus(StrEnum):
    """Statut normalisé d'un contrôle de conformité."""

    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    REQUIRES_EXPERT = "requires_expert"


class ComplianceArea(StrEnum):
    """Domaines de conformité couverts par le module."""

    CE_MARKING = "CE"
    ROHS = "RoHS"
    REACH = "REACH"
    SANCTIONS = "Sanctions"
    QUOTAS_LICENSES = "Quotas / licences"
    DOCUMENTS = "Documents requis"
    CLASSIFICATION = "Classification douanière"


class ActorType(StrEnum):
    """Acteur ayant effectué une étape de la chaîne de décision."""

    MACHINE = "machine"
    EXPERT = "expert"
    TRANSITAIRE = "transitaire"
    COURTIER_DOUANE = "courtier_douane"
    IMPORTATEUR = "importateur"
    SYSTEM = "system"


class OfficialSource(BaseModel):
    """Source citée dans une proposition ou un contrôle.

    Les URL référencent des ressources officielles à connecter via intégration
    dédiée. Le module ne réalise pas d'appel réseau en dur.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(..., min_length=1, description="Nom de la source.")
    url: str = Field(..., min_length=1, description="URL officielle.")
    source_type: SourceKind = Field(default=SourceKind.OTHER)
    reference: str | None = Field(
        default=None,
        description="Référence juridique, tarifaire ou administrative précise.",
    )
    excerpt: str | None = Field(
        default=None,
        description="Extrait ou résumé court de la source consultée.",
    )
    retrieved_at: datetime = Field(default_factory=utc_now)

    @field_validator("name", "url", "reference", "excerpt", mode="before")
    @classmethod
    def _strip_optional_strings(cls, value: Any) -> Any:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None if value is not None and value.strip() == "" else stripped
        return value


class ProductDescription(BaseModel):
    """Description structurée d'un produit à classifier et contrôler.

    Les champs absents sont conservés comme inconnus : ils alimentent les données
    manquantes et peuvent déclencher une escalade.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str = Field(..., min_length=1, description="Nom commercial ou usuel du produit.")
    material_composition: list[str] = Field(
        default_factory=list,
        description="Matière, composition, pourcentages ou substances connues.",
    )
    primary_use: str | None = Field(
        default=None,
        description="Usage principal déclaré ou objectivable.",
    )
    country_origin: str | None = Field(
        default=None,
        description="Pays d'origine préférentielle ou non préférentielle.",
    )
    country_import: str | None = Field(
        default=None,
        description="Pays d'importation ou de mise en libre pratique.",
    )
    images: list[str] = Field(
        default_factory=list,
        description="URL ou chemins vers images produit/étiquettes/plaques signalétiques.",
    )
    known_certifications: list[str] = Field(
        default_factory=list,
        description="Certifications ou documents déjà connus : CE, RoHS, REACH, RTC, etc.",
    )
    components: list[str] = Field(
        default_factory=list,
        description="Composants, sous-ensembles, accessoires et fonctions techniques.",
    )
    technical_specs: dict[str, str] = Field(
        default_factory=dict,
        description="Fiche technique normalisée : modèle, puissance, tension, fluide, etc.",
    )
    raw_description: str | None = Field(
        default=None,
        description="Description libre initiale fournie par l'utilisateur.",
    )

    @field_validator(
        "name",
        "primary_use",
        "country_origin",
        "country_import",
        "raw_description",
        mode="before",
    )
    @classmethod
    def _strip_string(cls, value: Any) -> Any:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value

    @field_validator("material_composition", "images", "known_certifications", "components", mode="before")
    @classmethod
    def _clean_string_lists(cls, value: Any) -> Any:
        if value is None:
            return []
        if isinstance(value, str):
            value = [value]
        if isinstance(value, list):
            return [item.strip() for item in value if isinstance(item, str) and item.strip()]
        return value

    @field_validator("technical_specs", mode="before")
    @classmethod
    def _clean_specs(cls, value: Any) -> Any:
        if value is None:
            return {}
        if isinstance(value, dict):
            cleaned: dict[str, str] = {}
            for key, item in value.items():
                if key is None or item is None:
                    continue
                key_str = str(key).strip()
                value_str = str(item).strip()
                if key_str and value_str:
                    cleaned[key_str] = value_str
            return cleaned
        return value

    def all_text(self) -> str:
        """Concatène les informations textuelles pour les règles heuristiques."""
        chunks: list[str] = [
            self.name,
            self.primary_use or "",
            self.country_origin or "",
            self.country_import or "",
            self.raw_description or "",
            " ".join(self.material_composition),
            " ".join(self.known_certifications),
            " ".join(self.components),
            " ".join(f"{key} {value}" for key, value in self.technical_specs.items()),
        ]
        return " ".join(chunk for chunk in chunks if chunk).lower()

    def critical_missing_fields(self) -> list[str]:
        """Liste les informations critiques manquantes pour une classification sérieuse."""
        missing: list[str] = []
        if not self.material_composition:
            missing.append("composition exacte avec pourcentages, matériaux ou substances")
        if not self.primary_use:
            missing.append("usage principal réel du produit")
        if not self.country_origin:
            missing.append("pays d'origine douanière")
        if not self.country_import:
            missing.append("pays d'importation / mise en libre pratique")
        if not self.components and not self.technical_specs:
            missing.append("fiche technique, composants, fonction principale et modèle")
        if not self.images:
            missing.append("photos du produit, étiquette, emballage et plaque signalétique")
        return missing


class ClassificationProposal(BaseModel):
    """Proposition de code SH/NC/TARIC avec justification et niveau de confiance."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    hs_code: str = Field(
        ...,
        min_length=2,
        max_length=10,
        pattern=r"^\d{2,10}$",
        description="Code SH/NC/TARIC numérique, sans espace ni point.",
    )
    title: str | None = Field(default=None, description="Libellé synthétique du code proposé.")
    confidence_level: ConfidenceLevel = Field(default=ConfidenceLevel.LOW)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    source: SourceKind = Field(default=SourceKind.WCO, description="Source principale.")
    sources: list[OfficialSource] = Field(
        default_factory=list,
        description="Sources officielles ou expertes citées.",
    )
    justification: str = Field(
        ...,
        min_length=1,
        description="Raisonnement : règles générales, notes, fonction, matière et usage.",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Hypothèses retenues pour que cette proposition soit valable.",
    )
    missing_data: list[str] = Field(
        default_factory=list,
        description="Données manquantes susceptibles de modifier le classement.",
    )
    risk_flags: list[str] = Field(
        default_factory=list,
        description="Points de vigilance : ambiguïté, produit composite, jurisprudence, etc.",
    )
    disclaimer: str = Field(default=LEGAL_DISCLAIMER)

    @field_validator("hs_code", mode="before")
    @classmethod
    def _normalize_hs_code(cls, value: Any) -> Any:
        if isinstance(value, str):
            digits = "".join(char for char in value if char.isdigit())
            return digits
        return value

    @field_validator("assumptions", "missing_data", "risk_flags", mode="before")
    @classmethod
    def _clean_lists(cls, value: Any) -> Any:
        if value is None:
            return []
        if isinstance(value, str):
            value = [value]
        if isinstance(value, list):
            return [item.strip() for item in value if isinstance(item, str) and item.strip()]
        return value


class ComplianceCheck(BaseModel):
    """Résultat documenté d'un contrôle réglementaire."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    area: ComplianceArea
    status: ComplianceStatus
    source_officielle: OfficialSource
    recommendation: str = Field(..., min_length=1)
    details: str | None = None
    applicable_regulations: list[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=utc_now)
    disclaimer: str = Field(default=LEGAL_DISCLAIMER)


class DecisionStep(BaseModel):
    """Étape horodatée de la chaîne de décision."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    timestamp: datetime = Field(default_factory=utc_now)
    actor: ActorType
    action: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    sources: list[OfficialSource] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EscalationTicket(BaseModel):
    """Ticket d'escalade vers expert humain, transitaire ou courtier en douane."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    ticket_id: str = Field(default_factory=lambda: f"ESC-{uuid4().hex[:12].upper()}")
    created_at: datetime = Field(default_factory=utc_now)
    reason: str = Field(..., min_length=1)
    destination: Literal["expert_humain", "transitaire", "courtier_douane"] = "expert_humain"
    product: ProductDescription
    proposals: list[ClassificationProposal] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)
    priority: Literal["low", "normal", "high", "urgent"] = "normal"
    status: Literal["open", "in_progress", "closed"] = "open"
    recommended_actions: list[str] = Field(default_factory=list)
    disclaimer: str = Field(default=LEGAL_DISCLAIMER)


class DecisionChain(BaseModel):
    """Objet central traçant toute la chaîne de décision.

    La chaîne est complétée étape par étape : ingestion, génération de
    propositions, scoring, contrôles réglementaires, arbitrage et escalade.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    chain_id: str = Field(default_factory=lambda: f"DC-{uuid4().hex}")
    product: ProductDescription
    steps: list[DecisionStep] = Field(default_factory=list)
    classification_proposals: list[ClassificationProposal] = Field(default_factory=list)
    selected_proposal: ClassificationProposal | None = None
    compliance_checks: list[ComplianceCheck] = Field(default_factory=list)
    escalation_ticket: EscalationTicket | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    disclaimer: str = Field(default=LEGAL_DISCLAIMER)

    def add_step(
        self,
        *,
        actor: ActorType,
        action: str,
        summary: str,
        inputs: dict[str, Any] | None = None,
        outputs: dict[str, Any] | None = None,
        sources: list[OfficialSource] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DecisionStep:
        """Ajoute une étape horodatée à la chaîne de décision."""
        step = DecisionStep(
            actor=actor,
            action=action,
            summary=summary,
            inputs=inputs or {},
            outputs=outputs or {},
            sources=sources or [],
            metadata=metadata or {},
        )
        self.steps.append(step)
        self.updated_at = utc_now()
        return step


class ClassificationOutcome(BaseModel):
    """Résultat complet de la chaîne de classification assistée."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    product: ProductDescription
    decision_chain: DecisionChain
    proposals: list[ClassificationProposal] = Field(default_factory=list)
    selected_proposal: ClassificationProposal | None = None
    escalation_ticket: EscalationTicket | None = None
    missing_data: list[str] = Field(default_factory=list)
    recommendation: str = Field(..., min_length=1)
    disclaimer: str = Field(default=LEGAL_DISCLAIMER)
