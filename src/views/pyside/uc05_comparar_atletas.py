from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.views.pyside.shared import fill_table, table


class ComparePlayersScreen:
    def __init__(self, context, show_error):
        self.context = context
        self.show_error = show_error
        self.compare_player_a = None
        self.compare_player_b = None
        self.team_filter_a = None
        self.team_filter_b = None
        self.compare_table = None
        self.jogadores_comparacao_a = []
        self.jogadores_comparacao_b = []

    def build(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        filters = QHBoxLayout()
        self.team_filter_a = QComboBox()
        self.team_filter_b = QComboBox()
        self.team_filter_a.currentTextChanged.connect(self.preencher_combo_a)
        self.team_filter_b.currentTextChanged.connect(self.preencher_combo_b)
        filters.addWidget(QLabel("Time A"))
        filters.addWidget(self.team_filter_a, 1)
        filters.addWidget(QLabel("Time B"))
        filters.addWidget(self.team_filter_b, 1)
        layout.addLayout(filters)

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
        self._preencher_filtro_times()
        self.preencher_combo_a()
        self.preencher_combo_b()
        if len(self.jogadores_comparacao_b) > 1:
            self.compare_player_b.setCurrentIndex(1)

    def preencher_combo_a(self):
        self.compare_player_a.clear()
        self.jogadores_comparacao_a = self._jogadores_filtrados(
            self.team_filter_a.currentText() if self.team_filter_a else "Todos"
        )
        for jogador in self.jogadores_comparacao_a:
            self.compare_player_a.addItem(self._rotulo_jogador(jogador))

    def preencher_combo_b(self):
        self.compare_player_b.clear()
        self.jogadores_comparacao_b = self._jogadores_filtrados(
            self.team_filter_b.currentText() if self.team_filter_b else "Todos"
        )
        for jogador in self.jogadores_comparacao_b:
            self.compare_player_b.addItem(self._rotulo_jogador(jogador))

    def _jogadores_filtrados(self, time):
        jogadores = self.context.jogadores_catalogo
        if time != "Todos":
            jogadores = [
                jogador
                for jogador in jogadores
                if (jogador.nome_time or "sem time") == time
            ]
        return sorted(
            jogadores,
            key=lambda jogador: (
                (jogador.nome or "").casefold(),
                (jogador.nome_time or "").casefold(),
            ),
        )

    def _preencher_filtro_times(self):
        if self.team_filter_a is None or self.team_filter_b is None:
            return

        atual_a = self.team_filter_a.currentText() or "Todos"
        atual_b = self.team_filter_b.currentText() or "Todos"
        times = sorted(
            {
                jogador.nome_time or "sem time"
                for jogador in self.context.jogadores_catalogo
            },
            key=lambda time: time.casefold(),
        )
        opcoes = ["Todos"] + times
        opcoes_a = self._opcoes_combo(self.team_filter_a)
        opcoes_b = self._opcoes_combo(self.team_filter_b)
        if opcoes_a == opcoes and opcoes_b == opcoes:
            return

        self._atualizar_opcoes_combo(self.team_filter_a, opcoes, atual_a)
        self._atualizar_opcoes_combo(self.team_filter_b, opcoes, atual_b)

    def _opcoes_combo(self, combo):
        return [combo.itemText(indice) for indice in range(combo.count())]

    def _atualizar_opcoes_combo(self, combo, opcoes, atual):
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(opcoes)
        if atual in opcoes:
            combo.setCurrentText(atual)
        combo.blockSignals(False)

    def _rotulo_jogador(self, jogador):
        return f"{jogador.nome} - {jogador.nome_time or 'sem time'}"

    def comparar_jogadores(self):
        if not self.jogadores_comparacao_a or not self.jogadores_comparacao_b:
            self.show_error("Carregue ao menos dois jogadores no catalogo.")
            return

        jogador_a = self.jogadores_comparacao_a[self.compare_player_a.currentIndex()]
        jogador_b = self.jogadores_comparacao_b[self.compare_player_b.currentIndex()]
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
