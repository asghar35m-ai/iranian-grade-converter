from collections.abc import Iterator
from dataclasses import dataclass

from pydantic import BaseModel

from core.config import get_session

SEARCH_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

# Offene Annahme: CLAUDE.md pinnt nur NCBI auf 3/10 Anfragen pro Sekunde.
# Fuer Europe PMC steht dort nichts fest -- 5/s ist eine defensive Schaetzung,
# die wir beim ersten 429 nach unten korrigieren.
MAX_CALLS_PER_SECOND = 5

# Europe PMC erlaubt bis zu 1000 Treffer pro Seite -- fuer reine ID-Listen
# (Dedup-Check) sind wenige, grosse Seiten schneller als viele kleine.
ID_PAGE_SIZE = 1000


class EuropePmcArticle(BaseModel):
    pmid: str | None
    doi: str | None = None
    title: str
    abstract: str | None = None
    is_open_access: bool
    full_text_url: str | None = None
    pub_year: int | None = None
    source: str


@dataclass(frozen=True)
class EuropePmcId:
    pmid: str | None
    doi: str | None


def _parse_article(result: dict) -> EuropePmcArticle:
    full_text_url = None
    for entry in result.get("fullTextUrlList", {}).get("fullTextUrl", []):
        if entry.get("availabilityCode") == "OA":
            full_text_url = entry["url"]
            break

    pub_year = result.get("pubYear")
    return EuropePmcArticle(
        pmid=result.get("pmid"),
        doi=result.get("doi"),
        title=result["title"],
        abstract=result.get("abstractText"),
        is_open_access=result.get("isOpenAccess") == "Y",
        full_text_url=full_text_url,
        pub_year=int(pub_year) if pub_year else None,
        source=result.get("source", "MED"),
    )


class EuropePmcClient:
    """Kennt nur die Europe-PMC-API, gibt Pydantic-Objekte zurueck.

    Kein DB-Zugriff, kein eigenes Caching -- beides sitzt zentral in
    core/config.py (get_session), wie in CLAUDE.md gefordert.
    """

    def __init__(self) -> None:
        self._session = get_session(
            "www.ebi.ac.uk", max_calls=MAX_CALLS_PER_SECOND, period=1.0
        )

    def hit_count(self, query: str) -> int:
        """Gesamttrefferzahl einer Anfrage, ohne Ergebnisse zu laden (pageSize=1)."""
        response = self._session.get(
            SEARCH_URL,
            params={
                "query": query,
                "format": "json",
                "resultType": "lite",
                "pageSize": 1,
            },
        )
        response.raise_for_status()
        return response.json().get("hitCount", 0)

    def search_ids(self, query: str) -> Iterator[EuropePmcId]:
        """Liefert nur PMID/DOI aller Treffer -- fuer Dedup-Checks vor dem
        eigentlichen Download von Titel/Abstract/Volltext."""
        cursor_mark = "*"

        while True:
            response = self._session.get(
                SEARCH_URL,
                params={
                    "query": query,
                    "format": "json",
                    "resultType": "lite",
                    "pageSize": ID_PAGE_SIZE,
                    "cursorMark": cursor_mark,
                },
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("resultList", {}).get("result", [])
            if not results:
                break

            for result in results:
                yield EuropePmcId(pmid=result.get("pmid"), doi=result.get("doi"))

            next_cursor_mark = data.get("nextCursorMark")
            if not next_cursor_mark or next_cursor_mark == cursor_mark:
                break
            cursor_mark = next_cursor_mark

    def search(
        self, query: str, page_size: int = 100, max_results: int = 500
    ) -> Iterator[EuropePmcArticle]:
        """Durchsucht Europe PMC und liefert Artikel-fuer-Artikel per Cursor-Pagination."""
        cursor_mark = "*"
        fetched = 0

        while fetched < max_results:
            response = self._session.get(
                SEARCH_URL,
                params={
                    "query": query,
                    "format": "json",
                    "resultType": "core",
                    "pageSize": min(page_size, max_results - fetched),
                    "cursorMark": cursor_mark,
                },
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("resultList", {}).get("result", [])
            if not results:
                break

            for result in results:
                yield _parse_article(result)
                fetched += 1
                if fetched >= max_results:
                    return

            next_cursor_mark = data.get("nextCursorMark")
            if not next_cursor_mark or next_cursor_mark == cursor_mark:
                break
            cursor_mark = next_cursor_mark
