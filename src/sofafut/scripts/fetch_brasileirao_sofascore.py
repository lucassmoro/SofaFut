import argparse
import csv
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from sofafut.infrastructure.sofascore_client import SofascoreClient, SofascoreSeason


BRASILEIRAO_SERIE_A_UNIQUE_TOURNAMENT_ID = 325
DEFAULT_SEASON = "2026"
SAO_PAULO_TZ = ZoneInfo("America/Sao_Paulo")
BASE_FIELDNAMES = [
    "event_id",
    "season_id",
    "season_year",
    "season_name",
    "tournament_id",
    "unique_tournament_id",
    "round",
    "date",
    "timestamp",
    "status_code",
    "status_type",
    "status_description",
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
    "slug",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa partidas do Brasileirao atual via endpoints internos do Sofascore.")
    parser.add_argument("--season", default=DEFAULT_SEASON, help="Ano da temporada. Padrao: 2026.")
    parser.add_argument("--output", default=None, help="Caminho do CSV de saida.")
    parser.add_argument(
        "--played-only",
        action="store_true",
        help="Salva apenas jogos passados/finalizados ou em andamento retornados pelo endpoint last.",
    )
    parser.add_argument(
        "--no-statistics",
        action="store_true",
        help="Nao consulta estatisticas por partida.",
    )
    args = parser.parse_args()

    client = SofascoreClient()
    season = find_season(client, args.season)
    events = fetch_season_events(client, season.id, include_future=not args.played_only)
    rows = build_rows(client, events, season, include_statistics=not args.no_statistics)
    rows.sort(key=lambda row: (row["timestamp"] or 0, row["event_id"]))

    output_path = Path(args.output or f"data/sofascore_brasileirao_{season.year}_partidas.csv")
    write_csv(output_path, rows)

    print(f"CSV salvo em {output_path} com {len(rows)} partidas.")
    print(f"Temporada Sofascore: {season.name} (season_id={season.id}).")


def find_season(client: SofascoreClient, season_year: str) -> SofascoreSeason:
    seasons = client.seasons(BRASILEIRAO_SERIE_A_UNIQUE_TOURNAMENT_ID)
    for season in seasons:
        if season.year == season_year:
            return season
    available = ", ".join(f"{season.year}:{season.id}" for season in seasons[:10])
    raise RuntimeError(f"Temporada {season_year} nao encontrada no Sofascore. Disponiveis: {available}")


def fetch_season_events(client: SofascoreClient, season_id: int, include_future: bool) -> list[dict[str, Any]]:
    events_by_id: dict[int, dict[str, Any]] = {}
    for event in client.paged_events(BRASILEIRAO_SERIE_A_UNIQUE_TOURNAMENT_ID, season_id, "last"):
        events_by_id[int(event["id"])] = event
    if include_future:
        for event in client.paged_events(BRASILEIRAO_SERIE_A_UNIQUE_TOURNAMENT_ID, season_id, "next"):
            events_by_id[int(event["id"])] = event
    return list(events_by_id.values())


def build_rows(
    client: SofascoreClient,
    events: list[dict[str, Any]],
    season: SofascoreSeason,
    include_statistics: bool,
) -> list[dict[str, Any]]:
    rows = []
    for event in events:
        stats = {}
        if include_statistics and should_fetch_statistics(event):
            try:
                stats = flatten_statistics(client.event_statistics(int(event["id"])))
                time.sleep(0.15)
            except RuntimeError:
                stats = {}
        rows.append(event_to_row(event, season, stats))
    return rows


def should_fetch_statistics(event: dict[str, Any]) -> bool:
    status_type = event.get("status", {}).get("type")
    return status_type in {"finished", "inprogress"}


def flatten_statistics(payload: dict[str, Any]) -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for period in payload.get("statistics", []):
        if period.get("period") != "ALL":
            continue
        for group in period.get("groups", []):
            for item in group.get("statisticsItems", []):
                key = normalize_stat_key(item.get("key") or item.get("name"))
                if not key:
                    continue
                label = item.get("name")
                if label:
                    flattened[f"label_{key}"] = label
                flattened[f"home_{key}"] = statistic_value(item, "home")
                flattened[f"away_{key}"] = statistic_value(item, "away")
    return flattened


def normalize_stat_key(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return re.sub(r"[^A-Za-z0-9_]+", "_", text).strip("_")


def statistic_value(item: dict[str, Any], side: str) -> Any:
    for field in (side, f"{side}Value", f"{side}Total"):
        value = item.get(field)
        if value not in (None, ""):
            return value
    return ""


def event_to_row(event: dict[str, Any], season: SofascoreSeason, statistics: dict[str, Any] | None = None) -> dict[str, Any]:
    home_team = event.get("homeTeam", {})
    away_team = event.get("awayTeam", {})
    home_score = event.get("homeScore", {})
    away_score = event.get("awayScore", {})
    status = event.get("status", {})
    round_info = event.get("roundInfo", {})
    tournament = event.get("tournament", {})
    timestamp = event.get("startTimestamp")

    row = {
        "event_id": event.get("id"),
        "season_id": season.id,
        "season_year": season.year,
        "season_name": season.name,
        "tournament_id": tournament.get("id"),
        "unique_tournament_id": BRASILEIRAO_SERIE_A_UNIQUE_TOURNAMENT_ID,
        "round": round_info.get("round"),
        "date": timestamp_to_iso(timestamp),
        "timestamp": timestamp,
        "status_code": status.get("code"),
        "status_type": status.get("type"),
        "status_description": status.get("description"),
        "home_team_id": home_team.get("id"),
        "home_team_name": home_team.get("name"),
        "home_team_short_name": home_team.get("shortName"),
        "away_team_id": away_team.get("id"),
        "away_team_name": away_team.get("name"),
        "away_team_short_name": away_team.get("shortName"),
        "home_score_current": home_score.get("current"),
        "away_score_current": away_score.get("current"),
        "home_score_display": home_score.get("display"),
        "away_score_display": away_score.get("display"),
        "home_score_period1": home_score.get("period1"),
        "away_score_period1": away_score.get("period1"),
        "home_score_period2": home_score.get("period2"),
        "away_score_period2": away_score.get("period2"),
        "slug": event.get("slug"),
    }
    row.update(statistics or {})
    return row


def timestamp_to_iso(timestamp: int | None) -> str:
    if timestamp is None:
        return ""
    return datetime.fromtimestamp(int(timestamp), tz=SAO_PAULO_TZ).isoformat()


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = csv_fieldnames(rows)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def csv_fieldnames(rows: list[dict[str, Any]]) -> list[str]:
    dynamic_fields: list[str] = []
    seen = set(BASE_FIELDNAMES)
    for row in rows:
        for field in row:
            if field not in seen:
                dynamic_fields.append(field)
                seen.add(field)
    return [*BASE_FIELDNAMES, *dynamic_fields]


if __name__ == "__main__":
    main()
