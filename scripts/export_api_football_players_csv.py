#!/usr/bin/env python3
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import API_FOOTBALL_KEY


BASE_URL = "https://v3.football.api-sports.io"

CSV_FIELDS = [
    "player_id",
    "name",
    "firstname",
    "lastname",
    "age",
    "birth_date",
    "birth_place",
    "birth_country",
    "nationality",
    "height",
    "weight",
    "injured",
    "photo",
    "team_id",
    "team_name",
    "team_logo",
    "league_id",
    "league_name",
    "league_country",
    "league_logo",
    "league_flag",
    "season",
    "games_appearences",
    "games_lineups",
    "games_minutes",
    "games_number",
    "games_position",
    "games_rating",
    "games_captain",
    "substitutes_in",
    "substitutes_out",
    "substitutes_bench",
    "shots_total",
    "shots_on",
    "goals_total",
    "goals_conceded",
    "goals_assists",
    "goals_saves",
    "passes_total",
    "passes_key",
    "passes_accuracy",
    "tackles_total",
    "tackles_blocks",
    "tackles_interceptions",
    "duels_total",
    "duels_won",
    "dribbles_attempts",
    "dribbles_success",
    "dribbles_past",
    "fouls_drawn",
    "fouls_committed",
    "cards_yellow",
    "cards_yellowred",
    "cards_red",
    "penalty_won",
    "penalty_committed",
    "penalty_scored",
    "penalty_missed",
    "penalty_saved",
]


def nested(data, *keys):
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def get_json(path, api_key, timeout, **params):
    clean_params = {key: value for key, value in params.items() if value is not None}
    url = f"{BASE_URL}{path}?{urlencode(clean_params)}"
    request = Request(
        url,
        headers={
            "x-apisports-key": api_key,
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise RuntimeError(f"Erro HTTP {exc.code} da API-Football: {body}") from exc


def row_for(player_item, stat):
    player = player_item.get("player", {})
    birth = player.get("birth", {})
    team = stat.get("team", {})
    league = stat.get("league", {})

    return {
        "player_id": player.get("id"),
        "name": player.get("name"),
        "firstname": player.get("firstname"),
        "lastname": player.get("lastname"),
        "age": player.get("age"),
        "birth_date": birth.get("date"),
        "birth_place": birth.get("place"),
        "birth_country": birth.get("country"),
        "nationality": player.get("nationality"),
        "height": player.get("height"),
        "weight": player.get("weight"),
        "injured": player.get("injured"),
        "photo": player.get("photo"),
        "team_id": team.get("id"),
        "team_name": team.get("name"),
        "team_logo": team.get("logo"),
        "league_id": league.get("id"),
        "league_name": league.get("name"),
        "league_country": league.get("country"),
        "league_logo": league.get("logo"),
        "league_flag": league.get("flag"),
        "season": league.get("season"),
        "games_appearences": nested(stat, "games", "appearences"),
        "games_lineups": nested(stat, "games", "lineups"),
        "games_minutes": nested(stat, "games", "minutes"),
        "games_number": nested(stat, "games", "number"),
        "games_position": nested(stat, "games", "position"),
        "games_rating": nested(stat, "games", "rating"),
        "games_captain": nested(stat, "games", "captain"),
        "substitutes_in": nested(stat, "substitutes", "in"),
        "substitutes_out": nested(stat, "substitutes", "out"),
        "substitutes_bench": nested(stat, "substitutes", "bench"),
        "shots_total": nested(stat, "shots", "total"),
        "shots_on": nested(stat, "shots", "on"),
        "goals_total": nested(stat, "goals", "total"),
        "goals_conceded": nested(stat, "goals", "conceded"),
        "goals_assists": nested(stat, "goals", "assists"),
        "goals_saves": nested(stat, "goals", "saves"),
        "passes_total": nested(stat, "passes", "total"),
        "passes_key": nested(stat, "passes", "key"),
        "passes_accuracy": nested(stat, "passes", "accuracy"),
        "tackles_total": nested(stat, "tackles", "total"),
        "tackles_blocks": nested(stat, "tackles", "blocks"),
        "tackles_interceptions": nested(stat, "tackles", "interceptions"),
        "duels_total": nested(stat, "duels", "total"),
        "duels_won": nested(stat, "duels", "won"),
        "dribbles_attempts": nested(stat, "dribbles", "attempts"),
        "dribbles_success": nested(stat, "dribbles", "success"),
        "dribbles_past": nested(stat, "dribbles", "past"),
        "fouls_drawn": nested(stat, "fouls", "drawn"),
        "fouls_committed": nested(stat, "fouls", "committed"),
        "cards_yellow": nested(stat, "cards", "yellow"),
        "cards_yellowred": nested(stat, "cards", "yellowred"),
        "cards_red": nested(stat, "cards", "red"),
        "penalty_won": nested(stat, "penalty", "won"),
        "penalty_committed": nested(stat, "penalty", "commited"),
        "penalty_scored": nested(stat, "penalty", "scored"),
        "penalty_missed": nested(stat, "penalty", "missed"),
        "penalty_saved": nested(stat, "penalty", "saved"),
    }


def export_players_csv(api_key, league, season, output, timeout, sleep_seconds, max_pages):
    rows = []
    page = 1
    total_pages = None

    while True:
        data = get_json(
            "/players",
            api_key=api_key,
            timeout=timeout,
            league=league,
            season=season,
            page=page,
        )
        errors = data.get("errors")
        if errors:
            raise RuntimeError(f"Erro da API-Football: {errors}")

        paging = data.get("paging", {})
        total_pages = total_pages or int(paging.get("total") or 1)
        response = data.get("response", [])

        for player_item in response:
            stats = player_item.get("statistics") or [{}]
            for stat in stats:
                rows.append(row_for(player_item, stat))

        print(f"Pagina {page}/{total_pages}: {len(response)} jogadores, {len(rows)} linhas")

        if page >= total_pages:
            break
        if max_pages is not None and page >= max_pages:
            break

        page += 1
        if sleep_seconds:
            time.sleep(sleep_seconds)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows), total_pages


def parse_args():
    parser = argparse.ArgumentParser(
        description="Exporta jogadores e estatisticas da API-Football para CSV."
    )
    parser.add_argument("--league", type=int, default=71, help="ID da liga. Padrao: 71 (Brasileirao).")
    parser.add_argument("--season", type=int, required=True, help="Temporada, ex: 2024.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Caminho do CSV de saida.",
    )
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--sleep", type=float, default=0.25, help="Pausa entre paginas.")
    parser.add_argument("--max-pages", type=int, default=None, help="Limite opcional para testes.")
    return parser.parse_args()


def main():
    args = parse_args()
    api_key = os.getenv("API_FOOTBALL_KEY") or API_FOOTBALL_KEY
    if not api_key:
        raise RuntimeError("Configure API_FOOTBALL_KEY ou src/config.py.")

    output = args.output or Path(
        f"data/api_football/players_stats_league_{args.league}_season_{args.season}.csv"
    )
    total_rows, total_pages = export_players_csv(
        api_key=api_key,
        league=args.league,
        season=args.season,
        output=output,
        timeout=args.timeout,
        sleep_seconds=args.sleep,
        max_pages=args.max_pages,
    )
    print(f"CSV gerado: {output}")
    print(f"Linhas exportadas: {total_rows}")
    print(f"Paginas disponiveis na API: {total_pages}")


if __name__ == "__main__":
    main()
