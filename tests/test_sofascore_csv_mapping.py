import unittest

from sofafut.infrastructure.sofascore_client import SofascoreSeason
from sofafut.scripts.fetch_brasileirao_sofascore import event_to_row, flatten_statistics


class SofascoreCsvMappingTest(unittest.TestCase):
    def test_event_to_row(self) -> None:
        row = event_to_row(
            {
                "id": 1,
                "startTimestamp": 1769637600,
                "roundInfo": {"round": 1},
                "status": {"code": 100, "description": "Ended", "type": "finished"},
                "homeTeam": {"id": 10, "name": "Sofa FC", "shortName": "Sofa"},
                "awayTeam": {"id": 20, "name": "Mesa FC", "shortName": "Mesa"},
                "homeScore": {"current": 2, "display": 2, "period1": 1, "period2": 1},
                "awayScore": {"current": 1, "display": 1, "period1": 0, "period2": 1},
                "tournament": {"id": 83},
                "slug": "sofa-fc-mesa-fc",
            },
            SofascoreSeason(id=87678, year="2026", name="Brasileiro Serie A 2026"),
            {"home_ballPossession": 52, "away_ballPossession": 48, "home_unknownMetric": 3},
        )

        self.assertEqual(row["event_id"], 1)
        self.assertEqual(row["season_id"], 87678)
        self.assertEqual(row["round"], 1)
        self.assertEqual(row["home_team_name"], "Sofa FC")
        self.assertEqual(row["away_score_current"], 1)
        self.assertIn("2026", row["date"])
        self.assertEqual(row["home_ballPossession"], 52)
        self.assertEqual(row["home_unknownMetric"], 3)

    def test_flatten_statistics(self) -> None:
        stats = flatten_statistics(
            {
                "statistics": [
                    {
                        "period": "ALL",
                        "groups": [
                            {
                                "statisticsItems": [
                                    {"key": "expectedGoals", "homeValue": 1.2, "awayValue": 0.8},
                                    {"key": "duelWon", "name": "Duels won", "home": "42", "away": "39"},
                                ]
                            }
                        ],
                    }
                ]
            }
        )

        self.assertEqual(stats["home_expectedGoals"], 1.2)
        self.assertEqual(stats["label_duelWon"], "Duels won")
        self.assertEqual(stats["home_duelWon"], "42")


if __name__ == "__main__":
    unittest.main()
