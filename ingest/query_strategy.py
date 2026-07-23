from dataclasses import dataclass
from pathlib import Path

import yaml

from ingest.europepmc import EuropePmcClient, EuropePmcId

DEFAULT_QUERIES_PATH = Path("config/queries.yaml")


@dataclass(frozen=True)
class QueryConfig:
    name: str
    label: str
    query: str


def load_queries(path: Path = DEFAULT_QUERIES_PATH) -> list[QueryConfig]:
    data = yaml.safe_load(path.read_text())
    return [QueryConfig(**entry) for entry in data["queries"]]


def _dedup_key(item: EuropePmcId) -> tuple[str, str]:
    if item.pmid:
        return ("pmid", item.pmid)
    return ("doi", (item.doi or "").lower())


def preview(queries_path: Path = DEFAULT_QUERIES_PATH) -> None:
    """Zeigt hitCount pro Anfrage und die Gesamtzahl nach Deduplizierung
    (PMID/DOI) -- laedt nur Kennungen, keine Titel/Abstracts/Volltexte."""
    client = EuropePmcClient()
    queries = load_queries(queries_path)

    print("Einzelne Anfragen:")
    for q in queries:
        count = client.hit_count(q.query)
        print(f"  {q.name:30} {count:>7}  ({q.label})")

    seen: set[tuple[str, str]] = set()
    total_raw = 0
    for q in queries:
        ids = list(client.search_ids(q.query))
        total_raw += len(ids)
        seen.update(_dedup_key(item) for item in ids)

    print()
    print(f"Treffer gesamt (mit Ueberschneidungen): {total_raw}")
    print(f"Eindeutige Artikel nach Deduplizierung:  {len(seen)}")


if __name__ == "__main__":
    preview()
