import csv
import tempfile
import unittest
from pathlib import Path

from sofafut.controllers.main_controller import MainController
from sofafut.services.favorites_service import FavoritesService
from sofafut.services.fixture_service import FixtureService


class MainControllerTest(unittest.TestCase):
    def test_controller_prepara_dados_para_view(self) -> None:
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
                        "date": "2022-04-09T16:30:00-03:00",
                        "home_team_name": "Sofa FC",
                        "away_team_name": "Mesa FC",
                        "goals_home": "2",
                        "goals_away": "1",
                        "venue_name": "Arena",
                        "status_short": "FT",
                    }
                )

            controller = MainController(
                "vini",
                fixture_service=FixtureService(csv_path),
                favorites_service=FavoritesService(Path(temp_dir) / "favorites.json"),
            )

            self.assertEqual(controller.default_season(), "2022")
            self.assertEqual(controller.default_round("2022"), "Regular Season - 1")
            self.assertEqual(controller.game_rows("2022", "Regular Season - 1")[0].score, "2 x 1")
            self.assertEqual(controller.date_options("2022")[0][1], "09/04/2022")

            view_data = controller.save_favorites({"Sofa FC"})

            self.assertIn("Sofa FC", view_data.subtitle)
            self.assertEqual(len(view_data.rows), 1)


if __name__ == "__main__":
    unittest.main()
