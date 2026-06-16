from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from src.views.pyside.shared import fill_table, selected_rows, table


class LineupScoreScreen:
    def __init__(
        self,
        context,
        get_temporada,
        get_rodada,
        refresh_market,
        refresh_ranking,
        show_error,
    ):
        self.context = context
        self.get_temporada = get_temporada
        self.get_rodada = get_rodada
        self.refresh_market = refresh_market
        self.refresh_ranking = refresh_ranking
        self.show_error = show_error
        self.lineup_table = None
        self.lineup_status = None
        self.score_text = None

    def build(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.lineup_table = table(["ID", "Jogador", "Time", "Pos", "Capitao"])
        layout.addWidget(self.lineup_table, 1)

        footer = QHBoxLayout()
        captain_button = QPushButton("Definir capitao")
        captain_button.clicked.connect(self.definir_capitao)
        remove_button = QPushButton("Remover")
        remove_button.clicked.connect(self.remover_escalado)
        score_button = QPushButton("Calcular pontuacao")
        score_button.clicked.connect(self.calcular_pontuacao)
        self.lineup_status = QLabel("0/11 jogadores")
        footer.addWidget(captain_button)
        footer.addWidget(remove_button)
        footer.addWidget(score_button)
        footer.addWidget(self.lineup_status)
        footer.addStretch(1)
        layout.addLayout(footer)

        self.score_text = QTextEdit()
        self.score_text.setReadOnly(True)
        self.score_text.setMaximumHeight(170)
        layout.addWidget(self.score_text)
        return tab

    def preencher(self, status=None):
        fill_table(
            self.lineup_table,
            [
                [
                    jogador.api_id or "",
                    jogador.nome or "",
                    jogador.nome_time or "",
                    jogador.posicao or "",
                    "Sim" if jogador is self.context.capitao else "",
                ]
                for jogador in self.context.jogadores_escalados
            ],
        )
        self.lineup_status.setText(
            status or f"{len(self.context.jogadores_escalados)}/11 jogadores"
        )

    def definir_capitao(self):
        linhas = selected_rows(self.lineup_table)
        if not linhas:
            return
        self.context.capitao = self.context.jogadores_escalados[linhas[0]]
        self.preencher()

    def remover_escalado(self):
        linhas = selected_rows(self.lineup_table)
        if not linhas:
            return
        try:
            jogador = self.context.jogadores_escalados[linhas[0]]
            self.context.market_controller.vender(self.context.username, jogador)
            self.refresh_market()
        except Exception as exc:
            self.show_error(str(exc))

    def calcular_pontuacao(self):
        try:
            if len(self.context.jogadores_escalados) != 11:
                raise RuntimeError("Voce precisa comprar exatamente 11 jogadores para a rodada.")

            if self.context.capitao is None:
                raise RuntimeError("Escolha um capitao antes de calcular a pontuacao.")

            rodada = self.get_rodada()
            jogadores_fantasy = self.context.lineup_controller.criar_escalacao_fantasy(
                self.context.jogadores_escalados,
                capitao=self.context.capitao,
            )
            rodada_model = self.context.round_controller.montar_rodada_por_cache(
                temporada=self.get_temporada(),
                numero_rodada=rodada,
                jogadores_escalados=self.context.jogadores_escalados,
            )
            self.context.round_controller.adicionar_rodada(rodada_model)
            pontuacao_total = self.context.lineup_controller.executar_rodada(
                username=self.context.username,
                numero_rodada=rodada,
                jogadores_fantasy=jogadores_fantasy,
            )
            escalacao = self.context.lineup_controller.buscar_escalacao(rodada)
            jogadores_calculados = (
                escalacao.jogadores if escalacao is not None else jogadores_fantasy
            )
            self.score_text.setPlainText(
                "\n".join(
                    [
                        f"Rodada {rodada}: {pontuacao_total} pontos",
                        "",
                        *[
                            (
                                f"{item.jogador.nome}"
                                f"{' (capitao)' if item.capitao else ''}: "
                                f"{item.pontuacao} pontos"
                            )
                            for item in jogadores_calculados
                        ],
                    ]
                )
            )
            self.refresh_ranking()
        except Exception as exc:
            self.show_error(str(exc))
