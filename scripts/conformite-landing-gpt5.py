#!/usr/bin/env python3
"""
Session 2 — Consolidation conformité landing via GPT-5.
Génère : mentions-légales.html (LCEN complète) + CGV-BETA.md + corrections landing.
Audit croisé du localStorage + du footer.
"""
import sys, time, requests

API_KEY = "REDACTEDee58e407d5135ab255bd908a12b02e624632dff5d77e4e303f526e81efc5bb48"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-5.5"
OUT = "/home/tars/import-export-project/scripts/conformite-landing-gpt5.md"
BASE = "/home/tars/import-export-project"

def read(p):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[MANQUANT: {p}]"

LANDING = read(f"{BASE}/landing/index.html")
CONFIDENTIALITE = read(f"{BASE}/landing/confidentialite.html")
AUDIT = read(f"{BASE}/scripts/audit-juridique-gpt5.md")[:10000]  # sections RGPD + LCEN
COURS = read(f"{BASE}/knowledge-base/course/COURS-IMPORT-SYSTEM.md")

SYSTEM = """Tu es un JURISTE français spécialisé LCEN (loi pour la confiance dans l'économie numérique 2004-575),
RGPD, et droit de la consommation B2C. Tu produis des documents de conformité opérationnels et
directement utilisables pour un éditeur de site web qui lance une bêta fermée.

PRINCIPES :
- LCEN art. 6 III-1 et 2 : identification éditeur + hébergeur
- Code conso art. L221-5 et s. : informations précontractuelles vente à distance
- Code conso art. L221-18 : droit de rétractation 14 jours
- Code conso art. L221-28 : exception contenu numérique immédiat (consentement exprès)
- Code conso art. L224-25-1 et s. : garantie légale de conformité des contenus/services numériques
- Code conso art. L612-1 : médiation de la consommation

Tu réponds en FRANÇAIS. Tu utilises des [CHAMPS À COMPLÉTER] explicites quand l'info n'est pas disponible.
Tu produis du HTML/MD directement copiable. Tu restes sobre (pas de promesses)."""

USER = f"""CONTEXTE : Projet "Operator Roster" en lancement bêta fermée (waitlist email, pas de vente immédiate).
La landing (index.html) et une politique de confidentialité (confidentialite.html) existent déjà.

# ============================================================
# 1. LANDING ACTUELLE (index.html)
# ============================================================
{LANDING}

# ============================================================
# 2. POLITIQUE DE CONFIDENTIALITÉ EXISTANTE
# ============================================================
{CONFIDENTIALITE}

# ============================================================
# 3. AUDIT JURIDIQUE PRÉCÉDENT (extrait sections RGPD + LCEN)
# ============================================================
{AUDIT}

# ============================================================
# 4. COURS PAYANT (structure d'offre — 197/497/1497€)
# ============================================================
{COURS}

---

## TA MISSION — 4 LIVRABLES HTML/MD DIRECTEMENT COPIABLES

### LIVRABLE 1 — PAGE `mentions-legales.html` (LCEN complète)
HTML autonome, même design que confidentialite.html (CSS dark/amber, déjà défini).
Doit contenir :
- Éditeur : [CHAMPS À COMPLÉTER : nom/prénom ou dénomination sociale, forme, capital si société, adresse, SIRET/RCS/RM, n° TVA intra si applicable]
- Directeur de publication
- Contact : email + [à compléter : adresse postale ou email]
- Hébergeur : [à compléter — Vercel/Netlify/OVH…]
- Numéro CNIL (plus obligatoire depuis 2018 mais on peut mentionner "dispensé")
- Propriété intellectuelle (contenus, marque, code)
- Responsabilité (limitation, outil d'aide à la décision, pas conseil personnalisé)
- Liens hypertextes (politique de modération)
- Cookies/traceurs (renvoi vers confidentialite.html)
- Droit applicable (France) et juridiction
- Liens vers confidentialite.html, NOTICE-SOURCES.md, POLITIQUE-CITATION.md
- Mention "lancement en bêta fermée — pas de vente à ce stade"

Format : HTML complet, structuré h1/h2/h3, tableaux pour éditeur/hébergeur.

### LIVRABLE 2 — PAGE `cgu.html` (CGU bêta waitlist)
HTML autonome même design. CGU de la bêta waitlist (pas CGV vente, car pas de vente en bêta).
Doit contenir :
- Objet : inscription à la waitlist « Roster »
- Conditions d'inscription (email valide, consentement)
- Nature du service bêta : notifications de drops, accès éventuel à des rapports, pas d'exécution d'import
- Gratuité de la bêta (ou contrepartie précisée)
- Limites : outil d'analyse, pas conseil, pas garantie de résultat
- Données personnelles (renvoi vers confidentialite.html)
- Propriété intellectuelle des contenus distribués
- Comportement attendu (pas de revente, pas de scraping des contenus, respect du droit d'auteur)
- Suspension d'accès (motifs : abus, non-respect)
- Modifications des CGU
- Résiliation / désinscription (1 clic)
- Contact et médiation
- Droit applicable

### LIVRABLE 3 — `CGV-BETA.md` (modèle prêt pour quand la vente démarre)
Document Markdown à conserver dans le repo, qui servira de base quand le cours (197/497/1497€)
sera commercialisé. Doit couvrir :
- Identité vendeur
- Description des offres (Starter 197€ / Operator 497€ / Commando 1497€)
- Prix TTC, modalités de paiement
- Accès et durée
- Droit de rétractation 14 jours (art. L221-18)
- Exception contenu numérique immédiat : case à cocher « Je consens à l'exécution immédiate et renonce à mon droit de rétractation » (art. L221-28)
- Garantie légale de conformité numérique (art. L224-25-1 et s.)
- Médiation de la consommation (art. L612-1)
- Limitation de responsabilité : outil d'aide, pas conseil
- Propriété intellectuelle du cours (interdiction de redistribution)
- Politique de remboursement
- Droit applicable et juridiction

### LIVRABLE 4 — CORRECTIONS À APPORTER À LA LANDING ACTUELLE
Liste précise des modifications à faire dans index.html :
- Footer : simplifier, pointer vers mentions-legales.html / confidentialite.html / cgu.html / NOTICE-SOURCES.md
- Le disclaimer verbatim "transcripts YouTube" à corriger en "vidéos YouTube" (cohérence avec le nettoyage session 1)
- Le localStorage de l'email : remplacer par simple message de confirmation (déjà fait ? à vérifier)
- Ajout d'une case à cocher consentement RGPD dans le formulaire (si pas déjà)
- Lien "Mentions légales" visible dans le footer
- Vérifier cohérence : la landing promet-elle quelque chose que la bêta ne fait pas ?

Donne pour chaque correction : le code AVANT / APRÈS exact.

## FORMAT
Chaque livrable clairement délimité par des séparateurs `### LIVRABLE N — [nom]` et le code
dans des blocs HTML/MD complets directement copiables.
Sois exhaustif mais sobre. Pas de promesses. Mentionne explicitement les [CHAMPS À COMPLÉTER]
que l'éditeur devra renseigner avec ses vraies infos."""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER},
    ],
    "temperature": 0.3,
    "max_tokens": 14000,
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://localhost",
    "X-Title": "pi-coding-agent",
}

print(f"→ Conformité landing via {MODEL}", file=sys.stderr)
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
    header = f"<!-- Généré par {data.get('model', MODEL)} via OpenRouter · 2026-06-20 · Session 2 conformité landing -->\n"
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
