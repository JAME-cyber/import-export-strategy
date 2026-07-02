"""Journal d'audit append-only avec chaînage cryptographique SHA-256.

Le journal est inspiré d'un fonctionnement WORM applicatif : chaque entrée est
écrite en JSONL, contient le hash de l'entrée précédente et son propre hash.
Toute modification, suppression ou réordonnancement rompt l'intégrité vérifiable.

Ce mécanisme ne remplace pas un stockage WORM matériel ou cloud immuable, mais
fournit une preuve applicative robuste et testable.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .models import ActorType, OfficialSource, utc_now

GENESIS_HASH = "0" * 64


class JournalEntry(BaseModel):
    """Entrée atomique du journal d'audit."""

    model_config = ConfigDict(extra="forbid")

    index: int = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=utc_now)
    actor: ActorType
    action: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    sources: list[OfficialSource] = Field(default_factory=list)
    previous_hash: str = Field(..., min_length=64, max_length=64)
    hash: str = Field(..., min_length=64, max_length=64)


def _json_default(value: Any) -> Any:
    """Convertit les objets non JSON natifs en représentation stable."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "value"):
        return value.value
    return str(value)


def _canonical_json(data: dict[str, Any]) -> str:
    """Sérialise un dictionnaire en JSON canonique pour hashing."""
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=_json_default)


def compute_entry_hash(entry_without_hash: dict[str, Any]) -> str:
    """Calcule le SHA-256 canonique d'une entrée sans son champ ``hash``."""
    canonical = _canonical_json(entry_without_hash)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AuditJournal:
    """Journal append-only hash-chaîné."""

    _process_lock = threading.Lock()

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(
        self,
        *,
        actor: ActorType,
        action: str,
        payload: dict[str, Any] | None = None,
        sources: list[OfficialSource] | None = None,
    ) -> JournalEntry:
        """Ajoute une entrée au journal et force l'écriture disque."""
        if not action.strip():
            raise ValueError("L'action journalisée ne peut pas être vide.")

        with self._process_lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            last_index, last_hash = self._last_index_and_hash()

            entry_without_hash: dict[str, Any] = {
                "index": last_index + 1,
                "timestamp": utc_now().isoformat(),
                "actor": actor.value,
                "action": action.strip(),
                "payload": payload or {},
                "sources": [source.model_dump(mode="json") for source in (sources or [])],
                "previous_hash": last_hash,
            }
            entry_hash = compute_entry_hash(entry_without_hash)
            entry_data = {**entry_without_hash, "hash": entry_hash}
            entry = JournalEntry.model_validate(entry_data)

            # IMPORTANT : on sérialise le dict PRIMITIF utilisé pour le hash, SANS
            # round-trip Pydantic. Sinon la sérialisation datetime (+00:00 -> Z)
            # dérive et verify_integrity() échoue.
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(_canonical_json(entry_data) + "\n")
                handle.flush()
                os.fsync(handle.fileno())

            return entry

    def read_entries(self) -> list[JournalEntry]:
        """Lit toutes les entrées du journal."""
        if not self.path.exists():
            return []

        entries: list[JournalEntry] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    entries.append(JournalEntry.model_validate_json(stripped))
                except Exception as exc:  # pragma: no cover - message enrichi pour exploitation
                    raise ValueError(f"Entrée de journal invalide ligne {line_number}: {exc}") from exc
        return entries

    def _read_raw_lines(self) -> list[dict[str, Any]]:
        """Lit les lignes brutes du journal comme dicts (sans round-trip modèle).

        Indispensable pour la vérification : on recalcule les hashes sur la forme
        PRIMITIVE exacte qui a été stockée, sans repasser par Pydantic (sinon la
        sérialisation datetime dérive : +00:00 vs Z).
        """
        if not self.path.exists():
            return []
        out: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    out.append(json.loads(stripped))
                except Exception as exc:
                    raise ValueError(f"Ligne {line_number} non JSON: {exc}") from exc
        return out

    def verify_integrity(self) -> bool:
        """Vérifie l'intégrité complète du journal.

        Retourne ``False`` si une entrée a été modifiée, supprimée ou réordonnée.
        Travaille sur les dicts bruts pour garantir la cohérence du hash.
        """
        try:
            raw_entries = self._read_raw_lines()
        except Exception:
            return False

        previous_hash = GENESIS_HASH
        for expected_index, data in enumerate(raw_entries):
            if data.get("index") != expected_index:
                return False
            if data.get("previous_hash") != previous_hash:
                return False

            stored_hash = data.get("hash")
            without_hash = {k: v for k, v in data.items() if k != "hash"}
            if compute_entry_hash(without_hash) != stored_hash:
                return False

            previous_hash = stored_hash

        return True

    def _last_index_and_hash(self) -> tuple[int, str]:
        """Retourne l'index et le hash de la dernière entrée valide."""
        if not self.path.exists():
            return -1, GENESIS_HASH

        entries = self.read_entries()
        if not entries:
            return -1, GENESIS_HASH
        if not self.verify_integrity():
            raise ValueError("Journal corrompu : append refusé pour préserver l'audit trail.")
        last = entries[-1]
        return last.index, last.hash


def verify_integrity(path: str | Path) -> bool:
    """Vérifie l'intégrité d'un journal d'audit."""
    return AuditJournal(path).verify_integrity()
