# ============================================================

> ⚠️ **Notes originales, non verbatim.** Sources publiques (vidéos YouTube, plateformes
> B2B, données officielles) — voir `../../NOTICE-SOURCES.md` et `../../POLITIQUE-CITATION.md`.
> Citations courtes uniquement (CPI art. L122-5 3°). Aucun transcript brut n'est inclus dans ce dépôt.
# SYNTHÈSE : JURIDIQUE & FISCALITÉ POUR L'IMPORT-EXPORT
# Basé sur vidéos @StartBusinessWorld + recherches complémentaires
# ============================================================

## 1. STATUTS JURIDIQUES (France)

### Comparatif pour activité import-export :

| Statut | Impôts | Charges | Plafond CA | Crédibilité | Recommandation |
|--------|--------|---------|------------|-------------|---------------|
| **Micro-entreprise** | Sur CA (22%) | Forfaitaires | 77.7K€ services / 188.7K€ vente | Faible | ❌ Pas idéal |
| **EURL/SARL** | Sur bénéfice (IS ou IR) | Réelles | Aucun | Moyenne | ✅ Si associé unique |
| **SASU/SAS** | Sur bénéfice (IS) | Réelles | Aucun | Haute | ⭐ Recommandé |
| **SA** | Sur bénéfice (IS) | Réelles | Aucun | Très haute | Seulement si gros volume |

### Recommandation : SASU ou SAS
- **IS** : 15% jusqu'à 42 500€ de bénéfice, 25% au-delà
- **Déductions possibles** : Achats marchandises, publicités, déplacements, matériel, abonnements
- **Protection du patrimoine** personnel (responsabilité limitée aux apports)
- **Possibilité d'évolution** : Ajouter associés (SAS), lever des fonds
- **Comptabilité** : Obligatoire mais déductible

### Pourquoi ÉVITER la micro-entreprise pour l'import :
- Pas de déduction des charges (achats stock, pub, etc.)
- Si 30% de marge et 22% de cotisations → reste 8%
- Plafond vite atteint en import
- Pas crédible pour fournisseurs chinoises sérieuses

## 2. CRÉER UNE SOCIÉTÉ À HONG KONG

### Avantages :
- Régime fiscal **territorial** (HK n'impose que les revenus de source HK) — mais **cela ne se traduit pas automatiquement par 0 % d'impôt** pour un résident fiscal français. Analyse au cas par cas : lieu de direction effective, établissement stable, substance locale, règles françaises sur les revenus mondiaux (risque CFC)
- **0,25 %** sur les premiers 200 000 HKD de bénéfices de source HK, puis **16,5 %** (taux à vérifier sur inlandrevenue.gov.hk)
- Création à distance techniquement possible — **à valider avec un fiscaliste** (résidence fiscale, conventions FR-HK)
- Compte multidevise (EUR, USD, CNY...)
- Compatible Stripe & PayPal (non blacklisté)
- Stabilité juridique & bancaire
- Crédibilité internationale élevée

### Processus de création :
1. Choisir 2-3 noms de société (unicité obligatoire à HK)
2. Vérification KYC : passeport + selfie + justificatif domicile
3. Enregistrement en 5-7 jours ouvrés
4. Réception CI (Certificate of Incorporation) + BR (Business Registration)
5. Ouverture compte bancaire (banque en ligne = 95% des cas)

### Comptes bancaires HK :
- **Banques traditionnelles** : DBS, HSBC (demandent historique business)
- **Banques en ligne** : Plus accessibles pour débutants, multidevise, Apple Pay
- Ouverture en 24-48h pour banques en ligne

### Obligations annuelles :
- Renouvellement annuel (3 jours)
- Garder factures en cas de contrôle
- Audit optionnel (recommandé si gros volumes)

### Pour qui ?
- ✅ Import-export multi-pays
- ✅ Business en ligne
- ✅ Freelance international
- ✅ Optimisation fiscale légale
- ✅ Besoin Stripe/PayPal fiable

## 3. TVA & TAXES EN IMPORT

### Calcul TVA import (France/EU) :
```
Valeur taxable = (Valeur marchandise CIF + Droits de douane) × TVA
```
Exemple :
- Marchandise : 10 000€
- Transport : 2 000€
- Droits douane (8%) : 960€
- Valeur taxable : (12 000 + 960) × 20% = 2 592€
- **Coût total à l'import** : 12 000 + 960 + 2 592 = **15 552€**

### Régimes TVA :
- **TVA déductible** : Si vous êtes assujetti (entreprise), la TVA d'import est récupérable
- **Autoliquidation** : Déclarer et déduire simultanément = flux de trésorerie neutre
- **DEB** : Déclaration d'Échanges de Biens (obligatoire pour échanges intra-UE)

### Droits de douane par catégorie (indicatif) :
| Catégorie | Droit moyen | Observations |
|-----------|------------|-------------|
| Électronique | 0-4% | Parfois exemption |
| Textile/Habillement | 6-12% | Variable selon type |
| Chaussures | 8-17% | Selon matériau |
| Mobilier | 0-6% | Bois vs métal |
| Machines | 0-4% | Souvent favorable |
| Cosmétiques | 0-5% | Réglementation stricte |
| Jouets | 3-7% | Certifications obligatoires |

## 4. PROTECTION JURIDIQUE

### Dépôt de marque :
- **En Chine** : Qui dépose possède → Déposer AVANT de contacter des usines
- **INPI France** : Protection nationale (~200€)
- **EUIPO** : Protection européenne (~850€)
- **OMPI (Madrid)** : Protection internationale (~300-500€ par pays)

### Contrats recommandés avec fournisseurs :
1. **NDA** (Non-Disclosure Agreement) : Confidentialité
2. **NNN Agreement** : Non-divulgation + Non-contournement + Non-concurrence
3. **Contrat OEM/ODM** : Définit droits de propriété intellectuelle
4. **Contrat de fabrication** : Specs, qualité, délais, pénalités

### Certifications à vérifier selon produit :
- **CE** : Obligatoire pour vente en Europe
- **RoHS** : Restriction substances dangereuses (électronique)
- **REACH** : Substances chimiques (textile, cosmétique)
- **ISO 9001** : Système management qualité
- **ISO 14001** : Management environnemental
- **BSCI / SEDEX** : Éthique sociale (audit usine)

## 5. STRUCTURE OPTIMALE POUR L'IMPORT-EXPORT

### Setup recommandé pour débutant :
```
Option A — France uniquement :
  SASU/SAS en France → Import direct → Revente locale
  
Option B — France + Hong Kong (⚠️ **à n'envisager qu'après avis fiscal spécialisé**) :
  HK Ltd → Facturation internationale (sous conditions de substance réelle)
  + SASU France → Opérations locales
  → Nécessite justification économique, conventions intragroupe cohérentes,
    documentation des prix de transfert ; risque de requalification par l'administration française
  
Option C — Progressif :
  1. Commencer avec SASU France
  2. Ajouter HK Ltd quand CA > 50K€/an
  3. Structurer avec comptable international
```

### Optimisation fiscale légale :
- Déduire tous les frais liés à l'activité
- TVA import récupérable
- Charges sociales optimisées en SAS/SASU
- Hong Kong pour revenus extra-territoriaux
- Convention fiscale FR-HK (pas de double imposition)
