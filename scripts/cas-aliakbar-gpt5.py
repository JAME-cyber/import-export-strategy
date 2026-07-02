#!/usr/bin/env python3
"""
Cas d'étude anti-biais : Ali Akbar / Daily Ecommerce "$400K/mo AI dropshipping".
GPT-5 décortique les allégations, recalcule le coût complet, identifie les oublis.
Respecte NOTICE-SOURCES.md / POLITIQUE-CITATION.md (reformulation, citation stricte).
"""
import sys, time, requests

API_KEY = "REDACTEDee58e407d5135ab255bd908a12b02e624632dff5d77e4e303f526e81efc5bb48"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-5.5"
OUT = "/home/tars/import-export-project/knowledge-base/synthesis/11-CAS-ALIAKBAR-400K-AI-DROPSHIPPING.md"

def read(p):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[MANQUANT: {p}]"

TRANSCRIPT = read("/home/tars/import-export-project/.archive/concurrents/AliAkbar-DailyEcom_400K-AI-Dropshipping_ehNjnJlXwFg.txt")
SKILL_ANTI_BIAIS = read("/home/tars/.pi/skills/analyse-critique/SKILL.md")
RAPPORT_EVERGREEN = read("/home/tars/import-export-project/knowledge-base/synthesis/10-RAPPORT-DEMONSTRATEUR-EVERGREEN.md")[:6000]
POLITIQUE = read("/home/tars/import-export-project/POLITIQUE-CITATION.md")

SYSTEM = """Tu es un ANALYSTE IMPORT/DROP-SHIPPING senior — l'avocat du diable, pas un valideur.
Tu appliques rigoureusement le cadre anti-biais ci-dessous (10 réflexes).
Tu traites un cas réel : une vidéo YouTube qui promet de cloner une boutique Shopify à 400K$/mois "100% IA".

CONTRAINTES ÉDITORIALES STRICTES (politique de citation du projet Operator Roster) :
- Tu NE reproduis PAS le transcript. Reformulation originale non verbatim uniquement.
- Citations directes EXCEPTIONNELLES, < 30 mots, entre guillemets, avec attribution (chaîne + URL + date).
- Tu distingues : FAITS (non protégeables) vs FORMULATIONS (à reformuler).
- Tu neutralises les promesses commerciales ("100% automatisé", "succès quasi certain").
- Conflits d'intérêt documentés explicitement.

Tu réponds en FRANÇAIS. Tu es impitoyable sur les chiffres. Tu ne flattes pas le créateur.
Le cas d'étude doit servir de DÉMONSTRATION vivante de l'anti-biais du Roster."""

USER = f"""MISSION : produire un cas d'étude anti-biais sur la vidéo d'Ali Akbar (Daily Ecommerce).
Titre vidéo : "I Built A $400K/mo Claude Shopify Dropshipping Store (100% Ai Automated)"
URL : https://www.youtube.com/watch?v=ehNjnJlXwFg · Date : 20 juin 2026 · Durée : 45:35 · Chaîne : Ali Akbar / Daily Ecommerce

# TRANSCRIPT BRUT (matière première — à NE PAS reproduire, à reformuler)
{TRANSCRIPT}

# CADRE ANTI-BAIS À APPLIQUER
{SKILL_ANTI_BIAIS[:6000]}

# POLITIQUE DE CITATION (à respecter strictement)
{POLITIQUE[:3000]}

# RÉFÉRENCE — notre rapport evergreen (style attendu)
{RAPPORT_EVERGREEN[:4000]}

---

## TA MISSION — CAS D'ÉTUDE EN 10 SECTIONS

Structure STRICTEMENT (même esprit que le rapport evergreen, mais adapté à un cas de dropshipping) :

### SECTION 1 — SYNTHÈSE EXÉCUTIVE (5 lignes max)
Verdict en 1 phrase + les 3 révélations les plus importantes du cas.

### SECTION 2 — LE DISCOURS DE LA VIDÉO (reformulé, pas verbatim)
- Promesse centrale (reformulée)
- Le workflow présenté (8-9 outils cités, reformulés comme "workflow d'automatisation")
- Les allégations chiffrées brutes ($400K, 64% marge, 93%, 48 ads, etc.)
- Ce qui est VENDU réellement (formation + affiliations)

### SECTION 3 — LE BAIT-AND-SWITCH
Le titre promet un store à $400K, mais il clone un AUTRE produit (split-end trimmer).
Analyser cet écart titre/contenu.

### SECTION 4 — RECALCUL DU COÛT COMPLET (le cœur de l'anti-biais)
Reprendre les chiffres du trimmer ($14 achat + $3 ship → $52 vente = "marge 64%")
et recalculer en coût complet réaliste pour un primo-dropshipper US/EU :
Tableau poste par poste : achat, shipping, marketing FB/TT (CAC dropshipping = 25-40% du CA !),
retours (8-15% électronique/beauté), SAV, plateforme (Shopify + Stripe),
taxes (TVA EU / sales tax US), RC produit, stockage, invendus.
→ Marge nette RÉELLE estimée (3 scénarios pire/médian/optimiste).
COMPARER avec la "marge 64%" annoncée.

### SECTION 5 — LES OUBLIS RÉGLEMENTAIRES (ce que la vidéo ne dit jamais)
Lister exhaustivement ce qui n'est jamais mentionné mais qui est OBLIGATOIRE :
- Conformité produit : CE/LVD/EMC/RoHS/REACH pour l'UE (le trimmer est électrique !)
- Droits de la consommation : garantie 2 ans, droit rétractation 14j
- Propriété intellectuelle : cloner un store = droits d'auteur (copie des photos/copy)
- RGPD : scraping ad libraries, collecte emails, données clients
- Fiscalité : TVA UE, sales tax US (nexus), déclarations
- Douane : si import hors UE/US
- Assurance RC produit
- Risque de bannissement Facebook (le créateur l'évoque 1 fois pour un autre produit)

### SECTION 6 — CONFLITS D'INTÉRÊT CARTOGRAPHIÉS
La vidéo est saturée d'affiliations et upsell. Lister chaque outil mentionné et son statut :
- Affiliate direct (Winning Hunter -20%)
- Outil propriétaire (WhiteLabeler, AI Vault, ShopFunnels employees)
- Upsell formation (White Label Drop Shipping, "claw dropshipping")
Analyser : quel est le VRAI business model ? (spoiler : ce n'est pas le dropshipping)

### SECTION 7 — LES "AI EMPLOYEES" SONT DES WRAPPERS
Démontrer que les "AI employees gratuits/payants" sont en réalité des prompts Claude pré-emballés
(connecteur custom + system prompt). Aucune IA propriétaire. Le moat technique = zéro.
Révéler l'illusion "100% AI automated".

### SECTION 8 — KILL FACTORS (top 5 risques mortels pour un débutant qui suit le tuto)
Lister les 5 scénarios qui ruinent le projet : bannissement FB, droit d'auteur,
saisie douane, retours massifs, cash burn marketing.

### SECTION 9 — VERDICT ET COMPARAISON AVEC LE ROSTER
- Verdict sur la vidéo : FIABLE / PARTIEL / TROMPEUR (justifier)
- Ce qu'un débutant peut réellement en retirer (1-2 éléments utiles)
- Comment le Roster aurait traité ce même cas (différence méthodologique)

### SECTION 10 — SOURCES ET ATTRIBUTION (format POLITIQUE-CITATION)
Citation stricte de la vidéo (chaîne, titre, URL, date).
Note sur le statut de fiabilité ⚠️ PARTIEL.
Lien vers NOTICE-SOURCES.md.

## EXIGENCES
- Tableaux avec chiffres précis (pas vagues)
- 3 scénarios chiffrés pour le recalcul marge
- Aucune promesse de résultat
- Style sobre, factuel, opposable
- Le cas doit démontrer CONCRÈTEMENT pourquoi un débutant a besoin d'analyse anti-biais

Sois impitoyable mais factuel. Ce cas d'étude va dans knowledge-base/synthesis/ et sert de
démonstrateur de la valeur du Roster."""

payload = {
    "model": MODEL,
    "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": USER}],
    "temperature": 0.4,
    "max_tokens": 14000,
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://localhost",
    "X-Title": "pi-coding-agent",
}

print(f"→ Cas Ali Akbar via {MODEL}", file=sys.stderr)
print(f"→ Contexte : {len(TRANSCRIPT)+len(SKILL_ANTI_BIAIS)+len(RAPPORT_EVERGREEN)+len(POLITIQUE):,} chars", file=sys.stderr)
t0 = time.time()
try:
    r = requests.post(BASE_URL, headers=headers, json=payload, timeout=420)
    dt = time.time() - t0
    print(f"→ HTTP {r.status_code} en {dt:.1f}s", file=sys.stderr)
    if r.status_code != 200:
        print("ERREUR:", r.text[:2000], file=sys.stderr)
        sys.exit(1)
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    header = f"""# 🎯 CAS D'ÉTUDE ANTI-BAIS — "AI Dropshipping 400K$/mo"

> Cas d'étude du Roster — démonstration vivante de l'analyse anti-biais.
> Source vidéo : Ali Akbar / Daily Ecommerce, vidéo `ehNjnJlXwFg` — https://www.youtube.com/watch?v=ehNjnJlXwFg
> Date vidéo : 20 juin 2026 · Durée : 45:35 · Consultée le 21 juin 2026.
> Statut fiabilité : ⚠️ **PARTIEL** — voir `../../NOTICE-SOURCES.md` et `../../POLITIQUE-CITATION.md`.
> Notes originales, non verbatim. Citations courtes uniquement (CPI art. L122-5 3°).

---

"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(header + content)
    print(f"\n✓ Sauvegardé : {OUT}", file=sys.stderr)
    print(f"  Tokens : prompt={usage.get('prompt_tokens','?')} completion={usage.get('completion_tokens','?')}", file=sys.stderr)
    print(f"  Taille : {len(content):,} caractères", file=sys.stderr)
    print("\n" + "="*72 + "\n", file=sys.stderr)
    print(content)
except requests.exceptions.Timeout:
    print(f"\n[TIMEOUT après {time.time()-t0:.0f}s]", file=sys.stderr)
    sys.exit(2)
except Exception as e:
    print(f"\n[ERREUR: {e}]", file=sys.stderr)
    sys.exit(3)
