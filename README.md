# ⬡ OPERATOR ROSTER — Import System

> Les cours vous apprennent. **Les agents analysent.**

Système d'agents IA spécialisés dans l'**import-export international** (Chine → Europe / Afrique), construit sur **24 h+ de contenu expert** issu de 7 chaînes YouTube spécialisées — avec un **anti-biais intégré** qui cartographie les conflits d'intérêt de chaque source.

Le Roster n'est pas une formation. C'est une chaîne de 5 unités IA qui **pré-analysent** vos opportunités : elles identifient des sources, calculent les coûts complets réels, signalent les exigences de conformité probables et dressent un manifeste de décision. **Elles n'exécutent pas l'import à votre place** — elles préparent une analyse pour que vous validiez ensuite avec un transitaire, un organisme notifié (SGS/Bureau Veritas) et un professionnel habilité avant de signer.

---

## 🎯 Le positionnement (lisez ceci en premier)

| Les autres (cours / dropshipping) | Le Roster |
|---|---|
| Vous apprennent à faire | **Analysent vos opportunités** |
| Prix FOB cités seuls → marges illusoires | FOB **+ coût complet** systématique |
| Promesses « 8 figures » | **3 scénarios** (pire 40 % / médian 40 % / optimiste 20 %) |
| Scalable si vous embauchez | Scalable **par design** |
| Sources présentées comme neutres | **Conflits d'intérêt cartographiés** |

---

## 🗂 Le système

```
import-export-project/
├── README.md                          # Ce manifeste
├── landing/                           # Page waitlist "Roster" (HTML autonome)
├── config/
│   └── agents-config.yaml             # Calibration des unités + tables anti-biais
├── agents/                            # ⬡ LES 5 UNITÉS
│   ├── sourcing-master/               # UNIT-01 · SOURCING
│   ├── logistique-pro/                # UNIT-02 · LOGISTIQUE
│   ├── legal-fiscal/                  # UNIT-03 · LEGAL & FISCAL (anti-biais CRITICAL)
│   ├── market-analyzer/               # UNIT-04 · MARKET
│   └── brand-builder/                 # UNIT-05 · BRAND
├── knowledge-base/
│   ├── transcripts/                   # 24 transcripts YouTube bruts (la matière première)
│   ├── synthesis/                     # ⬡ DOSSIERS — synthèses structurées
│   ├── guides/                        # ⬡ MANUELS D'OPÉRATION
│   ├── course/                        # ⬡ IMPORT SYSTEM (cours payant dérivé)
│   └── templates/                     # Calculateur coûts, cahier des charges
└── data/
    ├── fournisseurs/                  # ⬡ LE MANIFEST — base fournisseurs + RFQ
    ├── produits/                      # Catalogue produits & prix
    ├── heat-wave-prices-alibaba.json  # Drop #001 — niche canicule
    └── reglementation/                # Réglementations par pays
```

---

## ⬡ Les 5 unités

| Unité | Rôle | Anti-biais | Source dominante |
|---|---|---|---|
| 🏭 **UNIT-01 SOURCING** | Fournisseurs, prix réels, MOQ, négociation | **HIGH** | @SINOSOURCING, @StartBusinessWorld |
| 🚢 **UNIT-02 LOGISTIQUE** | Containers, incoterms, transitaires, douane | **LOW** (source neutre) | @CargoFamily |
| ⚖️ **UNIT-03 LEGAL & FISCAL** | Statuts, TVA, douane, CE/RoHS | **CRITICAL** | @StartBusinessWorld |
| 📊 **UNIT-04 MARKET** | Marges corrigées, saturation, scénarios | **HIGH** | multiples |
| 🎨 **UNIT-05 BRAND** | Private label, OEM/ODM, packaging | **HIGH** | @lineborrajo, @Sebastien |

Chaque unité charge `agents/COMMUN-ANTI-BAIS.md` et applique les tables de correction :
- **Prix** : `FOB × 1.4–1.6 = coût réel minimum`
- **Marges** : `marge YouTube × 0.25 = marge nette réaliste`
- **Marketing B2C** : `-20 % du CA` · **Retours** : `-8 %` · **Frais plateforme** : `-15 %`

---

## 📜 Le Manifest (données produit)

**Drop #001 — Niche Canicule EU 2026** (démonstrateur) :
- Refroidisseur évaporatif portable : **20 € FOB → 30–35 € coût complet → 70–150 € marché EU**
- Marge nette réaliste : **15–25 %** (SAV/garantie 2 ans + stockage inclus ; vs « 300 % » annoncé YouTube)
- Voir `data/heat-wave-prices-alibaba.json` + `knowledge-base/synthesis/09-NICHE-CANICULE-FINAL.md`

---

## 🚀 Démarrage rapide

```bash
# Consulter une unité
python scripts/query-agent.py sourcing "Je veux importer des climatiseurs portatifs de Chine"

# Construire la base de connaissances
python scripts/build-knowledge.py

# Ouvrir la page waitlist Roster
open landing/index.html
```

---

## 📚 Sources de connaissances (782 KB de transcripts)

| Chaîne | Focus | Fiabilité | Biais |
|--------|-------|-----------|-------|
| @StartBusinessWorld | Import-Export Chine, plateformes | ⚠️ PARTIEL | Vend formation « Sourcing Pro » + création société |
| @CargoFamily | Logistique, transit, douane | ✅ **FIABLE** | Aucun (podcast pro gratuit) |
| @SINOSOURCING (Fabien Dessaint) | Sourcing usines, Canton Fair | ⚠️ PARTIEL | Vend « Incubator » + services logistiques |
| @lineborrajo | Création marques e-commerce | ⚠️ PARTIEL | Vend méthode création de marque |
| @Sebastien.selfmadeprogram | E-commerce avancé, mini-brands | ⚠️ PARTIEL | Vend formations dropshipping |

---

## 🧭 Domaines couverts

Sourcing Chine (1688, Taobao, Alibaba, Made-in-China, Global Sources) · Logistique (maritime, aérien, express) · Incoterms (EXW, FOB, CIF, DDP) · Douane (codes HS, CE, RoHS) · Statuts juridiques (Micro, SASU, SARL, Hong Kong Ltd) · Création de marque (private label, OEM/ODM) · Canton Fair · Assurance cargo · Optimisation fiscale · Marchés cibles (Europe, Afrique, Moyen-Orient).

---

## 🔗 Dérivés & clarification du positionnement

> **Offre principale = les agents** (outils d'aide à l'analyse). Le **cours** IMPORT SYSTEM est un
> produit **secondaire d'onboarding** : il sert au segment qui veut comprendre avant de déléguer.
> Ce n'est pas une contradiction avec « pas un cours » — le cours est l'exception explicitement
> secondaire, l'offre principale reste le système d'agents. À l'inverse des cours concurrents,
> les agents continuent le travail d'analyse après la formation.

- **Page waitlist Roster** : `landing/index.html` (style teaser crédible, email-gated, conforme RGPD)
- **Cours dérivé** : `knowledge-base/course/` (IMPORT SYSTEM — 30 jours, version « formation humaine » du système, pour le segment qui veut apprendre avant de déléguer)
- **Limites assumées des agents** : ils analysent les sources publiques et produisent des scénarios ; ils ne négocient pas en direct, n'inspectent pas physiquement les usines et ne valident pas les certifications à la place d'un organisme notifié (SGS/Bureau Veritas).

---

<sub>OPERATOR ROSTER · IMPORT SYSTEM · 2026 — Outil d'analyse import anti-biais. Pas une promesse d'exécution automatique.</sub>
