from dataclasses import dataclass
from datetime import date, datetime

from sofafut.services.favorites_service import FavoritesService
from sofafut.services.fixture_service import FixtureService
from sofafut.services.match_details_service import MatchDetails, MatchDetailsService


@dataclass(frozen=True)
class FixtureRow:
    fixture_id: str
    date: str
    season: str
    round_name: str
    home_team: str
    score: str
    away_team: str
    venue: str


@dataclass(frozen=True)
class FavoritesViewData:
    rows: list[FixtureRow]
    subtitle: str


class MainController:
    def __init__(
        self,
        username: str,
        fixture_service: FixtureService | None = None,
        favorites_service: FavoritesService | None = None,
        match_details_service: MatchDetailsService | None = None,
    ) -> None:
        self.username = username
        self.fixture_service = fixture_service or FixtureService()
        self.favorites_service = favorites_service or FavoritesService()
        self.match_details_service = match_details_service or MatchDetailsService(self.fixture_service)

    def seasons(self) -> list[str]:
        return [str(season) for season in self.fixture_service.seasons()]

    def default_season(self) -> str:
        seasons = self.seasons()
        current_year = str(date.today().year)
        if current_year in seasons:
            return current_year
        return seasons[0] if seasons else ""

    def rounds(self, season: str) -> list[str]:
        if not season:
            return []
        return self.fixture_service.rounds(int(season))

    def default_round(self, season: str) -> str:
        rounds = self.rounds(season)
        if "Regular Season - 1" in rounds:
            return "Regular Season - 1"
        return rounds[0] if rounds else ""

    def date_options(self, season: str) -> list[tuple[str, str]]:
        if not season:
            return []
        today = self.fixture_service.today()
        days = self.fixture_service.dates(int(season))
        if season == str(date.today().year) and today not in days:
            days = sorted([*days, today])
        return [(day, self.format_day_label(day, today)) for day in days]

    def default_date(self, season: str) -> str:
        if not season:
            return ""
        today = self.fixture_service.today()
        if season == str(date.today().year):
            return today
        dates = self.fixture_service.dates(int(season))
        return dates[0] if dates else ""

    def format_day_label(self, day: str, today: str | None = None) -> str:
        today = today or self.fixture_service.today()
        if day == today:
            return "Hoje"
        try:
            return datetime.fromisoformat(day).strftime("%d/%m/%Y")
        except ValueError:
            return day

    def game_rows(self, season: str, round_name: str) -> list[FixtureRow]:
        if not season or not round_name:
            return []
        fixtures = self.fixture_service.fixtures(int(season), round_name)
        return [self._to_row(fixture) for fixture in fixtures]

    def game_rows_by_date(self, season: str, day: str) -> list[FixtureRow]:
        if not season or not day:
            return []
        fixtures = self.fixture_service.fixtures_by_date(int(season), day)
        return [self._to_row(fixture) for fixture in fixtures]

    def teams_with_favorite_state(self) -> list[tuple[str, bool]]:
        favorites = self.favorites()
        return [(team, team in favorites) for team in self.fixture_service.teams()]

    def favorites(self) -> set[str]:
        return self.favorites_service.get_favorites(self.username)

    def save_favorites(self, teams: set[str], season: str = "", day: str = "") -> FavoritesViewData:
        self.favorites_service.save_favorites(self.username, teams)
        return self.favorites_view_data(season, day)

    def favorites_view_data(self, season: str = "", day: str = "") -> FavoritesViewData:
        favorites = self.favorites()
        fixtures = self.fixture_service.favorite_fixtures(
            favorites,
            int(season) if season else None,
            day or None,
        )
        rows = [self._to_row(fixture) for fixture in fixtures]
        if favorites:
            day_label = self.format_day_label(day) if day else "todos os dias"
            subtitle = f"{day_label}: jogos de {', '.join(sorted(favorites))}."
        else:
            subtitle = "Nenhum time favorito selecionado no perfil."
        return FavoritesViewData(rows=rows, subtitle=subtitle)

    def match_details(self, fixture_id: str) -> MatchDetails:
        return self.match_details_service.details(fixture_id)

    def _to_row(self, fixture) -> FixtureRow:
        return FixtureRow(
            fixture_id=fixture.fixture_id,
            date=fixture.date[:16].replace("T", " "),
            season=str(fixture.season),
            round_name=fixture.round_name,
            home_team=fixture.home_team,
            score=fixture.score,
            away_team=fixture.away_team,
            venue=fixture.venue,
        )
