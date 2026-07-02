#!/usr/bin/env python3
"""
Audit juridique complet (GPT-5 via OpenRouter).
Focus : droits d'auteur transcripts YouTube (point bloquant) + RGPD + responsabilité civile
+ mentions légales + publicité. Sortie : audit + corrections actionnables.
Sauvegarde dans : scripts/audit-juridique-gpt5.md
"""
import sys, time, requests

API_KEY = "REDACTEDee58e407d5135ab255bd908a12b02e624632dff5d77e4e303f526e81efc5bb48"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-5.5"
OUT = "/home/tars/import-export-project/scripts/audit-juridique-gpt5.md"
BASE = "/home/tars/import-export-project"

def read(p):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[MANQUANT: {p}]"

# Contexte réel du projet
LANDING = read(f"{BASE}/landing/index.html")
README = read(f"{BASE}/README.md")
COURS = read(f"{BASE}/knowledge-base/course/COURS-IMPORT-SYSTEM.md")
LISTING_TRANSCRIPTS = ""  # on liste juste les fichiers
import os
tdir = f"{BASE}/knowledge-base/transcripts"
if os.path.isdir(tdir):
    files = sorted([f for f in os.listdir(tdir) if f.endswith(".txt")])
    LISTING_TRANSCRIPTS = f"Nombre de transcripts : {len(files)}\nExemples : {', '.join(files[:8])}\n..."
SUMMARY_TRANSCRIPTS = read(f"{BASE}/knowledge-base/transcripts/_summary.json")
CRITIQUE_SONNET = read(f"{BASE}/scripts/critique-sonnet.md")  # contient déjà les points juridiques

SYSTEM = """Tu es un JURISTE Français spécialisé en :
- Droit de la propriété intellectuelle (Code de la propriété intellectuelle — CPI)
- Droit du numérique / RGPD (UE) 2016/679 et Loi Informatique et Libertés
- Droit de la consommation (Code de la consommation, DGCCRF, Clause d'insertion publicitaire)
- Droit du e-commerce (LCEN loi pour la confiance dans l'économie numérique)

Tu réponds en FRANÇAIS. Tu cites les articles de loi pertinents. Tu distingues :
- RISQUE ÉLEVÉ (doit être réglé avant lancement)
- RISQUE MOYEN (à régler dans le mois)
- RISQUE FAIBLE / À SURVEILLER

Tu ne fais pas de conseil personnalisé juridictionnel — tu produis un audit de conformité
pour un éditeur de logiciel/contenu qui se prépare à lancer un projet en bêta.
Tu n'es pas un avocat commis — tu es un juriste-conseil qui aide à prioriser.

Tu appliques le principe de réalité : qu'est-ce qui est RÉELLEMENT risqué aujourd'hui,
pas ce qui est théoriquement possible. Un créateur YouTube qui tombe sur son transcript
transformé en produit payant = vraie plainte potentielle. Un prospect qui s'inscrit à une
waitlist sans mentions complètes = DGCCRF théorique mais rare en bêta fermée."""

USER = f"""AUDIT JURIDIQUE DU PROJET "OPERATOR ROSTER / IMPORT SYSTEM".

Le projet : un éditeur français prépare un système d'agents IA d'analyse import-export,
construit sur 24h+ de TRANSCRIPTS YOUTUBE extraits de 7 chaînes spécialisées
(sourcing Chine, logistique, juridique). Objectif : vendre un cours (197-1497€) + abonnement
"Roster" (waitlist en bêta fermée). Lancement prévu en bêta limitée.

# ============================================================
# POINT 1 — LE PLUS CRITIQUE : DROITS D'AUTEUR SUR LES TRANSCRIPTS
# ============================================================

## Ce que fait le projet aujourd'hui avec les transcripts YouTube

{LISTING_TRANSCRIPTS}

## Métadonnées des transcripts (résumé des sources)

{SUMMARY_TRANSCRIPTS}

Le projet :
1. Extrait/stoke les transcripts (transcriptions textuelles de vidéos YouTube de tiers)
2. Construit des synthèses structurées (fichiers .md dans knowledge-base/synthesis/)
3. Utilise ces synthèses + transcripts comme contexte pour des agents IA
4. Monétise indirectement (cours payant + abonnement Roster)
5. Cite les sources YouTubeurs dans le README (attribution)

## QUESTIONS JURIDIQUES À TRAITER (Point 1)

a) **Statut juridique d'un transcript YouTube** — un transcript brut est-il une œuvre
   protégée au sens du CPI (art. L112-2, L122-4) ? Quelle est l'œuvre originale : la vidéo,
   le transcript, la transcription ?
b) **Conditions d'utilisation YouTube** — l'extraction de transcripts via outils tiers
   (yt-dlp) enfreint-elle les CGU YouTube ? Est-ce un contournement de mesure technique ?
c) **Exceptions de citation (art. L122-5 3°) et courte citation** — les synthèses dérivées
   relèvent-elles de l'exception de courte citation ? Non, car ce sont des reformulations
   longues et monétisées. À préciser.
d) **Droits patrimoniaux vs droits moraux** — même avec accord des YouTubeurs, les droits
   moraux (paternité L121-1) persistent. Comment gérer l'attribution ?
e) **Sanctions encourues** — contrefaçon (L335-2 à L335-4) : 300 000€ + 3 ans. Délit pénal
   ou civil ? Risque réel vs théorique ?
f) **Solutions concrètes pour le projet** — parmi :
   - accord écrit avec chaque YouTubeur (le plus sûr)
   - attribution + citation stricte + reformulation totale (jamais de copie verbatim)
   - suppression des transcripts bruts, ne garder que des notes personnelles
   - option "fair use" américaine (inopérante en France — le dire explicitement)
   - licence des YouTubeurs (certains autorisent reuse — vérifier)
   → Priorise ces solutions par risque résiduel / effort.

# ============================================================
# POINT 2 — RGPD (COLLECTE EMAIL WAITLIST)
# ============================================================

## La landing actuelle (version corrigée post-critique Sonnet)

{LANDING}

## QUESTIONS RGPD

a) La mention RGPD actuelle est-elle suffisante pour bêta fermée ? Pour lancement public ?
b) Quels éléments manquent (éditeur/SIRET/contact/hébergeur/politique séparée/consentement
   horodaté/sous-traitant/DPA) ?
c) Le localStorage du navigateur = collecte ? Si oui, faut-il bandeau cookies ?
d) Si branchement sur ConvertKit/Buttondown : quelles obligations (article 28 RGPD,
   accord sous-traitant) ?
e) Risque concret en bêta fermée 30-100 inscrits vs lancement public 1000+ ?

# ============================================================
# POINT 3 — RESPONSABILITÉ CIVILE / CONSEIL
# ============================================================

## Le cours payant (extrait pertinent : disclaimer juridique)

{COURS}

## QUESTIONS RESPONSABILITÉ

a) Le disclaimer "pas un conseil personnalisé" protège-t-il vraiment ? Limites ?
b) Exercice illégal d'une profession réglementée (art. L111-7 Code de la sécurité financière ?
   art. 81 Loi règlementant le notariat ? intermédiation en douane art. L431-1 du CDV ?)
   — jusqu'où peut-on aller en "information générale" ?
c) Si un client suit un agent qui dit "code HS 7323.93, conforme" et se fait saisir 50K€,
   l'éditeur est-il responsable ? Sur quelle base (1382 Code civil / responsabilité produit
   défectueux / manquement à une obligation d'information) ?
d) Assurance RC professionnelle : obligatoire ou conseillée pour ce type d'activité ?
e) CGV/CGU minimales à avoir avant de facturer le cours.

# ============================================================
# POINT 4 — PUBLICITÉ / MENTIONS LÉGALES / LCEN
# ============================================================

a) Mentions légales obligatoires d'un site éditeur (LCEN art. 6-I-3 + loi LCEN 2004) :
   éditeur, directeur publication, hébergeur, contact. Que manque-t-il ?
b) "Build in public" / témoignages / preuve sociale : pièges (Loi Soverein 2023 sur
   l'influence commerciale, FTC-style règles) ?
c) Clause d'insertion publicitaire (art. L121-1 Code conso) — le projet en fait-il ?
   Avis "operators" / compteurs / témoignages inventés ?

# ============================================================
# FORMAT DE RÉPONSE ATTENDU
# ============================================================

Structure STRICTEMENT ainsi :

## 🔴 SYNTHÈSE EXÉCUTIVE
- Risque global (ÉLEVÉ/MOYEN/FAIBLE) avec justification 1 ligne
- Les 3 actions JURIDIQUES à faire en PREMIER (avant lancement bêta)

## 📋 AUDIT DÉTAILLÉ PAR POINT
Pour chaque point (1 à 4) :
- Diagnostic (avec articles de loi)
- Niveau de risque (ÉLEVÉ/MOYEN/FAIBLE) + probabilité réelle
- Sanctions théoriques vs probables
- Correction concrète (actionnable, pas théorique)

## ⚖️ SOLUTION PRIORISÉE POUR LES TRANSCRIPTS (point 1)
Tableau : solution × risque résiduel × effort × recommandation
Quelle est LA solution à appliquer en premier pour la bêta ?

## ✅ CHECKLIST CONFORMITÉ BÊTA FERMÉE (30-100 inscrits)
Liste précise, ordonnée, à cocher.

## ⚠️ CHECKLIST CONFORMITÉ LANCEMENT PUBLIC (1000+ inscrits)
Liste précise, ordonnée, à cocher. Distinction nette avec la bêta.

Sois précis, concret, et priorise par RISQUE RÉEL. Je veux pouvoir décider et agir,
pas un cours de droit."""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER},
    ],
    "temperature": 0.3,
    "max_tokens": 12000,
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://localhost",
    "X-Title": "pi-coding-agent",
}

print(f"→ Audit juridique via {MODEL}", file=sys.stderr)
t0 = time.time()
try:
    r = requests.post(BASE_URL, headers=headers, json=payload, timeout=360)
    dt = time.time() - t0
    print(f"→ HTTP {r.status_code} en {dt:.1f}s", file=sys.stderr)
    if r.status_code != 200:
        print("ERREUR:", r.text[:2000], file=sys.stderr)
        sys.exit(1)
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})

    header = f"""# ⚖️ AUDIT JURIDIQUE — Operator Roster / Import System

> Généré par **{data.get('model', MODEL)}** via OpenRouter.
> Date : 2026-06-20 · Audit de conformité bêta + lancement public.
> **NOTE** : Audit de conformité par juriste-conseil. Ne remplace pas un avocat
> commis pour un cas individuel. Document de travail pour prioriser les actions.

---

"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(header + content)
    print(f"\n✓ Audit sauvegardé : {OUT}", file=sys.stderr)
    print(f"  Modèle : {data.get('model', MODEL)}", file=sys.stderr)
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
