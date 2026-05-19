import csv
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from sofafut.infrastructure.settings import PROJECT_ROOT


SOFASCORE_NON_STAT_FIELDS = {
    "home_team_id",
    "home_team_name",
    "home_team_short_name",
    "away_team_id",
    "away_team_name",
    "away_team_short_name",
    "home_score_current",
    "away_score_current",
    "home_score_display",
    "away_score_display",
    "home_score_period1",
    "away_score_period1",
    "home_score_period2",
    "away_score_period2",
}


@dataclass(frozen=True)
class Fixture:
    fixture_id: str
    season: int
    round_name: str
    date: str
    home_team: str
    away_team: str
    goals_home: str
    goals_away: str
    venue: str
    status: str
    stats: dict[str, str] = field(default_factory=dict)

    @property
    def score(self) -> str:
        if self.goals_home == "" or self.goals_away == "":
            return "-"
        return f"{self.goals_home} x {self.goals_away}"

    @property
    def day(self) -> str:
        return self.date[:10]


class FixtureService:
    def __init__(self, csv_path: Path | None = None) -> None:
        self.csv_path = csv_path or self._default_csv_path()
        self._fixtures: list[Fixture] | None = None

    def seasons(self) -> list[int]:
        return sorted({fixture.season for fixture in self._load()})

    def rounds(self, season: int) -> list[str]:
        rounds = {fixture.round_name for fixture in self._load() if fixture.season == season}
        return sorted(rounds, key=self._round_number)

    def fixtures(self, season: int, round_name: str) -> list[Fixture]:
        return [
            fixture
            for fixture in self._load()
            if fixture.season == season and fixture.round_name == round_name
        ]

    def dates(self, season: int) -> list[str]:
        days = {fixture.day for fixture in self._load() if fixture.season == season and fixture.day}
        return sorted(days)

    def fixtures_by_date(self, season: int, day: str) -> list[Fixture]:
        return [
            fixture
            for fixture in self._load()
            if fixture.season == season and fixture.day == day
        ]

    def fixture_by_id(self, fixture_id: str) -> Fixture | None:
        return next((fixture for fixture in self._load() if fixture.fixture_id == fixture_id), None)

    def teams(self) -> list[str]:
        names: set[str] = set()
        for fixture in self._load():
            names.add(fixture.home_team)
            names.add(fixture.away_team)
        return sorted(names)

    def favorite_fixtures(self, favorite_teams: set[str], season: int | None = None, day: str | None = None) -> list[Fixture]:
        if not favorite_teams:
            return []
        return [
            fixture
            for fixture in self._load()
            if (fixture.home_team in favorite_teams or fixture.away_team in favorite_teams)
            and (season is None or fixture.season == season)
            and (day is None or fixture.day == day)
        ]

    def today(self) -> str:
        return date.today().isoformat()

    def _load(self) -> list[Fixture]:
        if self._fixtures is not None:
            return self._fixtures
        if not self.csv_path.exists():
            self._fixtures = []
            return self._fixtures

        with self.csv_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            self._fixtures = [self._row_to_fixture(row) for row in reader]
        return self._fixtures

    def _row_to_fixture(self, row: dict[str, str]) -> Fixture:
        if "event_id" in row:
            return Fixture(
                fixture_id=row["event_id"],
                season=int(row["season_year"]),
                round_name=f"Rodada {row['round']}",
                date=row["date"],
                home_team=row["home_team_name"],
                away_team=row["away_team_name"],
                goals_home=row["home_score_current"],
                goals_away=row["away_score_current"],
                venue="",
                status=row["status_description"],
                stats=self._row_stats(row),
            )
        return Fixture(
            fixture_id=row["fixture_id"],
            season=int(row["season"]),
            round_name=row["round"],
            date=row["date"],
            home_team=row["home_team_name"],
            away_team=row["away_team_name"],
            goals_home=row["goals_home"],
            goals_away=row["goals_away"],
            venue=row["venue_name"],
            status=row["status_short"],
        )

    def _default_csv_path(self) -> Path:
        sofascore_paths = sorted((PROJECT_ROOT / "data").glob("sofascore_brasileirao_*_partidas.csv"))
        if sofascore_paths:
            return sofascore_paths[-1]
        return PROJECT_ROOT / "data" / "brasileirao_2022_2024_partidas.csv"

    def _row_stats(self, row: dict[str, str]) -> dict[str, str]:
        return {
            key: value
            for key, value in row.items()
            if key.startswith(("home_", "away_", "label_")) and key not in SOFASCORE_NON_STAT_FIELDS
        }

    def _round_number(self, round_name: str) -> int:
        try:
            return int(round_name.rsplit("-", 1)[1].strip())
        except (IndexError, ValueError):
            return 0
