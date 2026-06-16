from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.views.pyside.shared import fill_table, table


class RoundMatchesScreen:
    def __init__(self, context, show_error):
        self.context = context
        self.show_error = show_error
        self.temporada_combo = None
        self.rodada_combo = None
        self.matches_table = None
        self.status = None

    def build(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        filters = QHBoxLayout()
        self.temporada_combo = QComboBox()
        self.temporada_combo.addItems(
            [str(item) for item in self.context.round_controller.listar_temporadas_disponiveis()]
        )
        self.rodada_combo = QComboBox()
        self.rodada_combo.addItems(
            [str(item) for item in self.context.round_controller.listar_rodadas_disponiveis()]
        )
        load_button = QPushButton("Carregar jogos")
        load_button.clicked.connect(self.carregar_jogos)

        filters.addWidget(QLabel("Temporada"))
        filters.addWidget(self.temporada_combo)
        filters.addWidget(QLabel("Rodada"))
        filters.addWidget(self.rodada_combo)
        filters.addWidget(load_button)
        filters.addStretch(1)
        layout.addLayout(filters)

        self.matches_table = table(
            ["Data", "Status", "Mandante", "Placar", "Visitante", "Estadio", "Cidade"]
        )
        layout.addWidget(self.matches_table, 1)

        self.status = QLabel("")
        layout.addWidget(self.status)
        return tab

    def carregar_jogos(self):
        try:
            temporada = int(self.temporada_combo.currentText())
            rodada = int(self.rodada_combo.currentText())
            jogos = self.context.round_controller.listar_jogos_rodada(
                temporada=temporada,
                numero_rodada=rodada,
            )
            fill_table(
                self.matches_table,
                [
                    [
                        self._formatar_data(jogo["data"]),
                        jogo["status"],
                        jogo["mandante"],
                        self._formatar_placar(
                            jogo["gols_mandante"],
                            jogo["gols_visitante"],
                        ),
                        jogo["visitante"],
                        jogo["estadio"],
                        jogo["cidade"],
                    ]
                    for jogo in jogos
                ],
            )
            self.status.setText(f"{len(jogos)} jogos carregados")
        except Exception as exc:
            self.show_error(str(exc))

    def _formatar_placar(self, mandante, visitante):
        if mandante is None or visitante is None:
            return ""
        return f"{mandante} x {visitante}"

    def _formatar_data(self, data):
        if not data:
            return ""
        return data.replace("T", " ").split("+", 1)[0]
