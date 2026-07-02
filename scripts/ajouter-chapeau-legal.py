#!/usr/bin/env python3
"""
Ajoute un chapeau légal uniforme en tête de chaque fichier synthesis (01-10).
Mesure de conformité : transforme la nature juridique de tous les fichiers d'un coup.
Idempotent (ne réinsère pas si déjà présent).
"""
import os, re

SDIR = "/home/tars/import-export-project/knowledge-base/synthesis"
MARKER = "Notes originales, non verbatim"

HEADER = (
    "\n"
    "> ⚠️ **Notes originales, non verbatim.** Sources publiques (vidéos YouTube, plateformes\n"
    "> B2B, données officielles) — voir `../../NOTICE-SOURCES.md` et `../../POLITIQUE-CITATION.md`.\n"
    "> Citations courtes uniquement (CPI art. L122-5 3°). Aucun transcript brut n'est inclus dans ce dépôt.\n"
)

changed = []
skipped = []
for fname in sorted(os.listdir(SDIR)):
    if not fname.endswith(".md"):
        continue
    if not re.match(r"^\d{2}-", fname):
        continue
    path = os.path.join(SDIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER in content:
        skipped.append(fname)
        continue

    # Trouver la fin du premier titre H1
    lines = content.split("\n")
    insert_after = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            insert_after = i + 1
            break

    if insert_after == 0:
        # Pas de H1, insérer au début
        new_content = HEADER.lstrip("\n") + "\n" + content
    else:
        # Insérer après la ligne H1
        new_lines = lines[:insert_after] + [HEADER.rstrip("\n")] + lines[insert_after:]
        new_content = "\n".join(new_lines)

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    changed.append(fname)

print(f"✓ Chapeau légal ajouté à {len(changed)} fichier(s) :")
for f in changed:
    print(f"  - {f}")
if skipped:
    print(f"⊘ Déjà présent (ignorés) dans {len(skipped)} fichier(s) :")
    for f in skipped:
        print(f"  - {f}")
