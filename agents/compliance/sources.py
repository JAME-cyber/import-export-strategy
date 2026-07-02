"""Registre des sources officielles de conformité.

Les sources sont abstraites derrière l'interface ``RegulatorySource`` afin de
permettre une intégration ultérieure robuste : API officielle, scraping autorisé,
base documentaire interne validée ou connecteur métier.

Aucun appel réseau réel n'est effectué dans ce module. Les implémentations
fournies sont des bouchons déterministes qui citent les URL officielles et
retournent des signaux exploitables pour la chaîne de décision.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .models import OfficialSource, ProductDescription, SourceKind, utc_now


class RegulatoryQuery(BaseModel):
    """Requête normalisée envoyée à une source réglementaire."""

    model_config = ConfigDict(extra="forbid")

    area: str = Field(..., min_length=1)
    product: ProductDescription | None = None
    hs_code: str | None = None
    country_origin: str | None = None
    country_import: str | None = None
    keywords: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RegulatoryResponse(BaseModel):
    """Réponse normalisée d'une source réglementaire."""

    model_config = ConfigDict(extra="forbid")

    source: OfficialSource
    matched: bool = False
    summary: str
    data: dict[str, Any] = Field(default_factory=dict)
    references: list[str] = Field(default_factory=list)
    queried_at: datetime = Field(default_factory=utc_now)


class RegulatorySource(ABC):
    """Interface d'une source réglementaire consultable de manière asynchrone."""

    @property
    @abstractmethod
    def source_info(self) -> OfficialSource:
        """Retourne les métadonnées officielles de la source."""

    @abstractmethod
    async def query(self, query: RegulatoryQuery) -> RegulatoryResponse:
        """Interroge la source via une requête normalisée."""


class BaseStubRegulatorySource(RegulatorySource):
    """Base pour les sources bouchon déterministes sans accès réseau."""

    def __init__(self, source_info: OfficialSource) -> None:
        self._source_info = source_info

    @property
    def source_info(self) -> OfficialSource:
        return self._source_info

    async def _yield_control(self) -> None:
        """Conserve une interface async sans réaliser d'I/O réseau."""
        await asyncio.sleep(0)

    def _product_text(self, query: RegulatoryQuery) -> str:
        product_text = query.product.all_text() if query.product else ""
        keyword_text = " ".join(query.keywords)
        return f"{product_text} {query.hs_code or ''} {keyword_text}".lower()


class TaricSource(BaseStubRegulatorySource):
    """Bouchon TARIC : tarif intégré de l'Union européenne."""

    def __init__(self) -> None:
        super().__init__(
            OfficialSource(
                name="TARIC - Tarif intégré de l'Union européenne",
                url="https://ec.europa.eu/taxation_customs/dds2/taric/taric_consultation.jsp",
                source_type=SourceKind.TARIC,
                reference="Consultation TARIC officielle",
                excerpt="Tarifs, mesures, restrictions et nomenclature combinée applicables à l'importation UE.",
            )
        )

    async def query(self, query: RegulatoryQuery) -> RegulatoryResponse:
        await self._yield_control()
        text = self._product_text(query)
        hs_code = "".join(char for char in (query.hs_code or "") if char.isdigit())

        measures: list[str] = []
        references = ["Règlement (CEE) n° 2658/87 - Nomenclature combinée et TARIC"]
        matched = bool(hs_code)

        if hs_code.startswith("8415") or "climatiseur" in text or "air conditioner" in text:
            measures.extend(
                [
                    "Vérifier le classement NC précis des machines de conditionnement d'air.",
                    "Contrôler les mesures environnementales UE liées aux équipements contenant des gaz fluorés.",
                ]
            )
            matched = True
        if hs_code.startswith(("61", "62")) or any(word in text for word in ("textile", "vêtement", "t-shirt")):
            measures.append("Contrôler les règles textile, étiquetage fibres et éventuelles préférences d'origine.")
            matched = True
        if hs_code.startswith(("72", "73")) or "acier" in text or "steel" in text:
            measures.append("Produits sidérurgiques : vérifier mesures de surveillance, sauvegarde ou contingents.")
            matched = True
        if "dual-use" in text or "double usage" in text:
            measures.append("Vérifier les restrictions biens à double usage et licences d'export/import applicables.")
            matched = True

        summary = (
            "Signal TARIC disponible pour le produit ou le code fourni."
            if matched
            else "Aucun signal TARIC déterministe sans code NC/TARIC suffisamment précis."
        )
        return RegulatoryResponse(
            source=self.source_info,
            matched=matched,
            summary=summary,
            data={"measures_to_verify": measures, "hs_code": hs_code or None},
            references=references,
        )


class EurLexSource(BaseStubRegulatorySource):
    """Bouchon EUR-Lex : législation européenne."""

    def __init__(self) -> None:
        super().__init__(
            OfficialSource(
                name="EUR-Lex",
                url="https://eur-lex.europa.eu/",
                source_type=SourceKind.EUR_LEX,
                reference="Portail officiel du droit de l'Union européenne",
                excerpt="Accès aux directives, règlements et décisions de l'Union européenne.",
            )
        )

    async def query(self, query: RegulatoryQuery) -> RegulatoryResponse:
        await self._yield_control()
        text = self._product_text(query)
        refs: list[str] = []
        data: dict[str, Any] = {}

        if query.area.lower() in {"ce", "ce_marking", "marquage ce"}:
            if any(
                word in text
                for word in (
                    "électrique",
                    "electrical",
                    "electronique",
                    "électronique",
                    "machine",
                    "climatiseur",
                    "radio",
                    "jouet",
                    "pression",
                )
            ):
                refs.extend(
                    [
                        "Directive 2014/35/UE - basse tension",
                        "Directive 2014/30/UE - compatibilité électromagnétique",
                        "Directive 2006/42/CE ou Règlement (UE) 2023/1230 - machines selon calendrier d'application",
                    ]
                )
                data["ce_likely_required"] = True
            else:
                data["ce_likely_required"] = False

        if query.area.lower() == "rohs":
            refs.append("Directive 2011/65/UE (RoHS) et Directive déléguée (UE) 2015/863")
            data["eee_scope_signal"] = any(
                word in text
                for word in (
                    "électrique",
                    "electrical",
                    "electronique",
                    "électronique",
                    "circuit",
                    "batterie",
                    "led",
                    "climatiseur",
                    "chargeur",
                )
            )

        if query.area.lower() == "reach":
            refs.extend(
                [
                    "Règlement (CE) n° 1907/2006 (REACH)",
                    "Liste candidate SVHC publiée par l'ECHA",
                ]
            )
            data["reach_general_obligation"] = True
            data["chemical_signal"] = any(
                word in text
                for word in (
                    "chimique",
                    "chemical",
                    "solvant",
                    "peinture",
                    "adhésif",
                    "colle",
                    "résine",
                    "pvc",
                    "plastifiant",
                    "réfrigérant",
                    "r410a",
                    "gaz",
                )
            )

        return RegulatoryResponse(
            source=self.source_info,
            matched=bool(refs),
            summary="Références EUR-Lex identifiées selon le domaine réglementaire demandé.",
            data=data,
            references=refs,
        )


class WcoHsSource(BaseStubRegulatorySource):
    """Bouchon WCO HS : nomenclature mondiale du Système harmonisé."""

    def __init__(self) -> None:
        super().__init__(
            OfficialSource(
                name="WCO HS - Nomenclature du Système harmonisé",
                url="https://www.wcoomd.org/en/topics/nomenclature",
                source_type=SourceKind.WCO,
                reference="Organisation mondiale des douanes - HS Nomenclature",
                excerpt="Structure du Système harmonisé, règles générales interprétatives et notes explicatives.",
            )
        )

    async def query(self, query: RegulatoryQuery) -> RegulatoryResponse:
        await self._yield_control()
        text = self._product_text(query)
        hs_code = "".join(char for char in (query.hs_code or "") if char.isdigit())

        notes: list[str] = []
        if hs_code.startswith("8415") or "climatiseur" in text:
            notes.append("Chapitre 84 : machines et appareils mécaniques ; position 84.15 pour machines de conditionnement d'air.")
        if hs_code.startswith(("61", "62")) or "t-shirt" in text or "vêtement" in text:
            notes.append("Sections XI et chapitres 61/62 : distinction bonneterie/non bonneterie, composition textile et type de vêtement.")
        if hs_code.startswith("85") or "électronique" in text:
            notes.append("Chapitre 85 : appareils électriques ; classement dépendant de la fonction propre et des composants.")
        if hs_code.startswith("39") or "plastique" in text:
            notes.append("Chapitre 39 : ouvrages en matières plastiques ; classement très dépendant de la forme et de l'usage.")

        return RegulatoryResponse(
            source=self.source_info,
            matched=bool(notes),
            summary="Notes SH indicatives identifiées. Les notes explicatives complètes doivent être consultées par un expert.",
            data={"notes_summary": notes, "hs_code": hs_code or None},
            references=["Règles générales pour l'interprétation du Système harmonisé", "Notes explicatives du SH - WCO"],
        )


class Access2MarketsSource(BaseStubRegulatorySource):
    """Bouchon Access2Markets : portail UE import/export."""

    def __init__(self) -> None:
        super().__init__(
            OfficialSource(
                name="Access2Markets - Commission européenne",
                url="https://trade.ec.europa.eu/access-to-markets/fr/home",
                source_type=SourceKind.ACCESS2MARKETS,
                reference="Portail Access2Markets",
                excerpt="Droits, taxes, procédures, documents et règles d'origine pour le commerce avec l'UE.",
            )
        )

    async def query(self, query: RegulatoryQuery) -> RegulatoryResponse:
        await self._yield_control()
        text = self._product_text(query)
        docs = [
            "facture commerciale",
            "liste de colisage",
            "document de transport",
            "déclaration en douane",
            "preuve d'origine lorsque demandée ou préférence revendiquée",
        ]
        signals: list[str] = []
        if "bois" in text or "wood" in text:
            signals.append("Vérifier exigences phytosanitaires, emballages bois NIMP 15 et éventuelles restrictions bois.")
        if "aliment" in text or "food" in text or "cosmétique" in text:
            signals.append("Vérifier exigences sanitaires, sécurité produit et enregistrements sectoriels.")
        if "r410a" in text or "réfrigérant" in text or "refrigerant" in text:
            signals.append("Équipement contenant gaz fluorés : vérifier règles F-gas, quotas et déclaration de conformité.")
        if "textile" in text or "vêtement" in text or "t-shirt" in text:
            signals.append("Vérifier étiquetage textile UE et règles d'origine préférentielle si avantage tarifaire recherché.")

        return RegulatoryResponse(
            source=self.source_info,
            matched=True,
            summary="Documents et signaux procéduraux Access2Markets déterminés à partir des informations fournies.",
            data={"baseline_documents": docs, "signals": signals},
            references=["Access2Markets - procédures et formalités d'importation UE"],
        )


class FrenchCustomsSource(BaseStubRegulatorySource):
    """Bouchon Douanes françaises : RTC et documentation douanière française."""

    def __init__(self) -> None:
        super().__init__(
            OfficialSource(
                name="Douanes françaises - douane.gouv.fr",
                url="https://www.douane.gouv.fr/",
                source_type=SourceKind.DOUANE_FR,
                reference="Renseignement tarifaire contraignant (RTC) et documentation douanière",
                excerpt="Portail des douanes françaises pour demandes RTC et doctrine administrative publiée.",
            )
        )

    async def query(self, query: RegulatoryQuery) -> RegulatoryResponse:
        await self._yield_control()
        text = self._product_text(query)
        has_rtc_reference = any(token in text for token in ("rtc", "bti", "renseignement tarifaire contraignant"))
        return RegulatoryResponse(
            source=self.source_info,
            matched=True,
            summary=(
                "Référence RTC/BTI fournie par l'utilisateur : à vérifier dans la base officielle."
                if has_rtc_reference
                else "Aucun RTC fourni. Une demande de RTC est recommandée en cas d'enjeu financier ou d'ambiguïté."
            ),
            data={
                "rtc_reference_provided": has_rtc_reference,
                "recommended_when": [
                    "classement ambigu",
                    "montants de droits significatifs",
                    "produit nouveau ou composite",
                    "risque de divergence entre États membres",
                ],
            },
            references=["Procédure de demande de Renseignement tarifaire contraignant (RTC)"],
        )


class EUSanctionsSource(BaseStubRegulatorySource):
    """Bouchon Sanctions UE : listes restrictives et sanctions financières."""

    RESTRICTED_COUNTRY_SIGNALS = {
        "russie",
        "russia",
        "belarus",
        "biélorussie",
        "bielorussie",
        "iran",
        "syrie",
        "syria",
        "corée du nord",
        "coree du nord",
        "north korea",
        "dprk",
        "myanmar",
        "birmanie",
    }

    def __init__(self) -> None:
        super().__init__(
            OfficialSource(
                name="EU Sanctions Map / Financial Sanctions Database",
                url="https://webgate.ec.europa.eu/fsd/fsf",
                source_type=SourceKind.SANCTIONS_EU,
                reference="Base officielle des sanctions financières de l'Union européenne",
                excerpt="Consultation des mesures restrictives et des personnes/entités listées.",
            )
        )

    async def query(self, query: RegulatoryQuery) -> RegulatoryResponse:
        await self._yield_control()
        countries = " ".join(
            part
            for part in (
                query.country_origin or "",
                query.country_import or "",
                query.product.country_origin if query.product else "",
                query.product.country_import if query.product else "",
            )
            if part
        ).lower()
        restricted_signal = any(country in countries for country in self.RESTRICTED_COUNTRY_SIGNALS)
        return RegulatoryResponse(
            source=self.source_info,
            matched=True,
            summary=(
                "Signal pays sensible détecté : filtrage sanctions UE approfondi indispensable."
                if restricted_signal
                else "Aucun signal pays sensible déterminé par le bouchon ; filtrage entités/contreparties reste obligatoire."
            ),
            data={"restricted_country_signal": restricted_signal},
            references=["Base des sanctions financières UE", "EU Sanctions Map"],
        )


class SourceRegistry:
    """Registre de sources réglementaires injectables."""

    def __init__(self, sources: dict[str, RegulatorySource] | None = None) -> None:
        self._sources: dict[str, RegulatorySource] = sources or {}

    @classmethod
    def default(cls) -> "SourceRegistry":
        """Construit le registre par défaut avec toutes les sources officielles bouchon."""
        return cls(
            {
                "taric": TaricSource(),
                "eur_lex": EurLexSource(),
                "wco_hs": WcoHsSource(),
                "access2markets": Access2MarketsSource(),
                "douane_fr": FrenchCustomsSource(),
                "sanctions_eu": EUSanctionsSource(),
            }
        )

    def register(self, key: str, source: RegulatorySource) -> None:
        """Enregistre ou remplace une source sous une clé stable."""
        normalized = key.strip().lower()
        if not normalized:
            raise ValueError("La clé de source ne peut pas être vide.")
        self._sources[normalized] = source

    def get(self, key: str) -> RegulatorySource:
        """Récupère une source par clé."""
        normalized = key.strip().lower()
        try:
            return self._sources[normalized]
        except KeyError as exc:
            available = ", ".join(sorted(self._sources))
            raise KeyError(f"Source réglementaire inconnue: {key!r}. Sources disponibles: {available}") from exc

    def list_sources(self) -> list[OfficialSource]:
        """Liste les métadonnées officielles de toutes les sources enregistrées."""
        return [source.source_info for source in self._sources.values()]

    async def query(self, key: str, query: RegulatoryQuery) -> RegulatoryResponse:
        """Interroge une source enregistrée."""
        return await self.get(key).query(query)

    async def query_many(self, keys: list[str], query: RegulatoryQuery) -> list[RegulatoryResponse]:
        """Interroge plusieurs sources en parallèle."""
        return await asyncio.gather(*(self.query(key, query) for key in keys))
