#!/usr/bin/env python3
"""
Contre-analyse N°2 — Second avis (OpenAI GPT-5 via OpenRouter).
Rôle : arbitre / tie-breaker face à la critique de Sonnet.
Lit les versions CORRIGÉES des livrables + la critique Sonnet.
"""
import json, os, sys, time
import requests

API_KEY = "REDACTEDee58e407d5135ab255bd908a12b02e624632dff5d77e4e303f526e81efc5bb48"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-5.5"

BASE = "/home/tars/import-export-project"

def read(p):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[MANQUANT: {p}]"

SKILL = read("/home/tars/.pi/skills/analyse-critique/SKILL.md")
CRITIQUE_SONNET = read(f"{BASE}/scripts/critique-sonnet.md")
LANDING = read(f"{BASE}/landing/index.html")              # corrigée
README = read(f"{BASE}/README.md")                        # corrigé
COURS = read(f"{BASE}/knowledge-base/course/COURS-IMPORT-SYSTEM.md")  # corrigé
NICHE = read(f"{BASE}/knowledge-base/synthesis/09-NICHE-CANICULE-FINAL.md")

SYSTEM = """Tu es un ANALYSTE CRITIQUE senior qui sert d'ARBITRE (tie-breaker).
Un premier critique (Claude Sonnet 4) a déjà analysé ce projet et produit une contre-analyse.
Le créateur a appliqué une série de corrections suite à cette critique.

Ton rôle n'est PAS de revalider mécaniquement. Ton rôle est de :
1. Vérifier ce sur quoi Sonnet avait RAISON (et si les corrections suffisent).
2. Identifier ce que Sonnet a MANQUÉ ou SURÉVALUÉ (biais d'excès de sévérité).
3. Juger si les corrections appliquées sont SUFFISANTES ou s'il reste des angles morts.
4. Donner un verdict consolidé final.

Tu réponds en FRANÇAIS. Tu es direct, tranchant, structuré. Tu appliques le cadre anti-biais ci-dessous.
Tu n'es pas là pour flatter — mais pas non plus pour en faire trop par réflexe.
Quand Sonnet a exagéré, dis-le. Quand Sonnet avait raison et la correction est insuffisante, dis-le.

CADRE ANTI-BAIS (référence) :
""" + SKILL

USER = f"""CONTEXTE : Projet "Operator Roster / Import System" — système d'agents IA pour l'import-export
(Chine → Europe), positionné contre les cours de dropshipping type Steve Tan.

Ci-dessous :
1. La critique de Sonnet (contre-analyse N°1)
2. Les 3 livrables DANS LEUR VERSION CORRIGÉE (post-critique)
3. Le produit démonstrateur (niche canicule)

# ============================================================
# 1. CRITIQUE DE SONNET (à arbitrer)
# ============================================================
{CRITIQUE_SONNET}

# ============================================================
# 2. LIVRABLE A (corrigé) — Landing HTML
# ============================================================
{LANDING}

# ============================================================
# 3. LIVRABLE B (corrigé) — README
# ============================================================
{README}

# ============================================================
# 4. LIVRABLE C (corrigé) — Cours payant
# ============================================================
{COURS}

# ============================================================
# 5. Démonstrateur Drop #001 (niche canicule)
# ============================================================
{NICHE}

# ============================================================
# TA MISSION — RÉPONDS EN FRANÇAIS, STRUCTURÉ
# ============================================================

## A. ARBITRAGE SUR LES 7 POINTS DE SONNET
Pour chacun des 7 points de la critique Sonnet, donne ton verdict :
- ✅ Sonnet avait raison (et la correction est suffisante / insuffisante)
- ⚖️ Sonnet partiellement raison (préciser)
- ❌ Sonnet a exagéré ou se trompe (justifier)

Points à arbitrer :
1. "Les agents font le travail" = vaporware (agents = chatbots)
2. Contradiction "pas un cours" vs cours 1497€
3. Moat anti-biais fragile (copiable en 2h)
4. CAC insoutenable sans budget marketing
5. Niche canicule = mauvais démonstrateur
6. Marge 25-40% surévaluée → 15-25% (correction appliquée)
7. Risques RGPD + conseil illégal + publicité mensongère

## B. CE QUE SONNET A MANQUÉ
Liste 3-5 angles morts que Sonnet n'a pas vus (positive ou négative).

## C. LES CORRECTIONS SONT-ELLES SUFFISANTES ?
- RGPD : suffisant pour lancement bêta ? Manque-t-il quelque chose (CGU, politique cookies, hébergeur, mentions éditeur) ?
- Compteur supprimé : OK ou faut-il aussi retirer les autres éléments de preuve sociale inventés ?
- Marges 15-25% : le calcul est-il maintenant correct, ou encore incomplet ?
- "Agents analysent" (vs "travaillent") : le framing est-il maintenant honnête, ou reste-t-il trompeur ?
- Disclaimer juridique : protège-t-il vraiment, ou est-ce une clause insuffisante ?

## D. VERDICT CONSOLIDÉ FINAL
Pour chaque livrable (A, B, C) : OUI / OUI MAIS / NON / PAS ENCORE — avec la condition résiduelle.
Puis un verdict global sur la stratégie de lancement.

## E. LA PROCHAINE ACTION UNIQUE
Si je ne peux faire qu'UNE chose avant de lancer, laquelle ? (pas une liste — UNE action prioritaire).
Et si je peux en faire trois, lesquelles dans l'ordre ?

Sois précis et concret. Je veux pouvoir décider après ta réponse.
"""

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

print(f"→ Appel OpenRouter : {MODEL}", file=sys.stderr)
print(f"→ Contexte envoyé : {len(SYSTEM)+len(USER):,} caractères", file=sys.stderr)
t0 = time.time()
try:
    r = requests.post(BASE_URL, headers=headers, json=payload, timeout=300)
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
    print(f"\n[TIMEOUT après {time.time()-t0:.0f}s]", file=sys.stderr)
    sys.exit(2)
except Exception as e:
    print(f"\n[ERREUR: {e}]", file=sys.stderr)
    sys.exit(3)
