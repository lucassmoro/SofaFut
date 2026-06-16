from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.views.pyside.shared import fill_table, table


class PlayerStatsScreen:
    def __init__(self, context, show_error):
        self.context = context
        self.show_error = show_error
        self.player_combo = None
        self.details_table = None
        self.stats_table = None
        self.status = None

    def build(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        selectors = QHBoxLayout()
        self.player_combo = QComboBox()
        refresh_button = QPushButton("Atualizar atletas")
        refresh_button.clicked.connect(self.atualizar_atletas)
        show_button = QPushButton("Ver estatisticas")
        show_button.clicked.connect(self.mostrar_estatisticas)

        selectors.addWidget(QLabel("Atleta"))
        selectors.addWidget(self.player_combo, 1)
        selectors.addWidget(refresh_button)
        selectors.addWidget(show_button)
        layout.addLayout(selectors)

        self.details_table = table(["Campo", "Valor"])
        self.stats_table = table(["Estatistica", "Valor"])
        layout.addWidget(QLabel("Dados do atleta"))
        layout.addWidget(self.details_table, 1)
        layout.addWidget(QLabel("Metricas"))
        layout.addWidget(self.stats_table, 1)

        self.status = QLabel("")
        layout.addWidget(self.status)
        return tab

    def atualizar_atletas(self):
        jogadores = self._jogadores_catalogo()
        self.player_combo.clear()
        for jogador in jogadores:
            self.player_combo.addItem(self._rotulo_jogador(jogador))
        self.status.setText(f"{len(jogadores)} atletas disponiveis")
        if jogadores:
            self.mostrar_estatisticas()

    def mostrar_estatisticas(self):
        jogadores = self._jogadores_catalogo()
        if not jogadores:
            self.show_error("Carregue o catalogo de atletas primeiro.")
            return

        jogador = jogadores[self.player_combo.currentIndex()]
        estatisticas = self.context.player_comparison_controller.estatisticas_jogador(jogador)
        fill_table(
            self.details_table,
            [
                ["ID", jogador.api_id or ""],
                ["Nome", jogador.nome or ""],
                ["Clube", jogador.nome_time or ""],
                ["Posicao", jogador.posicao or ""],
                ["Idade", jogador.idade or 0],
                ["Valor de mercado", f"{float(jogador.valor_mercado or 0):.2f}"],
            ],
        )
        fill_table(
            self.stats_table,
            [
                ["Gols", estatisticas["gols"]],
                ["Assistencias", estatisticas["assistencias"]],
                ["Faltas", estatisticas["faltas"]],
                ["Cartoes amarelos", estatisticas["cartoes_amarelos"]],
                ["Cartoes vermelhos", estatisticas["cartoes_vermelhos"]],
                ["Gols sofridos", estatisticas["gols_sofridos"]],
            ],
        )

    def _jogadores_catalogo(self):
        if not self.context.jogadores_catalogo:
            self.context.jogadores_catalogo = self.context.player_catalog_controller.listar_jogadores()
        return self.context.jogadores_catalogo

    def _rotulo_jogador(self, jogador):
        return f"{jogador.nome} - {jogador.nome_time or 'sem time'}"
