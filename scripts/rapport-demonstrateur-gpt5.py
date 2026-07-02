#!/usr/bin/env python3
"""
Action 2 — Rapport démonstrateur evergreen (produit non saisonnier).
Généré par GPT-5 (via OpenRouter) selon le format strict validé par l'analyse critique.
Sauvegarde le rapport dans knowledge-base/synthesis/10-RAPPORT-DEMONSTRATEUR-EVERGREEN.md
"""
import sys, time, requests

API_KEY = "REDACTEDee58e407d5135ab255bd908a12b02e624632dff5d77e4e303f526e81efc5bb48"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-5.5"
OUT = "/home/tars/import-export-project/knowledge-base/synthesis/10-RAPPORT-DEMONSTRATEUR-EVERGREEN.md"

SYSTEM = """Tu es un ANALYSTE IMPORT senior (10+ ans). Tu ne vends rien. Tu produis un RAPPORT DE DUE DILIGENCE pour un primo-importateur.
Ton anti-biais : jamais une marge sans tous les postes de coûts ; jamais un verdict sans scénario pessimiste crédible.
Tu sais que 90% des certificats CE chinois fournis par défaut sont non conformes.
Tu refuses le mot "validé" pour quoi que ce soit que tu n'as pas physiquement vérifié. Tu dis "identifié, à valider".

FORMAT DE RAPPORT STRICT (10 sections, dans cet ordre) :
1. PRODUIT — description, pourquoi candidat evergreen, hypothèse de départ
2. FOURNISSEUR IDENTIFIÉ — région/plateforme 1688/Alibaba, type usine, MOQ estimé, STATUT : identifié / non validé
3. PRIX FOB — fourchette ¥/€/usd, source (transcript croisé ou estimation plafond marché), limites de l'estimation
4. COÛT COMPLET DÉTAILLÉ — tableau poste par poste : FOB, fret, assurance, droits de douane, TVA trésorerie, inspection, emballage, EPR/DEEE, assurance RC produit, échantillons. TOTAL €/unité
5. CONFORMITÉ UE — directives applicables (LVD/EMC/RoHS/REACH/CE 1935/2004 contact alimentaire si pertinent/WEEE/EPR), documents à exiger, qui valide vraiment (organisme notifié). Honnête : pas "simple"
6. SATURATION MARCHÉ — Amazon.fr résultats keyword, vendeurs >100 avis, Google Trends, marques établies. Verdict sous-exploité/saturé/à confirmer
7. RETOURS & SAV — taux estimé par catégorie, garantie 2 ans, pièces détachées, coût SAV % CA
8. 3 SCÉNARIOS — tableau : Pire (ventes -30%, retours doublés, promos) / Médian (base de décision) / Optimiste (conditions annoncées). Pour chaque : prix vente, marge nette %, gain/perte, cash immobilisé, stock restant
9. DÉCISION GO / NO-GO / PAS ENCORE — verdict + conditions strictes
10. VÉRIFICATIONS AVANT COMMANDE — checklist concrète (échantillon, SGS, code HS confirmé par transitaire, NNN, etc.)

Tu réponds en FRANÇAIS. Tu utilises des nombres concrets. Tu cites tes hypothèses. Tu ne flattes pas."""

USER = """MISSION : produire LE rapport démonstrateur du Roster — un produit EVERGREEN (non saisonnier) qui prouve que le système fait mieux qu'un prompt ChatGPT.

ÉTAPE 1 — Choisis le meilleur candidat parmi ces 3 pour un démonstrateur anti-biais ÉQUILIBRÉ (l'analyse doit révéler des choses : ni un "go" évident ni un "no-go" trivial). Justifie ton choix en 3 lignes max.

Candidats :
A. SET D'USTENSILES DE CUISINE EN INOX (bol mélangeur ou set complet) — conformité contact alimentaire CE 1935/2004 + DGCCRF France + EPR emballages, pas de batterie/électrique, evergreen, marché large, logistique simple (mais produits pondéreux)
B. ORGANISEUR DE COFFRE DE VOITURE (polyester/nylon modulable) — pas de conformité électrique, marché auto stable evergreen, logistique légère, EPR textile possible, marché Amazon saturé ?
C. BOUTELLE ISOTHERME INOX DOUBLE PAROI (type Hydro Flask) — conformité contact alimentaire + étiquetage, marché fitness/outdoor evergreen en croissance, saturation Amazon élevée, logistique pondéreuse, risque contrefaçon design

ÉTAPE 2 — Produis le rapport COMPLET pour ton candidat choisi, en suivant strictement les 10 sections du format ci-dessus.

EXIGENCES NUMÉRIQUES (sois précis, pas vague) :
- Prix FOB : fourchette réelle ¥ et € (tu peux estimer à partir de ta connaissance du marché 1688/Alibaba 2024-2026)
- Coût complet : tableau avec au moins 10 postes, en €/unité, pour un MOQ précis (ex: 500 ou 1000 pièces)
- Marge nette médiane : réaliste (après marketing 20-30%, retours 5-12%, SAV 5%, stockage, EPR/DEEE, RC produit). NE DÉPASSE PAS 25% en B2C sauf justification forte.
- 3 scénarios chiffrés : CA, coût marchandises, frais variables, marketing, résultat net, cash immobilisé
- Saturation : chiffres Amazon.fr / Google Trends réalistes

Sois impitoyable sur les marges. Un bon démonstrateur montre OÙ l'argent disparaît, pas combien on gagne.

Termine par une SECTION FINALE "À retenir pour le Roster" (3 puces) : ce que ce rapport démontre de mieux qu'un simple prompt ChatGPT."""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER},
    ],
    "temperature": 0.5,
    "max_tokens": 14000,
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://localhost",
    "X-Title": "pi-coding-agent",
}

print(f"→ Génération rapport démonstrateur via {MODEL}", file=sys.stderr)
t0 = time.time()
try:
    r = requests.post(BASE_URL, headers=headers, json=payload, timeout=300)
    dt = time.time() - t0
    print(f"→ HTTP {r.status_code} en {dt:.1f}s", file=sys.stderr)
    if r.status_code != 200:
        print("ERREUR:", r.text[:2000], file=sys.stderr)
        sys.exit(1)
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})

    header = f"""# ⬡ RAPPORT DÉMONSTRATEUR EVERGREEN — Drop #002

> Généré par **{data.get('model', MODEL)}** via OpenRouter.
> Format : due diligence import anti-biais (10 sections).
> Rôle : prouver que le Roster produit mieux qu'un prompt ChatGPT.
> Date : 2026-06-20 · Bêta — produit identifié, non validé physiquement.

---

"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(header + content)
    print(f"\n✓ Rapport sauvegardé : {OUT}", file=sys.stderr)
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
