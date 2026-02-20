from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class SeedMeta:
    path: str
    executions: int = 0
    novelty_hits: int = 0
    crash_hits: int = 0

    @property
    def energy(self) -> float:
        return 1.0 + (self.novelty_hits * 2.0) + (self.crash_hits * 4.0) / (1 + self.executions)


class Corpus:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.meta_path = self.root / "metadata.json"
        self._metadata: dict[str, SeedMeta] = {}
        self._content_hashes: set[str] = set()
        self._load_metadata()
        self._refresh_hashes()

    def _load_metadata(self) -> None:
        if not self.meta_path.exists():
            return
        raw = json.loads(self.meta_path.read_text(encoding="utf-8"))
        for item in raw:
            m = SeedMeta(**item)
            self._metadata[m.path] = m

    def _save_metadata(self) -> None:
        payload = [asdict(v) for v in sorted(self._metadata.values(), key=lambda x: x.path)]
        self.meta_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _hash_program(self, program: str) -> str:
        return hashlib.sha256(program.encode("utf-8", errors="ignore")).hexdigest()

    def _refresh_hashes(self) -> None:
        self._content_hashes.clear()
        for seed in self.seeds():
            self._content_hashes.add(self._hash_program(seed.read_text(encoding="utf-8")))

    def seeds(self) -> list[Path]:
        return sorted(self.root.glob("*.js"))

    def choose_seed(self, rng: random.Random) -> tuple[str, str] | tuple[None, None]:
        seeds = self.seeds()
        if not seeds:
            return None, None
        metas: list[SeedMeta] = []
        for p in seeds:
            rel = p.name
            meta = self._metadata.get(rel, SeedMeta(path=rel))
            metas.append(meta)
            self._metadata[rel] = meta
        selected = rng.choices(metas, weights=[m.energy for m in metas], k=1)[0]
        selected.executions += 1
        self._save_metadata()
        path = self.root / selected.path
        return path.read_text(encoding="utf-8"), selected.path

    def add(self, program: str) -> Path | None:
        fingerprint = self._hash_program(program)
        if fingerprint in self._content_hashes:
            return None
        next_id = len(self.seeds())
        out = self.root / f"seed_{next_id:06d}.js"
        out.write_text(program, encoding="utf-8")
        self._content_hashes.add(fingerprint)
        self._metadata[out.name] = SeedMeta(path=out.name)
        self._save_metadata()
        return out

    def import_directory(self, source: Path, limit: int | None = None) -> int:
        added = 0
        for js in sorted(source.glob("*.js")):
            if limit is not None and added >= limit:
                break
            content = js.read_text(encoding="utf-8", errors="ignore")
            if self.add(content):
                added += 1
        return added

    def mark_novel(self, seed_name: str | None) -> None:
        if not seed_name:
            return
        meta = self._metadata.get(seed_name)
        if not meta:
            return
        meta.novelty_hits += 1
        self._save_metadata()

    def mark_crash(self, seed_name: str | None) -> None:
        if not seed_name:
            return
        meta = self._metadata.get(seed_name)
        if not meta:
            return
        meta.crash_hits += 1
        self._save_metadata()
