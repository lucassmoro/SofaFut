from dataclasses import dataclass
from datetime import date, datetime

from sofafut.controllers.auth_controller import AuthController
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


@dataclass(frozen=True)
class PlayerViewRow:
    player_id: str
    name: str
    team: str
    position: str
    value: float
    owned: bool = False
    favorite: bool = False
    captain: bool = False
    points: float = 0.0


@dataclass(frozen=True)
class StatViewRow:
    player_id: str
    player_name: str
    team: str
    position: str
    goals: int
    assists: int
    tackles: int
    shots: int
    passes: int
    pass_accuracy: float
    yellow_cards: int
    red_cards: int


@dataclass(frozen=True)
class RankingViewRow:
    position: int
    username: str
    points: float
    balance: float


@dataclass(frozen=True)
class HistoryViewRow:
    round_number: int
    points: float
    balance: float


class MainController:
    def __init__(
        self,
        username: str,
        fixture_service: FixtureService | None = None,
        favorites_service: FavoritesService | None = None,
        match_details_service: MatchDetailsService | None = None,
        auth_controller: AuthController | None = None,
    ) -> None:
        self.username = username
        self.fixture_service = fixture_service or FixtureService()
        self.favorites_service = favorites_service or FavoritesService()
        self.match_details_service = match_details_service or MatchDetailsService(self.fixture_service)
        self.auth_controller = auth_controller or AuthController()
        self.balance = 100.0
        self.total_points = 0.0
        self.market_open = True
        self.formation = "4-3-3"
        self.lineup_locked = False
        self._owned_player_ids: set[str] = set()
        self._lineup_player_ids: list[str] = []
        self._captain_id = ""
        self._history: list[HistoryViewRow] = []
        self._players = self._build_player_catalog()
        self._stats = {player.player_id: self._build_stat_row(player, index) for index, player in enumerate(self._players)}

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

    def favorite_athletes(self) -> set[str]:
        return self.favorites_service.get_favorites_by_type(self.username, "atleta")

    def save_favorite_athletes(self, athlete_ids: set[str]) -> set[str]:
        self.favorites_service.save_favorites_by_type(self.username, "atleta", athlete_ids)
        return self.favorite_athletes()

    def add_favorite_athlete(self, athlete_id: str) -> set[str]:
        return self.favorites_service.add_favorite(self.username, "atleta", athlete_id)

    def remove_favorite_athlete(self, athlete_id: str) -> set[str]:
        return self.favorites_service.remove_favorite(self.username, "atleta", athlete_id)

    def profile(self) -> dict[str, str]:
        try:
            return self.auth_controller.perfil(self.username)
        except ValueError:
            return {"username": self.username, "nome": self.username, "email": ""}

    def update_profile(self, nome: str, email: str, username: str) -> dict[str, str]:
        old_username = self.username
        user = self.auth_controller.atualizar_perfil(
            self.username,
            nome=nome,
            email=email,
            novo_username=username,
        )
        self.username = user.username
        self.favorites_service.rename_user(old_username, user.username)
        return self.profile()

    def market_summary(self) -> str:
        state = "aberto" if self.market_open else "fechado"
        return f"Mercado {state}. Saldo: {self.balance:.2f} moedas."

    def set_market_open(self, open_: bool) -> str:
        self.market_open = open_
        return self.market_summary()

    def market_players(self) -> list[PlayerViewRow]:
        return [
            self._player_row(player)
            for player in sorted(self._players, key=lambda item: (item.team, item.position, item.name))
        ]

    def owned_players(self) -> list[PlayerViewRow]:
        return [
            self._player_row(player)
            for player in self._players
            if player.player_id in self._owned_player_ids
        ]

    def buy_player(self, player_id: str) -> str:
        if not self.market_open:
            raise ValueError("Mercado fechado para transacoes.")
        player = self._player(player_id)
        if player_id in self._owned_player_ids:
            raise ValueError("Jogador ja pertence ao elenco.")
        if self.balance < player.value:
            raise ValueError("Saldo insuficiente.")
        self.balance -= player.value
        self._owned_player_ids.add(player_id)
        return self.market_summary()

    def sell_player(self, player_id: str) -> str:
        if not self.market_open:
            raise ValueError("Mercado fechado para transacoes.")
        player = self._player(player_id)
        if player_id not in self._owned_player_ids:
            raise ValueError("Jogador nao pertence ao elenco.")
        self._owned_player_ids.remove(player_id)
        if player_id in self._lineup_player_ids:
            self._lineup_player_ids.remove(player_id)
        if self._captain_id == player_id:
            self._captain_id = ""
        self.balance += player.value
        return self.market_summary()

    def set_formation(self, formation: str) -> None:
        if self.lineup_locked:
            raise ValueError("Escalacao bloqueada.")
        self.formation = formation

    def lineup_required_count(self) -> int:
        return sum(int(part) for part in self.formation.split("-")) + 1

    def lineup_summary(self) -> str:
        locked = "bloqueada" if self.lineup_locked else "aberta"
        return (
            f"Escalacao {locked}: {len(self._lineup_player_ids)}/"
            f"{self.lineup_required_count()} atletas. Capitao: {self._captain_name()}."
        )

    def lineup_players(self) -> list[PlayerViewRow]:
        return [self._player_row(self._player(player_id)) for player_id in self._lineup_player_ids]

    def add_lineup_player(self, player_id: str) -> str:
        if self.lineup_locked:
            raise ValueError("Escalacao bloqueada.")
        if player_id not in self._owned_player_ids:
            raise ValueError("Compre o jogador antes de escalar.")
        if player_id in self._lineup_player_ids:
            raise ValueError("Jogador ja esta escalado.")
        if len(self._lineup_player_ids) >= self.lineup_required_count():
            raise ValueError("Escalacao ja atingiu o tamanho da formacao.")
        self._lineup_player_ids.append(player_id)
        return self.lineup_summary()

    def remove_lineup_player(self, player_id: str) -> str:
        if self.lineup_locked:
            raise ValueError("Escalacao bloqueada.")
        if player_id in self._lineup_player_ids:
            self._lineup_player_ids.remove(player_id)
        if self._captain_id == player_id:
            self._captain_id = ""
        return self.lineup_summary()

    def choose_captain(self, player_id: str) -> str:
        if self.lineup_locked:
            raise ValueError("Escalacao bloqueada.")
        if player_id not in self._lineup_player_ids:
            raise ValueError("Jogador nao esta escalado.")
        self._captain_id = player_id
        return self.lineup_summary()

    def lock_lineup(self) -> str:
        if not self._captain_id:
            raise ValueError("Escolha um capitao.")
        if len(self._lineup_player_ids) != self.lineup_required_count():
            raise ValueError("Escalacao incompleta para a formacao.")
        self.lineup_locked = True
        return self.lineup_summary()

    def calculate_round_points(self) -> str:
        if not self.lineup_locked:
            self.lock_lineup()
        round_number = len(self._history) + 1
        if any(item.round_number == round_number for item in self._history):
            raise ValueError("Rodada ja calculada.")
        points = 0.0
        for player_id in self._lineup_player_ids:
            stat = self._stats[player_id]
            player_points = self._stat_points(stat)
            if player_id == self._captain_id:
                player_points *= 2
            points += player_points
        self.total_points += points
        self._history.append(HistoryViewRow(round_number, points, self.balance))
        self.lineup_locked = False
        self._lineup_player_ids = []
        self._captain_id = ""
        return f"Rodada {round_number}: {points:.1f} pontos. Total: {self.total_points:.1f}."

    def stat_rows(self, criterion: str = "", minimum: str = "") -> list[StatViewRow]:
        rows = list(self._stats.values())
        criterion_key = self._stat_key(criterion)
        if criterion_key:
            try:
                minimum_value = float(minimum) if minimum.strip() else None
            except ValueError:
                minimum_value = None
            if minimum_value is not None:
                rows = [row for row in rows if float(getattr(row, criterion_key)) >= minimum_value]
            rows.sort(key=lambda row: float(getattr(row, criterion_key)), reverse=True)
        return rows

    def compare_players(self, first_id: str, second_id: str) -> str:
        first = self._stats[first_id]
        second = self._stats[second_id]
        metrics = [
            ("gols", first.goals, second.goals),
            ("assistencias", first.assists, second.assists),
            ("desarmes", first.tackles, second.tackles),
            ("passes", first.passes, second.passes),
            ("precisao", first.pass_accuracy, second.pass_accuracy),
        ]
        parts = [f"{first.player_name} x {second.player_name}"]
        parts.extend(f"{name}: {left} x {right}" for name, left, right in metrics)
        return " | ".join(parts)

    def ranking_rows(self) -> list[RankingViewRow]:
        rows = [
            RankingViewRow(0, self.username, self.total_points, self.balance),
            RankingViewRow(0, "demo_lider", 84.0, 67.0),
            RankingViewRow(0, "demo_saldo", self.total_points, self.balance + 12.0),
        ]
        rows.sort(key=lambda row: (row.points, row.balance), reverse=True)
        return [
            RankingViewRow(index, row.username, row.points, row.balance)
            for index, row in enumerate(rows, start=1)
        ]

    def history_rows(self) -> list[HistoryViewRow]:
        return list(self._history)

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

    def _build_player_catalog(self) -> list[PlayerViewRow]:
        teams = self.fixture_service.teams() or ["Sofa FC", "Mesa FC", "Campo FC"]
        positions = ["GOL", "LAT", "ZAG", "MEI", "ATA"]
        players = []
        for team_index, team in enumerate(teams):
            for position_index, position in enumerate(positions):
                value = 6.0 + ((team_index + position_index) % 7) * 1.5
                player_id = f"{team_index + 1}-{position.lower()}"
                players.append(
                    PlayerViewRow(
                        player_id=player_id,
                        name=f"{team} {position}",
                        team=team,
                        position=position,
                        value=value,
                    )
                )
        return players

    def _build_stat_row(self, player: PlayerViewRow, index: int) -> StatViewRow:
        return StatViewRow(
            player_id=player.player_id,
            player_name=player.name,
            team=player.team,
            position=player.position,
            goals=index % 4,
            assists=(index + 1) % 3,
            tackles=2 + (index % 6),
            shots=1 + (index % 5),
            passes=18 + (index * 7) % 64,
            pass_accuracy=68.0 + (index % 25),
            yellow_cards=index % 2,
            red_cards=1 if index % 23 == 0 else 0,
        )

    def _player_row(self, player: PlayerViewRow) -> PlayerViewRow:
        points = self._stat_points(self._stats[player.player_id])
        if player.player_id == self._captain_id:
            points *= 2
        return PlayerViewRow(
            player_id=player.player_id,
            name=player.name,
            team=player.team,
            position=player.position,
            value=player.value,
            owned=player.player_id in self._owned_player_ids,
            favorite=player.player_id in self.favorite_athletes(),
            captain=player.player_id == self._captain_id,
            points=points,
        )

    def _player(self, player_id: str) -> PlayerViewRow:
        for player in self._players:
            if player.player_id == player_id:
                return player
        raise ValueError("Jogador nao encontrado.")

    def _captain_name(self) -> str:
        if not self._captain_id:
            return "nenhum"
        return self._player(self._captain_id).name

    def _stat_key(self, criterion: str) -> str:
        aliases = {
            "": "",
            "Gols": "goals",
            "Assistencias": "assists",
            "Desarmes": "tackles",
            "Finalizacoes": "shots",
            "Passes": "passes",
            "Precisao": "pass_accuracy",
        }
        return aliases.get(criterion, "")

    def _stat_points(self, stat: StatViewRow) -> float:
        return (
            stat.goals * 8
            + stat.assists * 5
            + stat.tackles * 1.5
            + stat.shots * 0.8
            - stat.yellow_cards
            - stat.red_cards * 3
        )
