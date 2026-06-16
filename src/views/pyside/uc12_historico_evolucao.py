from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from src.views.pyside.shared import fill_table, table


class EvolutionHistoryScreen:
    def __init__(self, context):
        self.context = context
        self.score_table = None
        self.asset_table = None
        self.summary_text = None

    def build(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        refresh_button = QPushButton("Atualizar evolucao")
        refresh_button.clicked.connect(self.atualizar)
        layout.addWidget(refresh_button, 0, Qt.AlignmentFlag.AlignLeft)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(110)
        layout.addWidget(self.summary_text)

        layout.addWidget(QLabel("Pontuacao por rodada"))
        self.score_table = table(["Rodada", "Pontuacao", "Jogadores"])
        layout.addWidget(self.score_table, 1)

        layout.addWidget(QLabel("Patrimonio por transacao"))
        self.asset_table = table(["Data", "Tipo", "Jogador", "Valor", "Patrimonio apos"])
        layout.addWidget(self.asset_table, 1)
        return tab

    def atualizar(self):
        historico_pontos = self.context.ranking_controller.historico_pontuacao_usuario(
            self.context.username
        )
        historico_patrimonio = self.context.market_controller.historico_patrimonio(
            self.context.username
        )

        fill_table(
            self.score_table,
            [
                [
                    item.rodada,
                    f"{float(item.pontuacao or 0):.2f}",
                    len(item.jogadores),
                ]
                for item in historico_pontos
            ],
        )
        fill_table(
            self.asset_table,
            [
                [
                    f"{item.data_hora:%d/%m/%Y %H:%M}",
                    item.tipo.value,
                    item.jogador.nome,
                    f"{item.valor:.2f}",
                    (
                        f"{item.patrimonio_apos:.2f}"
                        if item.patrimonio_apos is not None
                        else ""
                    ),
                ]
                for item in historico_patrimonio
            ],
        )
        pontuacao_total = sum(float(item.pontuacao or 0) for item in historico_pontos)
        patrimonio_atual = self.context.market_controller.patrimonio(self.context.username)
        self.summary_text.setPlainText(
            "\n".join(
                [
                    f"Rodadas com pontuacao: {len(historico_pontos)}",
                    f"Pontuacao acumulada no historico: {pontuacao_total:.2f}",
                    f"Transacoes de mercado: {len(historico_patrimonio)}",
                    f"Patrimonio atual: {patrimonio_atual:.2f}",
                ]
            )
        )
