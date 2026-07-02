#!/usr/bin/env python3
"""
Reformulation comparaison concurrents (GPT-5 via OpenRouter).
Rends la comparaison Steve Tan/Ecom King conforme à la publicité comparative (Code conso art. L122-1).
"""
import sys, time, requests

API_KEY = "REDACTEDee58e407d5135ab255bd908a12b02e624632dff5d77e4e303f526e81efc5bb48"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-5.5"
OUT = "/home/tars/import-export-project/scripts/reformulation-comparaison-gpt5.md"
BASE = "/home/tars/import-export-project"

def read(p):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[MANQUANT: {p}]"

LANDING = read(f"{BASE}/landing/index.html")
AUDIT = read(f"{BASE}/scripts/audit-juridique-gpt5.md")

SYSTEM = """Tu es un JURISTE français + COPYWRITER B2B. Tu connais :
- Code conso art. L121-1 à L122-3 : publicité comparative et pratiques commerciales trompeuses
- LCEN art. 20 : publicité identifiable
- Loi 2023-451 influence commerciale

RÈGLES DE LA PUBLICITÉ COMPARATIVE EN FRANCE (art. L122-1) :
- Elle est AUTORISÉE mais encadrée
- Doit porter sur des biens/services répondant aux MÊMES BESOINS
- Doit être OBJECTIVE, VÉRIFIABLE, non DÉNIGRANTE
- Ne doit pas créer de confusion dans l'esprit du public
- Toute allégation doit être sourcée et démontrable

Ton objectif : transformer une comparaison frontale nominative (Steve Tan, Ecom King, "Ultimate
Dropshipping System", "8 figures en quelques jours") en argument commercial PUISSANT MAIS
LÉGALEMENT DÉFENDABLE. Tu préserves l'impact marketing sans risquer un procès en dénigrement
ou une action pour pratique trompeuse.

Tu réponds en FRANÇAIS. Tu donnes du code HTML directement copiable."""

USER = f"""CONTEXTE : Landing page "Operator Roster" — système d'agents IA d'analyse import.
Un bloc de comparaison (section #vs) compare actuellement le Roster aux cours de dropshipping
type Steve Tan / Ecom King. Cette formulation est RISQUÉE juridiquement :
- citations nominatives de concurrents identifiés (Steve Tan, Ecom King, "Ultimate Dropshipping System")
- allégation "8 figures en quelques jours" non sourcée précisément
- ton potentiellement dénigrant ("marges illusoires", "garde-fous manquants")

# BLOC ACTUEL À REFORMULER

{LANDING[LANDING.find('<!-- VS -->'):LANDING.find('</section>')+len('</section>')]}

# EXTRAIT AUDIT JURIDIQUE (cadre publicité comparative)

{AUDIT[AUDIT.find('POINT 4'):AUDIT.find('## ⚖️ SOLUTION')][:3500]}

---

## TA MISSION — 4 LIVRABLES

### LIVRABLE 1 — ANALYSE DU RISQUE ACTUEL
Liste précise des formulations à risque dans le bloc actuel, classées par gravité
(dénigrement, allégation non sourcée, confusion, etc.). Pour chaque : la raison juridique.

### LIVRABLE 2 — BLOC HTML REFORMULÉ (directement copiable)
Reformule l'ENSEMBLE de la section #vs en gardant :
- L'impact commercial (le contraste "apprentissage vs analyse automatisée")
- Le design HTML actuel (classes .vs, .col, .them, .us, SVG check/cross, h2/h3/ul/li)
- Les arguments différenciants (coût complet, scénarios, anti-biais)

Mais en :
- SUPPRIMANT les noms nominatifs (Steve Tan, Ecom King, Ultimate Dropshipping System)
  → Remplacer par "la plupart des formations e-commerce/import" ou "certaines formations du marché"
- SOURÇANT ou neutralisant l'allégation "8 figures" → "certaines promesses de résultats rapides"
- ÉVITANT le ton dénigrant → formulation neutre et factuelle ("axé apprentissage" plutôt que "marges illusoires")
- RENDANT VÉRIFIABLE chaque comparatif (critère objectif : humain vs automatisé, FOB seul vs coût complet)

Donne le HTML COMPLET de la section <!-- VS -->...</section>, structuré comme l'original mais reformulé.

### LIVRABLE 3 — VERSION ALTERNATIVE "PLUS PRUDENTE" (option de repli)
Une 2e version du bloc, encore plus prudente (aucune référence aux concurrents même générique,
focus 100% sur les bénéfices du Roster). Pour le cas où l'éditeur veut un risque zéro.

### LIVRABLE 4 — LINE-EDITOR : corrections ponctuelles hors bloc #vs
Si "Steve Tan", "Ecom King" ou "8 figures" apparaissent ailleurs dans la landing, propose la
reformulation (AVANT/APRÈS).

## CRITÈRES DE VALIDATION
Chaque version doit passer ce test :
1. Aucun nom de concurrent identifiable
2. Aucune allégation chiffrée non sourcée sur un tiers
3. Pas de ton dénigrant
4. Chaque comparatif repose sur un critère objectif (nature de l'offre, pas qualité morale)
5. Argument commercial préservé (le Roster paraît différenciant et utile)

Sois concret. Donne du HTML prêt à copier-coller."""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER},
    ],
    "temperature": 0.4,
    "max_tokens": 8000,
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://localhost",
    "X-Title": "pi-coding-agent",
}

print(f"→ Reformulation comparaison via {MODEL}", file=sys.stderr)
t0 = time.time()
try:
    r = requests.post(BASE_URL, headers=headers, json=payload, timeout=400)
    dt = time.time() - t0
    print(f"→ HTTP {r.status_code} en {dt:.1f}s", file=sys.stderr)
    if r.status_code != 200:
        print("ERREUR:", r.text[:2000], file=sys.stderr)
        sys.exit(1)
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(f"<!-- Reformulation comparaison — {data.get('model', MODEL)} · 2026-06-20 -->\n\n" + content)
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
