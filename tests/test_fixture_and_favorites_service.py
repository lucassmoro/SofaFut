import csv
import tempfile
import unittest
from pathlib import Path

from sofafut.services.favorites_service import FavoritesService
from sofafut.services.fixture_service import FixtureService


class FixtureAndFavoritesServiceTest(unittest.TestCase):
    def test_fixtures_por_temporada_rodada_e_favoritos(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "fixtures.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "fixture_id",
                        "season",
                        "round",
                        "date",
                        "home_team_name",
                        "away_team_name",
                        "goals_home",
                        "goals_away",
                        "venue_name",
                        "status_short",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "fixture_id": "1",
                        "season": "2022",
                        "round": "Regular Season - 1",
                        "date": "2022-01-01T10:00:00-03:00",
                        "home_team_name": "Sofa FC",
                        "away_team_name": "Mesa FC",
                        "goals_home": "2",
                        "goals_away": "1",
                        "venue_name": "Arena",
                        "status_short": "FT",
                    }
                )

            service = FixtureService(csv_path)

            self.assertEqual(service.seasons(), [2022])
            self.assertEqual(service.rounds(2022), ["Regular Season - 1"])
            self.assertEqual(len(service.fixtures(2022, "Regular Season - 1")), 1)
            self.assertEqual(len(service.favorite_fixtures({"Sofa FC"})), 1)

    def test_favorites_por_usuario(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = FavoritesService(Path(temp_dir) / "favorites.json")
            service.save_favorites("vini", {"Sofa FC", "Mesa FC"})

            self.assertEqual(service.get_favorites("vini"), {"Sofa FC", "Mesa FC"})


if __name__ == "__main__":
    unittest.main()
