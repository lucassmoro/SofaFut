from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from src.views.pyside.shared import fill_table, table


class AssetHistoryScreen:
    def __init__(self, context):
        self.context = context
        self.history_table = None

    def build(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        refresh_button = QPushButton("Atualizar historico")
        refresh_button.clicked.connect(self.preencher)
        self.history_table = table(["Data", "Tipo", "Jogador", "Valor", "Patrimonio apos"])
        layout.addWidget(refresh_button, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.history_table, 1)
        return tab

    def preencher(self):
        transacoes = self.context.market_controller.historico_patrimonio(
            self.context.username
        )
        fill_table(
            self.history_table,
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
                for item in transacoes
            ],
        )
