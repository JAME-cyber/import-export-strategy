#!/usr/bin/env python3
"""
Contre-analyse des 3 livrables par un modèle Anthropic (via OpenRouter).
Avocat du diable — applique le skill analyse-critique.
"""
import json, os, sys, time
import requests

API_KEY = "REDACTEDee58e407d5135ab255bd908a12b02e624632dff5d77e4e303f526e81efc5bb48"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "anthropic/claude-sonnet-4"

BASE = "/home/tars/import-export-project"

def read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[FICHIER MANQUANT: {path}]"

# --- Contexte à faire contre-analyser ---
SKILL = read("/home/tars/.pi/skills/analyse-critique/SKILL.md")
README_ORIG = read(f"{BASE}/README.md")              # livrable B
LANDING = read(f"{BASE}/landing/index.html")         # livrable A
COURS = read(f"{BASE}/knowledge-base/course/COURS-IMPORT-SYSTEM.md")  # livrable C
AGENTS_CFG = read(f"{BASE}/config/agents-config.yaml")
SOURCING_AGENT = read(f"{BASE}/agents/sourcing-master/AGENT.md")
NICHE = read(f"{BASE}/knowledge-base/synthesis/09-NICHE-CANICULE-FINAL.md")

SYSTEM = """Tu es un ANALYSTE CRITIQUE senior — l'avocat du diable. Pas un valideur.
Tu appliques RIGOUREUSEMENT le cadre anti-biais ci-dessous (10 réflexes).
Ton rôle : stress-tester chaque hypothèse, identifier les angles morts, les contradictions,
les promesses implicites non chiffrées, les risques que le créateur a minimisés.

Tu réponds en FRANÇAIS. Tu es direct, tranchant, structuré. Aucune flatterie.
Si quelque chose est bon, tu le dis en 1 ligne. Tu passes 90% de ton temps sur ce qui CLOCHE.

CADRE À APPLIQUER (skill analyse-critique) :
""" + SKILL

USER = f"""Je suis le créateur du projet "Operator Roster / Import System" — un système
d'agents IA pour l'import-export (Chine → Europe), positionné contre les cours de dropshipping
type Steve Tan. Je viens de produire 3 livrables après m'être "inspiré" de stevetan.com.

Je te demande une CONTRE-ANALYSE SANS PITIÉ de ces 3 livrables.

## CONTEXTE DU PROJET (pour que tu comprennes la base)

### Config agents (anti-biais revendiqué)
{AGENTS_CFG}

### Exemple d'agent (sourcing)
{SOURCING_AGENT}

### Le produit phare "Drop #001" (niche canicule)
{NICHE}

---

## LIVRABLE A — Landing page "Roster" (HTML)
{LANDING}

## LIVRABLE B — README réécrit (vocabulaire operator)
{README_ORIG}

## LIVRABLE C — Cours payant "IMPORT SYSTEM"
{COURS}

---

## TA MISSION

Contre-analyse ces 3 livrables comme l'avocat du diable. Structure ta réponse ainsi :

### 1. 🎯 Le positionnement stratégique est-il tenable ?
- "Les agents font le travail vs les cours apprennent" → est-ce que ce n'est pas juste du marketing ? Les agents sont-ils VRAIMENT capables d'exécuter (sourcer, négocier, vérifier la conformité) ou est-ce une promesse vaporware ?
- Y a-t-il une contradiction entre "pas un cours" et le fait de vendre... un cours (livrable C) ?
- Le moat "anti-biais" est-il défendable ou imitable en 1 semaine par un concurrent ?

### 2. 💸 Coûts cachés &amp; viabilité financière du PROJET LUI-MÊME
- Applique tes réflexes sur la grille tarifaire du cours (197/497/1497€). Le CAC pour vendre ça ? Le seuil de rentabilité ?
- La niche canicule (Drop #001) : saisonnière, effacité limitée à 35°C — est-ce un bon démonstrateur ou un piège ?
- La marge nette "25-40%" est-elle elle-même crédible ou déjà gonflée ?

### 3. ⚖️ Risques juridiques &amp; conformité
- La landing collecte des emails (waitlist). RGPD mentionné ?
- Promesse "agents vérifient la conformité CE" → responsabilité si un client suit l'agent et se fait saisir en douane ?
- Le cours donne des conseils juridiques (structure société, douane) → activité réglementée d'intermédiation/conseil ?

### 4. 📉 Saturation &amp; crédibilité marketing
- Steve Tan a 3254 operators. La landing affiche 412 (et anime un faux compteur). Est-ce risqué légalement/réputationnellement ?
- Le style "operator/manifest/classified" est explicitement copié de stevetan.com — risque de paraître dérivatif &amp; me-too ?
- "EMAIL-GATED · ROSTER ONLY" sur un projet qui n'a aucun produit fini déclassifié → est-ce du vaporware teasing ?

### 5. 💣 Top 5 KILL FACTORS (ce qui peut tuer le projet)
Liste les 5 risques mortels, du plus probable au moins probable.

### 6. 🏁 VERDICT par livrable
Pour A, B, C séparément : OUI / OUI MAIS / NON / PAS ENCORE — avec la condition de rattrapage.

### 7. ✏️ Les 5 corrections prioritaires (actionnables immédiatement)
Concrètes, pas vagues. Que dois-je changer EN PREMIER.

Sois impitoyable. Je préfère entendre "c'est du vaporware, voici pourquoi" maintenant
qu'après avoir lancé.
"""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER},
    ],
    "temperature": 0.4,
    "max_tokens": 4000,
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://localhost",
    "X-Title": "pi-coding-agent",
}

print(f"→ Appel OpenRouter : {MODEL}", file=sys.stderr)
print(f"→ Contexte envoyé : {len(SYSTEM)+len(USER):,} caractères", file=sys.stderr)
t0 = time.time()

try:
    r = requests.post(BASE_URL, headers=headers, json=payload, timeout=240)
    dt = time.time() - t0
    print(f"→ Réponse HTTP {r.status_code} en {dt:.1f}s", file=sys.stderr)
    if r.status_code != 200:
        print("ERREUR:", r.text[:2000], file=sys.stderr)
        sys.exit(1)
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    print("\n" + "="*72 + "\n", file=sys.stderr)
    print(f"Modèle: {data.get('model', MODEL)}", file=sys.stderr)
    print(f"Tokens: prompt={usage.get('prompt_tokens','?')} completion={usage.get('completion_tokens','?')}", file=sys.stderr)
    print("="*72 + "\n", file=sys.stderr)
    print(content)
except requests.exceptions.Timeout:
    print(f"\n[TIMEOUT après {time.time()-t0:.0f}s — réessaie ou prends un modèle plus rapide]", file=sys.stderr)
    sys.exit(2)
except Exception as e:
    print(f"\n[ERREUR: {e}]", file=sys.stderr)
    sys.exit(3)
