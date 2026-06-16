from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from src.views.pyside.shared import fill_table, next_sort_direction, sortable_value, table


class RoundScreen:
    def __init__(
        self,
        context,
        show_market,
        on_catalog_loaded,
        on_players_loaded,
        on_round_reset,
        show_error,
    ):
        self.context = context
        self.show_market = show_market
        self.on_catalog_loaded = on_catalog_loaded
        self.on_players_loaded = on_players_loaded
        self.on_round_reset = on_round_reset
        self.show_error = show_error
        self.temporada_combo = None
        self.rodada_combo = None
        self.max_partidas_input = None
        self.available_table = None
        self.round_status = None

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
        self.max_partidas_input = QLineEdit("10")
        self.max_partidas_input.setMaximumWidth(70)
        carregar_button = QPushButton("Carregar rodada")
        carregar_button.clicked.connect(self.carregar_rodada)

        filters.addWidget(QLabel("Temporada"))
        filters.addWidget(self.temporada_combo)
        filters.addWidget(QLabel("Rodada"))
        filters.addWidget(self.rodada_combo)
        filters.addWidget(QLabel("Max. partidas"))
        filters.addWidget(self.max_partidas_input)
        filters.addWidget(carregar_button)
        filters.addStretch(1)
        layout.addLayout(filters)

        self.available_table = table(["ID", "Jogador", "Time", "Pos", "Min", "Partida"])
        self.available_table.horizontalHeader().sectionClicked.connect(
            self.ordenar_jogadores_disponiveis
        )
        layout.addWidget(self.available_table, 1)
        add_button = QPushButton("Ir para mercado")
        add_button.clicked.connect(self.show_market)
        self.round_status = QLabel("")
        footer = QHBoxLayout()
        footer.addWidget(add_button)
        footer.addWidget(self.round_status)
        footer.addStretch(1)
        layout.addLayout(footer)
        return tab

    def carregar_catalogo(self):
        temporada = int(self.temporada_combo.currentText())
        self.context.jogadores_catalogo = (
            self.context.player_catalog_controller.carregar_jogadores_temporada(
                temporada=temporada
            )
        )
        self.on_catalog_loaded()
        self.round_status.setText(
            f"Catalogo carregado: {len(self.context.jogadores_catalogo)} jogadores"
        )

    def carregar_rodada(self):
        try:
            temporada = int(self.temporada_combo.currentText())
            rodada = int(self.rodada_combo.currentText())
            dados = self.context.round_controller.carregar_dados_rodada_cache(
                temporada=temporada,
                numero_rodada=rodada,
            )
            total = len(dados.get("partidas_api", {}).get("response", []))
            cacheadas = len(dados.get("partidas", []))
            self.listar_jogadores_rodada()
            self.on_round_reset()
            self.round_status.setText(
                f"Rodada {rodada}: {cacheadas}/{total} partidas com estatisticas em cache"
            )
        except Exception as exc:
            self.show_error(str(exc))

    def listar_jogadores_rodada(self):
        try:
            temporada = int(self.temporada_combo.currentText())
            rodada = int(self.rodada_combo.currentText())
            self.context.jogadores_disponiveis = (
                self.context.round_controller.listar_jogadores_disponiveis(
                    temporada=temporada,
                    numero_rodada=rodada,
                )
            )
            self.preencher_jogadores_disponiveis()
            self.round_status.setText(
                f"{len(self.context.jogadores_disponiveis)} atuacoes disponiveis"
            )
            self.on_players_loaded()
        except Exception as exc:
            self.show_error(str(exc))

    def preencher_jogadores_disponiveis(self):
        fill_table(
            self.available_table,
            [
                [
                    item.get("api_id") or "",
                    item.get("nome") or "",
                    item.get("time") or "",
                    item.get("posicao") or "",
                    item.get("minutos") or 0,
                    item.get("partida") or "",
                ]
                for item in self.context.jogadores_disponiveis
            ],
        )

    def ordenar_jogadores_disponiveis(self, section):
        coluna = ["api_id", "nome", "time", "posicao", "minutos", "partida"][section]
        reverse = next_sort_direction(self.context, f"disponiveis:{coluna}")
        self.context.jogadores_disponiveis.sort(
            key=lambda jogador: sortable_value(jogador.get(coluna)),
            reverse=reverse,
        )
        self.preencher_jogadores_disponiveis()
        self.on_players_loaded()

    def temporada(self):
        return int(self.temporada_combo.currentText())

    def rodada(self):
        return int(self.rodada_combo.currentText())

    def max_partidas(self):
        valor = self.max_partidas_input.text().strip()
        return int(valor) if valor else None
