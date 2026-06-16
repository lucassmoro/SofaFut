from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from src.views.pyside.shared import (
    fill_players_table,
    next_sort_direction,
    selected_rows,
    sortable_value,
    table,
)


class MarketScreen:
    def __init__(
        self,
        context,
        show_lineup,
        refresh_lineup,
        refresh_favorites,
        refresh_history,
        show_error,
    ):
        self.context = context
        self.show_lineup = show_lineup
        self.refresh_lineup = refresh_lineup
        self.refresh_favorites = refresh_favorites
        self.refresh_history = refresh_history
        self.show_error = show_error
        self.market_catalog_table = None
        self.market_roster_table = None
        self.market_status = None
        self.transactions_text = None

    def build(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)

        catalog_col = QVBoxLayout()
        catalog_col.addWidget(QLabel("Jogadores disponiveis na rodada"))
        self.market_catalog_table = table(["ID", "Jogador", "Time", "Pos", "Valor"])
        self.market_catalog_table.horizontalHeader().sectionClicked.connect(
            self.ordenar_jogadores_mercado
        )
        catalog_col.addWidget(self.market_catalog_table, 1)
        buy_button = QPushButton("Comprar selecionado")
        buy_button.clicked.connect(self.comprar_selecionado)
        catalog_col.addWidget(buy_button)
        favorite_player_button = QPushButton("Favoritar jogador")
        favorite_player_button.clicked.connect(self.favoritar_jogador_mercado)
        catalog_col.addWidget(favorite_player_button)
        favorite_club_button = QPushButton("Favoritar clube")
        favorite_club_button.clicked.connect(self.favoritar_clube_mercado)
        catalog_col.addWidget(favorite_club_button)

        roster_col = QVBoxLayout()
        self.market_status = QLabel("")
        roster_col.addWidget(self.market_status)
        self.market_roster_table = table(["ID", "Jogador", "Time", "Pos", "Valor"])
        roster_col.addWidget(self.market_roster_table, 1)
        sell_button = QPushButton("Vender selecionado")
        sell_button.clicked.connect(self.vender_selecionado)
        roster_col.addWidget(sell_button)
        confirm_button = QPushButton("Confirmar elenco")
        confirm_button.clicked.connect(self.confirmar_elenco)
        roster_col.addWidget(confirm_button)
        self.transactions_text = QTextEdit()
        self.transactions_text.setReadOnly(True)
        self.transactions_text.setMaximumHeight(130)
        roster_col.addWidget(self.transactions_text)

        layout.addLayout(catalog_col, 3)
        layout.addLayout(roster_col, 2)
        return tab

    def comprar_selecionado(self):
        linhas = selected_rows(self.market_catalog_table)
        if not linhas:
            return
        try:
            self.context.market_controller.comprar(
                self.context.username,
                self.context.jogadores_mercado[linhas[0]],
            )
            self.atualizar()
        except Exception as exc:
            self.show_error(str(exc))

    def favoritar_jogador_mercado(self):
        linhas = selected_rows(self.market_catalog_table)
        if not linhas:
            return
        try:
            jogador = self.context.jogadores_mercado[linhas[0]]
            self.context.favorite_controller.favoritar_jogador(self.context.username, jogador)
            self.refresh_favorites()
        except Exception as exc:
            self.show_error(str(exc))

    def favoritar_clube_mercado(self):
        linhas = selected_rows(self.market_catalog_table)
        if not linhas:
            return
        try:
            jogador = self.context.jogadores_mercado[linhas[0]]
            self.context.favorite_controller.favoritar_clube(
                self.context.username,
                jogador.nome_time,
            )
            self.refresh_favorites()
        except Exception as exc:
            self.show_error(str(exc))

    def vender_selecionado(self):
        linhas = selected_rows(self.market_roster_table)
        if not linhas:
            return
        try:
            elenco = self.context.market_controller.listar_elenco(self.context.username)
            self.context.market_controller.vender(self.context.username, elenco[linhas[0]])
            self.atualizar()
        except Exception as exc:
            self.show_error(str(exc))

    def confirmar_elenco(self):
        if len(self.context.jogadores_escalados) != 11:
            self.show_error("Compre exatamente 11 jogadores antes de confirmar.")
            return

        self.show_lineup()
        self.refresh_lineup(
            "11/11 jogadores. Escolha o capitao e calcule a pontuacao."
        )

    def atualizar(self):
        elenco = self.context.market_controller.listar_elenco(self.context.username)
        self.context.jogadores_escalados = list(elenco)
        if self.context.capitao not in self.context.jogadores_escalados:
            self.context.capitao = None

        self.preencher_catalogo()
        fill_players_table(self.market_roster_table, elenco)
        self.market_status.setText(
            f"Patrimonio: {self.context.market_controller.patrimonio(self.context.username):.2f} | "
            f"Elenco: {len(elenco)} jogadores"
        )
        self.transactions_text.setPlainText(
            "\n".join(
                [
                    (
                        f"{item.data_hora:%d/%m %H:%M} - {item.tipo.value}: "
                        f"{item.jogador.nome} ({item.valor:.2f})"
                    )
                    for item in self.context.market_controller.listar_transacoes(
                        self.context.username
                    )[-8:]
                ]
            )
        )
        self.refresh_lineup()
        self.refresh_favorites()
        self.refresh_history()

    def preencher_catalogo(self):
        jogadores_rodada = self.context.lineup_controller.selecionar_players_do_catalogo(
            self.context.jogadores_disponiveis
        )
        api_ids_elenco = {
            jogador.api_id
            for jogador in self.context.market_controller.listar_elenco(self.context.username)
        }
        self.context.jogadores_mercado = [
            jogador for jogador in jogadores_rodada if jogador.api_id not in api_ids_elenco
        ]
        fill_players_table(self.market_catalog_table, self.context.jogadores_mercado)

    def ordenar_jogadores_mercado(self, section):
        atributo = ["api_id", "nome", "nome_time", "posicao", "valor_mercado"][section]
        reverse = next_sort_direction(self.context, f"mercado:{atributo}")
        self.context.jogadores_mercado.sort(
            key=lambda jogador: sortable_value(getattr(jogador, atributo, None)),
            reverse=reverse,
        )
        fill_players_table(self.market_catalog_table, self.context.jogadores_mercado)

    def reiniciar_elenco_rodada(self):
        self.context.capitao = None
        self.context.jogadores_escalados = []
        self.context.market_controller.limpar_elenco_rodada(self.context.username)
        self.atualizar()
