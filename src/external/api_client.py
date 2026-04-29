import requests


class SofaScoreApiClient:

    BASE_URL = "https://api.sofascore.com/api/v1"

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.sofascore.com/",
        "Origin": "https://www.sofascore.com",
    }

    def __init__(self, timeout=15):
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(self.DEFAULT_HEADERS)

    def _get(self, path: str, **params) -> dict:
        url = f"{self.BASE_URL}{path}"
        response = self._session.get(url, params=params, timeout=self._timeout)

        if response.status_code != 200:
            raise RuntimeError(
                f"HTTP {response.status_code} em {response.url}\n"
                f"{response.text[:200]}"
            )

        return response.json()

    def get_live_events(self, sport: str = "football") -> dict:
        return self._get(f"/sport/{sport}/events/live")

    def get_events_by_date(self, dia: str, sport: str = "football") -> dict:
        return self._get(f"/sport/{sport}/scheduled-events/{dia}")

    def get_event(self, event_id: int) -> dict:
        return self._get(f"/event/{event_id}")

    def get_event_statistics(self, event_id: int) -> dict:
        return self._get(f"/event/{event_id}/statistics")

    def get_event_lineups(self, event_id: int) -> dict:
        return self._get(f"/event/{event_id}/lineups")

    def get_event_incidents(self, event_id: int) -> dict:
        return self._get(f"/event/{event_id}/incidents")

    def get_event_odds(self, event_id: int) -> dict:
        return self._get(f"/event/{event_id}/odds/1/all")

    def search(self, query: str, page: int = 0) -> dict:
        return self._get("/search/all", q=query, page=page)

    def get_player(self, player_id: int) -> dict:
        return self._get(f"/player/{player_id}")

    def get_player_statistics(self, player_id: int) -> dict:
        return self._get(f"/player/{player_id}/statistics/overall")

    def get_team(self, team_id: int) -> dict:
        return self._get(f"/team/{team_id}")

    def get_team_players(self, team_id: int) -> dict:
        return self._get(f"/team/{team_id}/players")