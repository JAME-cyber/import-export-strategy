"""Module conformité douanière d'ImportExport Pro.

Ce package fournit une chaîne de décision assistée, traçable et escaladable
pour la classification douanière et les contrôles réglementaires.

Disclaimer légal :
Cet outil ASSISTE la classification et la conformité. Il ne remplace pas
l'expert humain. Toute décision douanière engage votre responsabilité.
"""

from .classifier import HeuristicLLMProvider, LLMProvider, classify_product, classify_product_sync
from .compliance_checks import (
    check_ce_marking,
    check_documents_required,
    check_quotas_licenses,
    check_reach,
    check_rohs,
    check_sanctions,
    run_all_compliance_checks,
)
from .journal import AuditJournal, verify_integrity
from .models import (
    LEGAL_DISCLAIMER,
    ActorType,
    ClassificationOutcome,
    ClassificationProposal,
    ComplianceArea,
    ComplianceCheck,
    ComplianceStatus,
    ConfidenceLevel,
    DecisionChain,
    DecisionStep,
    EscalationTicket,
    OfficialSource,
    ProductDescription,
    SourceKind,
)
from .sources import (
    Access2MarketsSource,
    EUSanctionsSource,
    EurLexSource,
    FrenchCustomsSource,
    RegulatoryQuery,
    RegulatoryResponse,
    RegulatorySource,
    SourceRegistry,
    TaricSource,
    WcoHsSource,
)

__version__ = "1.0.0"

__all__ = [
    "LEGAL_DISCLAIMER",
    "Access2MarketsSource",
    "ActorType",
    "AuditJournal",
    "ClassificationOutcome",
    "ClassificationProposal",
    "ComplianceArea",
    "ComplianceCheck",
    "ComplianceStatus",
    "ConfidenceLevel",
    "DecisionChain",
    "DecisionStep",
    "EUSanctionsSource",
    "EscalationTicket",
    "EurLexSource",
    "FrenchCustomsSource",
    "HeuristicLLMProvider",
    "LLMProvider",
    "OfficialSource",
    "ProductDescription",
    "RegulatoryQuery",
    "RegulatoryResponse",
    "RegulatorySource",
    "SourceKind",
    "SourceRegistry",
    "TaricSource",
    "WcoHsSource",
    "check_ce_marking",
    "check_documents_required",
    "check_quotas_licenses",
    "check_reach",
    "check_rohs",
    "check_sanctions",
    "classify_product",
    "classify_product_sync",
    "run_all_compliance_checks",
    "verify_integrity",
]
