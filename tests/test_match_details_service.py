import csv
import tempfile
import unittest
from pathlib import Path

from sofafut.services.fixture_service import FixtureService
from sofafut.services.match_details_service import MatchDetailsService


class FakeSofascoreClient:
    def event_lineups(self, event_id: int) -> dict:
        return {
            "home": {
                "players": [
                    {
                        "player": {"name": "Jogador Casa"},
                        "shirtNumber": 10,
                        "position": "M",
                        "substitute": False,
                        "statistics": {"rating": 7.1},
                    }
                ]
            },
            "away": {
                "players": [
                    {
                        "player": {"name": "Jogador Fora"},
                        "shirtNumber": 9,
                        "position": "F",
                        "substitute": True,
                        "statistics": {"rating": 6.5},
                    }
                ]
            },
        }


class MatchDetailsServiceTest(unittest.TestCase):
    def test_details_monta_escalacao_e_estatisticas(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "sofascore.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as file:
                fieldnames = [
                    "event_id",
                    "season_year",
                    "round",
                    "date",
                    "home_team_name",
                    "away_team_name",
                    "home_score_current",
                    "away_score_current",
                    "status_description",
                    "home_ballPossession",
                    "away_ballPossession",
                    "home_totalShotsOnGoal",
                    "away_totalShotsOnGoal",
                    "home_goalkeeperSaves",
                    "away_goalkeeperSaves",
                    "label_duelWon",
                    "home_duelWon",
                    "away_duelWon",
                ]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(
                    {
                        "event_id": "1",
                        "season_year": "2026",
                        "round": "1",
                        "date": "2026-01-01T10:00:00-03:00",
                        "home_team_name": "Sofa FC",
                        "away_team_name": "Mesa FC",
                        "home_score_current": "2",
                        "away_score_current": "1",
                        "status_description": "Ended",
                        "home_ballPossession": "60",
                        "away_ballPossession": "40",
                        "home_totalShotsOnGoal": "12",
                        "away_totalShotsOnGoal": "8",
                        "home_goalkeeperSaves": "3",
                        "away_goalkeeperSaves": "5",
                        "label_duelWon": "Duelos vencidos",
                        "home_duelWon": "48",
                        "away_duelWon": "45",
                    }
                )

            service = MatchDetailsService(FixtureService(csv_path), FakeSofascoreClient())
            details = service.details("1")

            self.assertEqual(details.title, "Sofa FC x Mesa FC")
            self.assertEqual(details.home_lineup.players[0].name, "Jogador Casa")
            self.assertEqual(details.away_lineup.players[0].role, "Reserva")
            self.assertEqual(
                [stat.name for stat in details.stats],
                [
                    "Ataque",
                    "Finalizacoes totais",
                    "Passes",
                    "Posse de bola",
                    "Defesa",
                    "Defesas do goleiro",
                    "Outras",
                    "Duelos vencidos",
                ],
            )


if __name__ == "__main__":
    unittest.main()
