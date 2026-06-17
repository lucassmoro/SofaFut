#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path


MATCH_HEADERS = [
    "Data",
    "Horario",
    "Mandante",
    "Resultado",
    "Visitante",
    "Publico",
    "Local",
]

TEAM_NAME_ALIASES = {
    "Ath Paranaense": "Athletico Paranaense",
    "Atl Goianiense": "Atletico Goianiense",
    "Atlético Goianiense": "Atletico Goianiense",
    "Atlético Mineiro": "Atletico-MG",
    "Botafogo (RJ)": "Botafogo",
    "Criciúma": "Criciuma",
    "Cuiabá": "Cuiaba",
    "Fortaleza": "Fortaleza EC",
    "Grêmio": "Gremio",
    "RB Bragantino": "RB Bragantino",
    "Red Bull Bragantino": "RB Bragantino",
    "São Paulo": "Sao Paulo",
    "Vasco da Gama": "Vasco DA Gama",
    "Vitória": "Vitoria",
}

POSITION_GROUPS = {
    "GK": "G",
    "CB": "D",
    "LB": "D",
    "RB": "D",
    "WB": "D",
    "DM": "M",
    "CM": "M",
    "AM": "M",
    "LM": "M",
    "RM": "M",
    "FW": "F",
    "LW": "F",
    "RW": "F",
}


def canonical_team_name(name):
    name = str(name or "").strip()
    return TEAM_NAME_ALIASES.get(name, name)


def stable_id(*parts):
    raw = "|".join(str(part or "").casefold().strip() for part in parts)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def parse_int(value, default=0):
    value = str(value or "").strip()
    if not value:
        return default
    try:
        return int(float(value.replace(",", ".")))
    except ValueError:
        return default


def parse_float(value, default=0.0):
    value = str(value or "").strip()
    if not value:
        return default
    try:
        return float(value.replace(".", "").replace(",", "."))
    except ValueError:
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return default


def parse_age(value):
    value = str(value or "").strip()
    if not value:
        return 0
    return parse_int(value.split("-", 1)[0], default=0)


def parse_score(value):
    normalized = str(value or "").strip().replace("–", "-")
    parts = normalized.split("-")
    if len(parts) != 2:
        raise ValueError(f"Placar invalido: {value}")
    return parse_int(parts[0]), parse_int(parts[1])


def parse_time(value):
    match = re.search(r"\d{1,2}:\d{2}", str(value or ""))
    if not match:
        return "00:00"
    hour, minute = match.group(0).split(":", 1)
    return f"{int(hour):02d}:{minute}"


def normalize_position(value):
    first_position = str(value or "").split(",", 1)[0].strip().upper()
    return POSITION_GROUPS.get(first_position, "M")


def read_matches(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        return [
            row
            for row in csv.DictReader(file, fieldnames=MATCH_HEADERS)
            if any(str(value or "").strip() for value in row.values())
        ]


def read_player_stats(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def build_player_index(stats_rows):
    players = OrderedDict()
    stats_by_date_team = {}

    for row in stats_rows:
        player_name = row.get("Jogador", "").strip()
        team_name = canonical_team_name(row.get("Time", ""))
        if not player_name or not team_name:
            continue

        player_key = (player_name.casefold(), team_name.casefold())
        player_id = stable_id("player", player_name, team_name)
        team_id = stable_id("team", team_name)
        position = normalize_position(row.get("Pos."))

        if player_key not in players:
            players[player_key] = {
                "id": player_id,
                "name": player_name,
                "age": parse_age(row.get("Idade")),
                "team_id": team_id,
                "team_name": team_name,
                "position": position,
            }

        date_team_key = (row.get("Data", "").strip(), team_name.casefold())
        stats_by_date_team.setdefault(date_team_key, []).append(row)

    return players, stats_by_date_team


def build_catalog(players, league_id, season):
    return {
        "liga_id": league_id,
        "temporada": season,
        "fonte": "csv_cache_local",
        "response": [
            {
                "player": {
                    "id": player["id"],
                    "name": player["name"],
                    "age": player["age"],
                    "valor_mercado": 10.0,
                },
                "statistics": [
                    {
                        "team": {
                            "id": player["team_id"],
                            "name": player["team_name"],
                            "logo": "",
                        },
                        "games": {
                            "position": player["position"],
                        },
                    }
                ],
            }
            for player in players.values()
        ],
    }


def build_fixture(match_row, fixture_id, round_name, league_id, season):
    home_team = canonical_team_name(match_row["Mandante"])
    away_team = canonical_team_name(match_row["Visitante"])
    home_goals, away_goals = parse_score(match_row["Resultado"])
    date = match_row["Data"].strip()
    time = parse_time(match_row["Horario"])
    timestamp = int(datetime.fromisoformat(f"{date}T{time}:00").timestamp())

    return {
        "fixture": {
            "id": fixture_id,
            "referee": None,
            "timezone": "UTC",
            "date": f"{date}T{time}:00+00:00",
            "timestamp": timestamp,
            "periods": {
                "first": timestamp,
                "second": timestamp + 45 * 60,
            },
            "venue": {
                "id": stable_id("venue", match_row.get("Local")),
                "name": match_row.get("Local") or "",
                "city": "",
            },
            "status": {
                "long": "Match Finished",
                "short": "FT",
                "elapsed": 90,
                "extra": None,
            },
        },
        "league": {
            "id": league_id,
            "name": "Serie A",
            "country": "Brazil",
            "logo": "",
            "flag": "",
            "season": season,
            "round": round_name,
            "standings": True,
        },
        "teams": {
            "home": {
                "id": stable_id("team", home_team),
                "name": home_team,
                "logo": "",
                "winner": _winner(home_goals, away_goals),
            },
            "away": {
                "id": stable_id("team", away_team),
                "name": away_team,
                "logo": "",
                "winner": _winner(away_goals, home_goals),
            },
        },
        "goals": {
            "home": home_goals,
            "away": away_goals,
        },
        "score": {
            "halftime": {
                "home": None,
                "away": None,
            },
            "fulltime": {
                "home": home_goals,
                "away": away_goals,
            },
            "extratime": {
                "home": None,
                "away": None,
            },
            "penalty": {
                "home": None,
                "away": None,
            },
        },
    }


def _winner(team_goals, opponent_goals):
    if team_goals == opponent_goals:
        return None
    return team_goals > opponent_goals


def build_team_statistics(team_name, rows, goals_conceded):
    team_name = canonical_team_name(team_name)
    return {
        "team": {
            "id": stable_id("team", team_name),
            "name": team_name,
            "logo": "",
        },
        "players": [
            {
                "player": {
                    "id": stable_id("player", row.get("Jogador"), team_name),
                    "name": row.get("Jogador"),
                },
                "statistics": [
                    {
                        "games": {
                            "minutes": parse_int(row.get("Min.")),
                            "number": parse_int(row.get("#")),
                            "position": normalize_position(row.get("Pos.")),
                            "rating": None,
                            "captain": False,
                            "substitute": parse_int(row.get("Min.")) < 45,
                        },
                        "goals": {
                            "total": parse_int(row.get("Gols")),
                            "conceded": goals_conceded,
                            "assists": parse_int(row.get("Assis.")),
                            "saves": 0,
                        },
                        "cards": {
                            "yellow": parse_int(row.get("CrtsA")),
                            "red": parse_int(row.get("CrtV")),
                        },
                        "fouls": {
                            "committed": 0,
                        },
                    }
                ],
            }
            for row in rows
            if row.get("Jogador")
        ],
    }


def build_round_caches(matches, stats_by_date_team, league_id=71, season=2024, round_size=10):
    warnings = []
    total_rounds = int(math.ceil(len(matches) / round_size))
    rounds = []

    for round_index in range(total_rounds):
        round_number = round_index + 1
        round_name = f"Regular Season - {round_number}"
        round_matches = matches[round_index * round_size : (round_index + 1) * round_size]
        fixtures = []
        cached_matches = []

        for index, match_row in enumerate(round_matches, start=1):
            fixture_id = season * 10000 + round_index * round_size + index
            fixture = build_fixture(match_row, fixture_id, round_name, league_id, season)
            fixtures.append(fixture)

            home_team = fixture["teams"]["home"]["name"]
            away_team = fixture["teams"]["away"]["name"]
            home_goals = fixture["goals"]["home"]
            away_goals = fixture["goals"]["away"]
            date = match_row["Data"].strip()
            home_rows = stats_by_date_team.get((date, home_team.casefold()), [])
            away_rows = stats_by_date_team.get((date, away_team.casefold()), [])

            if not home_rows:
                warnings.append(f"Sem estatisticas para {date} {home_team}")
            if not away_rows:
                warnings.append(f"Sem estatisticas para {date} {away_team}")

            teams_stats = []
            if home_rows:
                teams_stats.append(build_team_statistics(home_team, home_rows, away_goals))
            if away_rows:
                teams_stats.append(build_team_statistics(away_team, away_rows, home_goals))

            cached_matches.append(
                {
                    "fixture_id": fixture_id,
                    "partida": {"response": [fixture]},
                    "estatisticas_jogadores": {
                        "get": "fixtures/players",
                        "parameters": {"fixture": str(fixture_id)},
                        "errors": [],
                        "results": len(teams_stats),
                        "paging": {"current": 1, "total": 1},
                        "response": teams_stats,
                    },
                }
            )

        rounds.append(
            (
                round_number,
                {
                    "liga_id": league_id,
                    "temporada": season,
                    "rodada": round_name,
                    "partidas_api": {
                        "get": "fixtures",
                        "parameters": {
                            "league": str(league_id),
                            "season": str(season),
                            "round": round_name,
                            "status": "FT",
                        },
                        "errors": [],
                        "results": len(fixtures),
                        "paging": {"current": 1, "total": 1},
                        "response": fixtures,
                    },
                    "partidas": cached_matches,
                },
            )
        )

    return rounds, warnings


def backup_output_dir(output_dir):
    output_dir = Path(output_dir)
    if not output_dir.exists() or not any(output_dir.iterdir()):
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = output_dir.parent / f"{output_dir.name}_backup_{timestamp}"
    shutil.copytree(output_dir, backup_dir)
    return backup_dir


def write_cache(matches_csv, player_stats_csv, output_dir, league_id=71, season=2024, backup=True):
    matches = read_matches(matches_csv)
    stats_rows = read_player_stats(player_stats_csv)
    players, stats_by_date_team = build_player_index(stats_rows)
    catalog = build_catalog(players, league_id=league_id, season=season)
    round_caches, warnings = build_round_caches(
        matches,
        stats_by_date_team,
        league_id=league_id,
        season=season,
    )

    output_dir = Path(output_dir)
    backup_dir = backup_output_dir(output_dir) if backup else None
    output_dir.mkdir(parents=True, exist_ok=True)

    with (output_dir / "players_available.json").open("w", encoding="utf-8") as file:
        json.dump(catalog, file, ensure_ascii=False, indent=2)

    for round_number, round_cache in round_caches:
        path = output_dir / f"brasileirao_round_{round_number}.json"
        with path.open("w", encoding="utf-8") as file:
            json.dump(round_cache, file, ensure_ascii=False, indent=2)

    return {
        "matches": len(matches),
        "players": len(players),
        "rounds": len(round_caches),
        "warnings": warnings,
        "backup_dir": backup_dir,
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Gera caches locais da API-Football a partir dos CSVs do Brasileirao 2024."
    )
    parser.add_argument(
        "--matches-csv",
        default=r"archive (5)\Brasileiro 2024 (Srie A) - Dataset - Final.csv",
        help="CSV de jogos, sem cabecalho, com data/horario/mandante/placar/visitante/publico/local.",
    )
    parser.add_argument(
        "--player-stats-csv",
        default=r"archive (7)\database.csv",
        help="CSV de estatisticas por jogador.",
    )
    parser.add_argument(
        "--output-dir",
        default=r"data\api_football",
        help="Diretorio onde os caches JSON serao gravados.",
    )
    parser.add_argument("--league-id", type=int, default=71)
    parser.add_argument("--season", type=int, default=2024)
    parser.add_argument("--no-backup", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    result = write_cache(
        matches_csv=args.matches_csv,
        player_stats_csv=args.player_stats_csv,
        output_dir=args.output_dir,
        league_id=args.league_id,
        season=args.season,
        backup=not args.no_backup,
    )

    if result["backup_dir"]:
        print(f"Backup criado em: {result['backup_dir']}")
    print(
        "Caches gerados: "
        f"{result['rounds']} rodadas, {result['matches']} jogos, "
        f"{result['players']} jogadores."
    )
    for warning in result["warnings"]:
        print(f"Aviso: {warning}")


if __name__ == "__main__":
    main()
