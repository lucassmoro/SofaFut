from dataclasses import dataclass
import re

from sofafut.infrastructure.sofascore_client import SofascoreClient
from sofafut.services.fixture_service import FixtureService


@dataclass(frozen=True)
class PlayerLineupRow:
    number: str
    name: str
    position: str
    role: str
    rating: str


@dataclass(frozen=True)
class TeamLineup:
    team_name: str
    players: list[PlayerLineupRow]


@dataclass(frozen=True)
class MatchStatRow:
    name: str
    home: str
    away: str
    is_group: bool = False


@dataclass(frozen=True)
class MatchDetails:
    title: str
    home_lineup: TeamLineup
    away_lineup: TeamLineup
    stats: list[MatchStatRow]


STAT_LABELS = {
    "ballPossession": "Posse de bola",
    "expectedGoals": "Gols esperados",
    "bigChanceCreated": "Grandes chances",
    "totalShotsOnGoal": "Finalizacoes totais",
    "goalkeeperSaves": "Defesas do goleiro",
    "cornerKicks": "Escanteios",
    "fouls": "Faltas",
    "passes": "Passes",
    "totalTackle": "Desarmes",
    "freeKicks": "Faltas cobradas",
    "yellowCards": "Cartoes amarelos",
    "redCards": "Cartoes vermelhos",
    "shotsOnGoal": "Finalizacoes no gol",
    "shotsOffGoal": "Finalizacoes fora",
    "blockedScoringAttempt": "Finalizacoes bloqueadas",
    "hitWoodwork": "Bolas na trave",
    "offsides": "Impedimentos",
    "accuratePasses": "Passes certos",
    "throwIns": "Laterais",
    "finalThirdEntries": "Entradas no terco final",
}

STAT_GROUPS = {
    "Ataque": (
        "expectedGoals",
        "totalShotsOnGoal",
        "shotsOnGoal",
        "shotsOffGoal",
        "blockedScoringAttempt",
        "totalShotsInsideBox",
        "totalShotsOutsideBox",
        "bigChanceCreated",
        "bigChanceScored",
        "bigChanceMissed",
        "hitWoodwork",
        "touchesInOppBox",
        "cornerKicks",
        "offsides",
        "dribblesPercentage",
        "finalThirdEntries",
        "finalThirdPhaseStatistic",
        "fouledFinalThird",
        "accurateCross",
        "freeKicks",
    ),
    "Passes": (
        "ballPossession",
        "passes",
        "accuratePasses",
        "accurateLongBalls",
        "accurateThroughBall",
        "throwIns",
        "goalKicks",
    ),
    "Defesa": (
        "goalkeeperSaves",
        "diveSaves",
        "goalsPrevented",
        "penaltySaves",
        "punches",
        "highClaims",
        "totalTackle",
        "wonTacklePercent",
        "interceptionWon",
        "ballRecovery",
        "totalClearance",
        "aerialDuelsPercentage",
        "groundDuelsPercentage",
        "duelWonPercent",
        "errorsLeadToShot",
        "errorsLeadToGoal",
    ),
}
STAT_GROUP_ORDER = {group: index for index, group in enumerate((*STAT_GROUPS, "Outras"))}
STAT_KEY_ORDER = {
    key: index
    for keys in STAT_GROUPS.values()
    for index, key in enumerate(keys)
}


class MatchDetailsService:
    def __init__(
        self,
        fixture_service: FixtureService,
        sofascore_client: SofascoreClient | None = None,
    ) -> None:
        self.fixture_service = fixture_service
        self.sofascore_client = sofascore_client or SofascoreClient()

    def details(self, fixture_id: str) -> MatchDetails:
        fixture = self.fixture_service.fixture_by_id(fixture_id)
        if fixture is None:
            raise ValueError("Partida nao encontrada.")

        lineups_payload = self._safe_lineups(fixture_id)
        return MatchDetails(
            title=f"{fixture.home_team} x {fixture.away_team}",
            home_lineup=self._team_lineup(fixture.home_team, lineups_payload.get("home", {})),
            away_lineup=self._team_lineup(fixture.away_team, lineups_payload.get("away", {})),
            stats=self._stats_rows(fixture.stats),
        )

    def _safe_lineups(self, fixture_id: str) -> dict:
        try:
            return self.sofascore_client.event_lineups(int(fixture_id))
        except RuntimeError:
            return {}

    def _team_lineup(self, team_name: str, payload: dict) -> TeamLineup:
        rows = []
        players = payload.get("players", [])
        players = sorted(players, key=lambda item: (bool(item.get("substitute")), item.get("position", ""), item.get("shirtNumber") or 999))
        for item in players:
            player = item.get("player", {})
            statistics = item.get("statistics", {})
            rating = statistics.get("rating")
            rows.append(
                PlayerLineupRow(
                    number=str(item.get("shirtNumber") or item.get("jerseyNumber") or ""),
                    name=str(player.get("name") or ""),
                    position=str(item.get("position") or player.get("position") or ""),
                    role="Reserva" if item.get("substitute") else "Titular",
                    rating="" if rating is None else str(rating),
                )
            )
        return TeamLineup(team_name=team_name, players=rows)

    def _stats_rows(self, stats: dict[str, str]) -> list[MatchStatRow]:
        grouped_rows: dict[str, list[tuple[int, int, MatchStatRow]]] = {}
        stat_keys = [key.removeprefix("home_") for key in stats if key.startswith("home_")]
        for original_index, key in enumerate(stat_keys):
            label = STAT_LABELS.get(key) or stats.get(f"label_{key}") or humanize_stat_key(key)
            home = stats.get(f"home_{key}", "")
            away = stats.get(f"away_{key}", "")
            if home == "" and away == "":
                continue
            group = stat_group(key)
            order = STAT_KEY_ORDER.get(key, original_index)
            grouped_rows.setdefault(group, []).append(
                (order, original_index, MatchStatRow(name=label, home=str(home), away=str(away)))
            )

        rows = []
        for group in sorted(grouped_rows, key=lambda item: STAT_GROUP_ORDER[item]):
            rows.append(MatchStatRow(name=group, home="", away="", is_group=True))
            rows.extend(row for _order, _original_index, row in sorted(grouped_rows[group]))
        return rows


def stat_group(key: str) -> str:
    for group, keys in STAT_GROUPS.items():
        if key in keys:
            return group
    return "Outras"


def humanize_stat_key(key: str) -> str:
    spaced = re.sub(r"(?<!^)([A-Z])", r" \1", key)
    return spaced.replace("_", " ").strip().capitalize()
