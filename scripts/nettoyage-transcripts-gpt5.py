#!/usr/bin/env python3
"""
Nettoyage droits d'auteur (GPT-5 via OpenRouter).
Scanne les 9 synthèses existantes, identifie les passages à risque (verbatim,
citations longues, structure reconnaissable), produit :
  1. Un audit des passages à risque par fichier
  2. Des reformulations originales proposées
  3. Une POLITIQUE DE CITATION type
  4. Une NOTICE bibliographique des sources (NOTICE-SOURCES.md)
Sauvegarde dans : scripts/nettoyage-transcripts-gpt5.md
"""
import sys, time, requests, os

API_KEY = "REDACTEDee58e407d5135ab255bd908a12b02e624632dff5d77e4e303f526e81efc5bb48"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-5.5"
OUT = "/home/tars/import-export-project/scripts/nettoyage-transcripts-gpt5.md"
BASE = "/home/tars/import-export-project"

def read(p):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[MANQUANT: {p}]"

# Charger les 9 synthèses avec délimiteurs clairs
syntheses_content = []
sdir = f"{BASE}/knowledge-base/synthesis"
synth_files = sorted([f for f in os.listdir(sdir) if f.startswith(("0", "1")) and f.endswith(".md")])
for fname in synth_files:
    content = read(f"{sdir}/{fname}")
    syntheses_content.append(f"### FICHIER : {fname}\n\n{content}\n\n---\n")
ALL_SYNTH = "\n".join(syntheses_content)

AUDIT = read(f"{BASE}/scripts/audit-juridique-gpt5.md")
# Garder juste la section transcripts pour réduire tokens
audit_short = AUDIT[:8000]  # la synthèse exécutive + point 1 suffisent

SYSTEM = """Tu es un JURISTE + ÉDITEUR spécialisé en propriété intellectuelle et conformité documentaire.
Tu connais le CPI français (contrefaçon L335-2/L335-3, exception courte citation L122-5 3°, droits moraux L121-1).

TA MISSION : rendre une base de connaissances exploitée commercialement CONFORME au droit d'auteur,
en transformant des synthèses dérivées de transcripts YouTube en NOTES ORIGINALES SOURCÉES,
sans perdre la valeur informationnelle.

PRINCIPES DIRECTEURS :
1. Les FAITS, PRIX, MÉTHODES, DONNÉES TECHNIQUES ne sont PAS protégeables → on peut les retenir
2. La STRUCTURE pédagogique, les FORMULATIONS caractéristiques, les EXEMPLES propres à un auteur → à reformuler
3. Jamais de citation > 30 mots sans guillemets + source + but critique/pédagogique
4. Toujours sourcer : titre vidéo, chaîne, URL, date de consultation (bibliographie)
5. Reformuler = restructurer, pas paraphraser mot à mot

Tu réponds en FRANÇAIS. Tu es concret et actionnable : pour chaque passage à risque,
tu donnes la reformulation directement applicable."""

USER = f"""CONTEXTE : Le projet "Operator Roster" dispose de 9 fichiers de synthèse dans
`knowledge-base/synthesis/` dérivés de 40 transcripts YouTube (7 chaînes). Les transcripts bruts
viennent d'être archivés hors repo (mesure de sécurité prise).

L'audit juridique (extrait pertinent ci-dessous) recommande de transformer les synthèses
en "notes originales non verbatim, sourcées par URL".

## EXTRAIT AUDIT JURIDIQUE (rappel du cadre)
{audit_short[:6000]}

---

## LES 9 SYNTHÈSES À AUDITER

{ALL_SYNTH}

---

## TA MISSION — 4 LIVRABLES

### LIVRABLE 1 — AUDIT DES PASSAGES À RISQUE (par fichier)
Pour chaque fichier (01 à 09), identifie précisément :
- Citations entre guillemets > 30 mots (risque : reproduction sans autorisation)
- Citations attribuées nommément à un YouTubeur avec verbatim
- Tableaux/structures qui reproduisent la pédagogie d'un auteur
- Phrases très caractéristiques reconnaissables

Format par fichier :
```
#### [nom fichier]
- LIGNE X : « passage exact » → RISQUE (reproduction / citation non sourcée / etc.)
- ...
- VERDICT fichier : X passages à corriger / Y à sourcer / OK sinon
```

### LIVRABLE 2 — REFORMULATIONS PRIORITAIRES
Pour les 10-15 passages les plus risqués (les plus longs ou les plus reconnaissables),
donne la reformulation originale DIRECTEMENT APPLICABLE :
```
AVANT : « citation problématique exacte »
APRÈS : [ta reformulation originale, non verbatim, qui retient le fait/info sans la forme]
SOURCE À INDIQUER : chaîne + URL + date
```

### LIVRABLE 3 — POLITIQUE DE CITATION TYPE (à inclure dans le projet)
Rédige une politique de citation courte et opérationnelle (1 page max) que l'éditeur
peut inclure dans le repo et afficher. Elle doit couvrir :
- Qu'est-ce qui est retenu (faits vs expressions)
- Comment sourcer (format bibliographique)
- Règle des citations courtes
- Droit de retrait des créateurs
- Disclaimer général

### LIVRABLE 4 — NOTICE BIBLIOGRAPHIQUE DES SOURCES (NOTICE-SOURCES.md)
Génère le contenu COMPLET d'un fichier `NOTICE-SOURCES.md` à mettre à la racine du projet,
listant les 7 chaînes YouTube utilisées comme sources d'apprentissage, avec :
- Nom de la chaîne / créateur
- URL chaîne
- Type de contenu
- Fiabilité (✅ FIABLE / ⚠️ PARTIEL)
- Conflit d'intérêt déclaré
- Lien vers l'audit complet
- Politique d'usage (reformulation originale, citation stricte, droit de retrait)
- Pour les chaînes identifiées dans l'audit : @StartBusinessWorld, @CargoFamily,
  @SINOSOURCING (Fabien Dessaint), @lineborrajo, @Sebastien.selfmadeprogram, @saadbenshow
  + une 7e si identifiable dans les synthèses

SOis exhaustif et précis. Ces 4 livrables vont directement dans le repo pour rendre le
projet conforme avant la bêta. Je veux pouvoir COPIER-COLLER le livrable 3 et 4 tels quels."""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER},
    ],
    "temperature": 0.4,
    "max_tokens": 14000,
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://localhost",
    "X-Title": "pi-coding-agent",
}

print(f"→ Nettoyage droits d'auteur via {MODEL}", file=sys.stderr)
print(f"→ Contexte : {len(ALL_SYNTH):,} caractères de synthèses + audit", file=sys.stderr)
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

    header = f"""# 📝 NETTOYAGE DROITS D'AUTEUR — Synthèses & Politique de citation

> Généré par **{data.get('model', MODEL)}** via OpenRouter.
> Date : 2026-06-20 · Suite à l'audit juridique (`audit-juridique-gpt5.md`).
> Objectif : rendre les 9 synthèses conformes au CPI avant bêta.

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
