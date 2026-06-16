from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.views.pyside.shared import fill_players_table, fill_table, selected_rows, table


class FavoritesScreen:
    def __init__(self, context, show_error):
        self.context = context
        self.show_error = show_error
        self.favorite_players_table = None
        self.favorite_clubs_table = None

    def build(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)

        players_col = QVBoxLayout()
        players_col.addWidget(QLabel("Jogadores favoritos"))
        self.favorite_players_table = table(["ID", "Jogador", "Time", "Pos", "Valor"])
        players_col.addWidget(self.favorite_players_table, 1)
        remove_player_button = QPushButton("Remover jogador")
        remove_player_button.clicked.connect(self.remover_jogador_favorito)
        players_col.addWidget(remove_player_button)

        clubs_col = QVBoxLayout()
        clubs_col.addWidget(QLabel("Clubes favoritos"))
        self.favorite_clubs_table = table(["Clube"])
        clubs_col.addWidget(self.favorite_clubs_table, 1)
        remove_club_button = QPushButton("Remover clube")
        remove_club_button.clicked.connect(self.remover_clube_favorito)
        clubs_col.addWidget(remove_club_button)

        layout.addLayout(players_col, 3)
        layout.addLayout(clubs_col, 2)
        return tab

    def preencher(self):
        self.context.jogadores_favoritos = self.context.favorite_controller.listar_jogadores(
            self.context.username
        )
        self.context.clubes_favoritos = self.context.favorite_controller.listar_clubes(
            self.context.username
        )
        fill_players_table(self.favorite_players_table, self.context.jogadores_favoritos)
        fill_table(
            self.favorite_clubs_table,
            [[clube] for clube in self.context.clubes_favoritos],
        )

    def remover_jogador_favorito(self):
        linhas = selected_rows(self.favorite_players_table)
        if not linhas:
            return
        try:
            jogador = self.context.jogadores_favoritos[linhas[0]]
            self.context.favorite_controller.remover_jogador(self.context.username, jogador)
            self.preencher()
        except Exception as exc:
            self.show_error(str(exc))

    def remover_clube_favorito(self):
        linhas = selected_rows(self.favorite_clubs_table)
        if not linhas:
            return
        try:
            clube = self.context.clubes_favoritos[linhas[0]]
            self.context.favorite_controller.remover_clube(self.context.username, clube)
            self.preencher()
        except Exception as exc:
            self.show_error(str(exc))
