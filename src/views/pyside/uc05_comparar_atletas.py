from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.views.pyside.shared import fill_table, table


class ComparePlayersScreen:
    def __init__(self, context, show_error):
        self.context = context
        self.show_error = show_error
        self.compare_player_a = None
        self.compare_player_b = None
        self.compare_table = None

    def build(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        selectors = QHBoxLayout()
        self.compare_player_a = QComboBox()
        self.compare_player_b = QComboBox()
        compare_button = QPushButton("Comparar")
        compare_button.clicked.connect(self.comparar_jogadores)

        selectors.addWidget(QLabel("Atleta A"))
        selectors.addWidget(self.compare_player_a, 1)
        selectors.addWidget(QLabel("Atleta B"))
        selectors.addWidget(self.compare_player_b, 1)
        selectors.addWidget(compare_button)
        layout.addLayout(selectors)

        self.compare_table = table(["Metrica", "Atleta A", "Atleta B"])
        layout.addWidget(self.compare_table, 1)
        return tab

    def preencher_combos(self):
        self.compare_player_a.clear()
        self.compare_player_b.clear()
        for jogador in self.context.jogadores_catalogo:
            rotulo = f"{jogador.nome} - {jogador.nome_time or 'sem time'}"
            self.compare_player_a.addItem(rotulo)
            self.compare_player_b.addItem(rotulo)
        if len(self.context.jogadores_catalogo) > 1:
            self.compare_player_b.setCurrentIndex(1)

    def comparar_jogadores(self):
        if len(self.context.jogadores_catalogo) < 2:
            self.show_error("Carregue ao menos dois jogadores no catalogo.")
            return

        jogador_a = self.context.jogadores_catalogo[self.compare_player_a.currentIndex()]
        jogador_b = self.context.jogadores_catalogo[self.compare_player_b.currentIndex()]
        comparacao = self.context.player_comparison_controller.comparar(jogador_a, jogador_b)
        fill_table(
            self.compare_table,
            [
                [
                    metrica,
                    self.formatar_valor(valor_a),
                    self.formatar_valor(valor_b),
                ]
                for metrica, valor_a, valor_b in comparacao["metricas"]
            ],
        )

    def formatar_valor(self, valor):
        if isinstance(valor, float):
            return f"{valor:.2f}"
        return valor
