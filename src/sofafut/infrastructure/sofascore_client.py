import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class SofascoreSeason:
    id: int
    year: str
    name: str


class SofascoreClient:
    def __init__(self, base_url: str = "https://www.sofascore.com/api/v1") -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }

    def seasons(self, unique_tournament_id: int) -> list[SofascoreSeason]:
        payload = self.get(f"unique-tournament/{unique_tournament_id}/seasons")
        return [
            SofascoreSeason(
                id=int(season["id"]),
                year=str(season.get("year", "")),
                name=str(season.get("name", "")),
            )
            for season in payload.get("seasons", [])
        ]

    def paged_events(self, unique_tournament_id: int, season_id: int, page_kind: str) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        page = 0
        while True:
            payload = self.get(
                f"unique-tournament/{unique_tournament_id}/season/{season_id}/events/{page_kind}/{page}"
            )
            events.extend(payload.get("events", []))
            if not payload.get("hasNextPage"):
                return events
            page += 1

    def round_events(self, unique_tournament_id: int, season_id: int, round_number: int) -> list[dict[str, Any]]:
        payload = self.get(
            f"unique-tournament/{unique_tournament_id}/season/{season_id}/events/round/{round_number}"
        )
        return payload.get("events", [])

    def event_statistics(self, event_id: int) -> dict[str, Any]:
        return self.get(f"event/{event_id}/statistics")

    def event_lineups(self, event_id: int) -> dict[str, Any]:
        return self.get(f"event/{event_id}/lineups")

    def get(self, endpoint: str) -> dict[str, Any]:
        request = Request(f"{self.base_url}/{endpoint.lstrip('/')}", headers=self.headers)
        last_error: Exception | None = None
        for attempt in range(4):
            try:
                with urlopen(request, timeout=30) as response:
                    return json.loads(response.read().decode("utf-8"))
            except (ConnectionResetError, HTTPError, URLError) as exc:
                last_error = exc
                time.sleep(0.8 * (attempt + 1))

        raise RuntimeError(f"Falha ao consultar Sofascore em {request.full_url}: {last_error}") from last_error
