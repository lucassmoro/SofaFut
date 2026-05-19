import argparse
import csv
from pathlib import Path
from typing import Any

from sofafut.infrastructure.api_football_client import ApiFootballClient


BRASILEIRAO_SERIE_A_LEAGUE_ID = 71
DEFAULT_SEASONS = (2022, 2023, 2024)


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa partidas do Brasileirao Serie A para CSV.")
    parser.add_argument(
        "--seasons",
        default=",".join(str(season) for season in DEFAULT_SEASONS),
        help="Temporadas separadas por virgula. Exemplo: 2022,2023,2024",
    )
    parser.add_argument("--output", default=None, help="Caminho do CSV de saida.")
    args = parser.parse_args()

    seasons = parse_seasons(args.seasons)
    output_path = Path(args.output or build_default_output_path(seasons))

    rows, requests_used, requests_remaining = fetch_fixtures_by_season(seasons)
    write_csv(output_path, rows)

    print(f"CSV salvo em {output_path} com {len(rows)} partidas.")
    print(f"Temporadas consultadas: {', '.join(str(season) for season in seasons)}.")
    print(f"Requisicoes usadas hoje: {requests_used}. Restantes pelo contador local: {requests_remaining}.")


def parse_seasons(raw_value: str) -> list[int]:
    seasons = []
    for value in raw_value.split(","):
        value = value.strip()
        if value:
            seasons.append(int(value))
    if not seasons:
        raise ValueError("Informe ao menos uma temporada.")
    return seasons


def build_default_output_path(seasons: list[int]) -> str:
    if len(seasons) == 1:
        return f"data/brasileirao_{seasons[0]}_partidas.csv"
    return f"data/brasileirao_{min(seasons)}_{max(seasons)}_partidas.csv"


def fetch_fixtures_by_season(seasons: list[int]) -> tuple[list[dict[str, Any]], int, int]:
    client = ApiFootballClient()
    rows: list[dict[str, Any]] = []
    requests_used = 0
    requests_remaining = 0

    for season in seasons:
        result = client.get(
            "fixtures",
            {
                "league": BRASILEIRAO_SERIE_A_LEAGUE_ID,
                "season": season,
                "timezone": "America/Sao_Paulo",
            },
        )
        rows.extend(fixture_to_row(item) for item in result.response)
        requests_used = result.requests_used_today
        requests_remaining = result.requests_remaining_today

    rows.sort(key=lambda row: (row["season"] or 0, row["date"] or "", row["fixture_id"] or 0))
    return rows, requests_used, requests_remaining


def fixture_to_row(item: dict[str, Any]) -> dict[str, Any]:
    fixture = item.get("fixture", {})
    league = item.get("league", {})
    teams = item.get("teams", {})
    goals = item.get("goals", {})
    score = item.get("score", {})
    home = teams.get("home", {})
    away = teams.get("away", {})
    status = fixture.get("status", {})

    return {
        "fixture_id": fixture.get("id"),
        "league_id": league.get("id"),
        "league_name": league.get("name"),
        "season": league.get("season"),
        "round": league.get("round"),
        "date": fixture.get("date"),
        "timestamp": fixture.get("timestamp"),
        "timezone": fixture.get("timezone"),
        "status_long": status.get("long"),
        "status_short": status.get("short"),
        "elapsed": status.get("elapsed"),
        "home_team_id": home.get("id"),
        "home_team_name": home.get("name"),
        "home_winner": home.get("winner"),
        "away_team_id": away.get("id"),
        "away_team_name": away.get("name"),
        "away_winner": away.get("winner"),
        "goals_home": goals.get("home"),
        "goals_away": goals.get("away"),
        "halftime_home": score.get("halftime", {}).get("home"),
        "halftime_away": score.get("halftime", {}).get("away"),
        "fulltime_home": score.get("fulltime", {}).get("home"),
        "fulltime_away": score.get("fulltime", {}).get("away"),
        "venue_id": fixture.get("venue", {}).get("id"),
        "venue_name": fixture.get("venue", {}).get("name"),
        "venue_city": fixture.get("venue", {}).get("city"),
        "referee": fixture.get("referee"),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(fixture_to_row({}).keys())
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
