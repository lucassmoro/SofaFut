import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sofafut.infrastructure.settings import get_env_int, get_required_env, load_env


@dataclass(frozen=True)
class ApiFootballResponse:
    endpoint: str
    parameters: dict[str, Any]
    response: list[dict[str, Any]]
    requests_used_today: int
    requests_remaining_today: int


class ApiFootballClient:
    def __init__(self, counter_path: Path | None = None) -> None:
        load_env()
        self.api_key = get_required_env("API_FOOTBALL_KEY")
        self.base_url = get_required_env("API_FOOTBALL_BASE_URL").rstrip("/")
        self.daily_limit = get_env_int("API_FOOTBALL_DAILY_LIMIT", 100)
        self.counter_path = counter_path or Path("data/api_football_requests.json")

    def get(self, endpoint: str, params: dict[str, Any]) -> ApiFootballResponse:
        self._reserve_request()
        query = urlencode({key: value for key, value in params.items() if value is not None})
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if query:
            url = f"{url}?{query}"

        request = Request(url, headers={"x-apisports-key": self.api_key})
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))

        errors = payload.get("errors")
        if errors:
            raise RuntimeError(f"API-Football retornou erro em {endpoint}: {errors}")

        counter = self._read_counter()
        return ApiFootballResponse(
            endpoint=endpoint,
            parameters=params,
            response=payload.get("response", []),
            requests_used_today=counter["count"],
            requests_remaining_today=max(self.daily_limit - counter["count"], 0),
        )

    def _reserve_request(self) -> None:
        from datetime import date

        today = date.today().isoformat()
        counter = self._read_counter()
        if counter["date"] != today:
            counter = {"date": today, "count": 0}
        if counter["count"] >= self.daily_limit:
            raise RuntimeError("Limite diario local da API-Football atingido.")

        counter["count"] += 1
        self.counter_path.parent.mkdir(parents=True, exist_ok=True)
        self.counter_path.write_text(json.dumps(counter, indent=2), encoding="utf-8")

    def _read_counter(self) -> dict[str, Any]:
        from datetime import date

        if not self.counter_path.exists():
            return {"date": date.today().isoformat(), "count": 0}
        return json.loads(self.counter_path.read_text(encoding="utf-8"))
