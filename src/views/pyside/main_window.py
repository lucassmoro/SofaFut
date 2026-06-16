from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.views.pyside.shared import PySideViewContext
from src.views.pyside.style import STYLE
from src.views.pyside.uc03_acessar_estatisticas import PlayerStatsScreen
from src.views.pyside.uc04_filtrar_atletas import FilterPlayersScreen
from src.views.pyside.uc05_comparar_atletas import ComparePlayersScreen
from src.views.pyside.uc06_jogos_rodada import RoundMatchesScreen
from src.views.pyside.uc06_uc18_rodada import RoundScreen
from src.views.pyside.uc07_favoritos import FavoritesScreen
from src.views.pyside.uc08_negociar_atletas import MarketScreen
from src.views.pyside.uc09_uc10_escalacao_pontuacao import LineupScoreScreen
from src.views.pyside.uc11_ranking import RankingScreen
from src.views.pyside.uc12_historico_evolucao import EvolutionHistoryScreen
from src.views.pyside.uc13_gerenciar_perfil import ProfileScreen
from src.views.pyside.uc14_historico_patrimonio import AssetHistoryScreen


class MainWindow(QMainWindow):
    def __init__(
        self,
        username,
        auth_controller,
        player_catalog_controller,
        player_comparison_controller,
        favorite_controller,
        round_controller,
        lineup_controller,
        ranking_controller,
        market_controller,
        user_profile_controller,
    ):
        super().__init__()
        self.context = PySideViewContext(
            username=username,
            auth_controller=auth_controller,
            player_catalog_controller=player_catalog_controller,
            player_comparison_controller=player_comparison_controller,
            favorite_controller=favorite_controller,
            round_controller=round_controller,
            lineup_controller=lineup_controller,
            ranking_controller=ranking_controller,
            market_controller=market_controller,
            user_profile_controller=user_profile_controller,
        )

        self.tabs = None
        self.user_label = None
        self.login_window = None
        self.round_screen = None
        self.round_matches_screen = None
        self.stats_screen = None
        self.filter_screen = None
        self.market_screen = None
        self.lineup_screen = None
        self.compare_screen = None
        self.favorites_screen = None
        self.evolution_screen = None
        self.history_screen = None
        self.ranking_screen = None
        self.profile_screen = None

        self.setWindowTitle("SofaFut")
        self.setMinimumSize(1100, 720)
        self._build_ui()
        self.round_screen.carregar_catalogo()
        self.ranking_screen.atualizar()
        self.market_screen.atualizar()

    def _build_ui(self):
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(22, 18, 22, 18)

        header = QHBoxLayout()
        title = QLabel("SofaFut")
        title.setProperty("role", "title")
        header.addWidget(title)
        header.addStretch(1)
        self.user_label = QLabel(f"Usuario: {self.context.username}")
        header.addWidget(self.user_label)
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self._logout)
        header.addWidget(logout_button)
        layout.addLayout(header)

        self.tabs = QTabWidget()
        self._build_screens()
        self.tabs.addTab(self.round_screen.build(), "Rodada")
        self.tabs.addTab(self.round_matches_screen.build(), "Jogos")
        self.tabs.addTab(self.filter_screen.build(), "Atletas")
        self.tabs.addTab(self.stats_screen.build(), "Estatisticas")
        self.tabs.addTab(self.market_screen.build(), "Mercado")
        self.tabs.addTab(self.lineup_screen.build(), "Escalacao")
        self.tabs.addTab(self.compare_screen.build(), "Comparar")
        self.tabs.addTab(self.favorites_screen.build(), "Favoritos")
        self.tabs.addTab(self.evolution_screen.build(), "Evolucao")
        self.tabs.addTab(self.history_screen.build(), "Historico")
        self.tabs.addTab(self.ranking_screen.build(), "Ranking")
        self.tabs.addTab(self.profile_screen.build(), "Perfil")
        layout.addWidget(self.tabs, 1)

        self.setCentralWidget(root)
        self.setStyleSheet(STYLE)

    def _build_screens(self):
        self.stats_screen = PlayerStatsScreen(self.context, self._erro)
        self.round_matches_screen = RoundMatchesScreen(self.context, self._erro)
        self.filter_screen = FilterPlayersScreen(self.context, self._erro)
        self.compare_screen = ComparePlayersScreen(self.context, self._erro)
        self.favorites_screen = FavoritesScreen(self.context, self._erro)
        self.evolution_screen = EvolutionHistoryScreen(self.context)
        self.history_screen = AssetHistoryScreen(self.context)
        self.ranking_screen = RankingScreen(self.context)
        self.profile_screen = ProfileScreen(
            self.context,
            self._atualizar_username,
            self._erro,
        )
        self.lineup_screen = LineupScoreScreen(
            context=self.context,
            get_temporada=lambda: self.round_screen.temporada(),
            get_rodada=lambda: self.round_screen.rodada(),
            refresh_market=lambda: self.market_screen.atualizar(),
            refresh_ranking=lambda: self.ranking_screen.atualizar(),
            refresh_evolution=lambda: self.evolution_screen.atualizar(),
            show_error=self._erro,
        )
        self.market_screen = MarketScreen(
            context=self.context,
            show_lineup=lambda: self.tabs.setCurrentIndex(5),
            refresh_lineup=lambda status=None: self.lineup_screen.preencher(status),
            refresh_favorites=lambda: self.favorites_screen.preencher(),
            refresh_history=lambda: self.history_screen.preencher(),
            refresh_evolution=lambda: self.evolution_screen.atualizar(),
            show_error=self._erro,
        )
        self.round_screen = RoundScreen(
            context=self.context,
            show_market=lambda: self.tabs.setCurrentIndex(4),
            on_catalog_loaded=self._catalogo_carregado,
            on_players_loaded=lambda: self.market_screen.preencher_catalogo(),
            on_round_reset=lambda: self.market_screen.reiniciar_elenco_rodada(),
            show_error=self._erro,
        )

    def _catalogo_carregado(self):
        self.compare_screen.preencher_combos()
        self.stats_screen.atualizar_atletas()
        self.filter_screen.atualizar_opcoes()

    def _logout(self):
        self.context.auth_controller.logout()

        from src.views.pyside.uc01_uc02_autenticacao import LoginWindow

        self.login_window = LoginWindow(
            auth_controller=self.context.auth_controller,
            player_catalog_controller=self.context.player_catalog_controller,
            player_comparison_controller=self.context.player_comparison_controller,
            favorite_controller=self.context.favorite_controller,
            round_controller=self.context.round_controller,
            lineup_controller=self.context.lineup_controller,
            ranking_controller=self.context.ranking_controller,
            market_controller=self.context.market_controller,
            user_profile_controller=self.context.user_profile_controller,
        )
        self.login_window.showMaximized()
        self.close()

    def _atualizar_username(self, username):
        self.user_label.setText(f"Usuario: {username}")

    def _erro(self, mensagem):
        QMessageBox.warning(self, "SofaFut", mensagem)
