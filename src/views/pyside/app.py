from PySide6.QtWidgets import QApplication

from src.views.pyside.uc01_uc02_autenticacao import LoginWindow


class SofaFutPySideGui:
    def __init__(
        self,
        auth_controller,
        player_catalog_controller,
        player_comparison_controller,
        favorite_controller,
        round_controller,
        lineup_controller,
        ranking_controller,
        market_controller,
    ):
        self.app = QApplication.instance() or QApplication([])
        self.window = LoginWindow(
            auth_controller=auth_controller,
            player_catalog_controller=player_catalog_controller,
            player_comparison_controller=player_comparison_controller,
            favorite_controller=favorite_controller,
            round_controller=round_controller,
            lineup_controller=lineup_controller,
            ranking_controller=ranking_controller,
            market_controller=market_controller,
        )

    def run(self):
        self.window.showMaximized()
        return self.app.exec()
