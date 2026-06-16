from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QTextEdit, QVBoxLayout, QWidget


class RankingScreen:
    def __init__(self, context):
        self.context = context
        self.ranking_text = None

    def build(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        refresh = QPushButton("Atualizar ranking")
        refresh.clicked.connect(self.atualizar)
        self.ranking_text = QTextEdit()
        self.ranking_text.setReadOnly(True)
        layout.addWidget(refresh, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.ranking_text, 1)
        return tab

    def atualizar(self):
        self.ranking_text.setPlainText(
            self.context.ranking_controller.formatar_ranking_usuarios()
        )
