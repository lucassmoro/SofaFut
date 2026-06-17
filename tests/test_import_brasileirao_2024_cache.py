import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.import_brasileirao_2024_cache import (
    MATCH_HEADERS,
    build_round_caches,
    build_player_index,
    read_matches,
    read_player_stats,
    write_cache,
)


class ImportBrasileiraoCacheTest(unittest.TestCase):
    def write_matches_csv(self, directory, rows):
        path = Path(directory) / "matches.csv"
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=MATCH_HEADERS)
            for row in rows:
                writer.writerow(row)
        return path

    def write_stats_csv(self, directory, rows):
        path = Path(directory) / "stats.csv"
        fieldnames = [
            "Jogador",
            "Time",
            "#",
            "Nação",
            "Pos.",
            "Idade",
            "Min.",
            "Gols",
            "Assis.",
            "PB",
            "PT",
            "TC",
            "CaG",
            "CrtsA",
            "CrtV",
            "Contatos",
            "Div",
            "Crts",
            "Bloqueios",
            "xG",
            "npxG",
            "xAG",
            "SCA",
            "GCA",
            "Cmp",
            "Att",
            "Cmp%",
            "PrgP",
            "Conduções",
            "PrgC",
            "Tent",
            "Suc",
            "Data",
        ]
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def player_row(
        self,
        jogador,
        time,
        posicao,
        data="2024-04-13",
        minutos="90.0",
        gols="0",
        assistencias="0",
    ):
        return {
            "Jogador": jogador,
            "Time": time,
            "#": "1",
            "Nação": "BRA",
            "Pos.": posicao,
            "Idade": "25-100",
            "Min.": minutos,
            "Gols": gols,
            "Assis.": assistencias,
            "PB": "0",
            "PT": "0",
            "TC": "0",
            "CaG": "0",
            "CrtsA": "1",
            "CrtV": "0",
            "Contatos": "0",
            "Div": "0",
            "Crts": "0",
            "Bloqueios": "0",
            "xG": "0",
            "npxG": "0",
            "xAG": "0",
            "SCA": "0",
            "GCA": "0",
            "Cmp": "0",
            "Att": "0",
            "Cmp%": "0",
            "PrgP": "0",
            "Conduções": "0",
            "PrgC": "0",
            "Tent": "0",
            "Suc": "0",
            "Data": data,
        }

    def test_build_round_cache_maps_matches_and_player_stats(self):
        with tempfile.TemporaryDirectory() as directory:
            matches_path = self.write_matches_csv(
                directory,
                [
                    {
                        "Data": "2024-04-13",
                        "Horario": "18:30",
                        "Mandante": "Criciuma",
                        "Resultado": "2-1",
                        "Visitante": "Bahia",
                        "Publico": "1000",
                        "Local": "Estadio",
                    }
                ],
            )
            stats_path = self.write_stats_csv(
                directory,
                [
                    self.player_row("Atacante", "Criciuma", "FW", gols="2"),
                    self.player_row("Goleiro", "Bahia", "GK"),
                ],
            )

            players, stats_by_date_team = build_player_index(read_player_stats(stats_path))
            rounds, warnings = build_round_caches(
                read_matches(matches_path),
                stats_by_date_team,
            )

            self.assertEqual(len(players), 2)
            self.assertEqual(warnings, [])
            self.assertEqual(len(rounds), 1)
            round_cache = rounds[0][1]
            self.assertEqual(round_cache["partidas_api"]["results"], 1)
            fixture = round_cache["partidas_api"]["response"][0]
            self.assertEqual(fixture["goals"], {"home": 2, "away": 1})
            stats_response = round_cache["partidas"][0]["estatisticas_jogadores"]["response"]
            self.assertEqual(len(stats_response), 2)
            self.assertEqual(stats_response[0]["players"][0]["statistics"][0]["goals"]["total"], 2)
            self.assertEqual(stats_response[0]["players"][0]["statistics"][0]["goals"]["conceded"], 1)

    def test_write_cache_creates_catalog_round_and_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            matches_path = self.write_matches_csv(
                directory,
                [
                    {
                        "Data": "2024-04-13",
                        "Horario": "18:30",
                        "Mandante": "Atl Goianiense",
                        "Resultado": "1-0",
                        "Visitante": "Bahia",
                        "Publico": "1000",
                        "Local": "Estadio",
                    }
                ],
            )
            stats_path = self.write_stats_csv(
                directory,
                [
                    self.player_row("Meia", "Atletico Goianiense", "AM"),
                    self.player_row("Defensor", "Bahia", "CB"),
                ],
            )
            output_dir = Path(directory) / "api_football"
            output_dir.mkdir()
            (output_dir / "old.json").write_text("{}", encoding="utf-8")

            result = write_cache(matches_path, stats_path, output_dir)

            self.assertIsNotNone(result["backup_dir"])
            self.assertTrue((output_dir / "players_available.json").exists())
            self.assertTrue((output_dir / "brasileirao_round_1.json").exists())
            catalog = json.loads((output_dir / "players_available.json").read_text(encoding="utf-8"))
            self.assertEqual(len(catalog["response"]), 2)
            round_cache = json.loads(
                (output_dir / "brasileirao_round_1.json").read_text(encoding="utf-8")
            )
            home_name = round_cache["partidas_api"]["response"][0]["teams"]["home"]["name"]
            self.assertEqual(home_name, "Atletico Goianiense")

    def test_missing_team_stats_are_reported_as_warnings(self):
        with tempfile.TemporaryDirectory() as directory:
            matches_path = self.write_matches_csv(
                directory,
                [
                    {
                        "Data": "2024-04-13",
                        "Horario": "18:30",
                        "Mandante": "Criciuma",
                        "Resultado": "0-0",
                        "Visitante": "Bahia",
                        "Publico": "1000",
                        "Local": "Estadio",
                    }
                ],
            )
            stats_path = self.write_stats_csv(
                directory,
                [self.player_row("Atacante", "Criciuma", "FW")],
            )

            _, stats_by_date_team = build_player_index(read_player_stats(stats_path))
            _, warnings = build_round_caches(read_matches(matches_path), stats_by_date_team)

            self.assertEqual(warnings, ["Sem estatisticas para 2024-04-13 Bahia"])


if __name__ == "__main__":
    unittest.main()
