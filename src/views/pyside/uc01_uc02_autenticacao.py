from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.views.pyside.style import STYLE


class LoginWindow(QMainWindow):
    def __init__(
        self,
        auth_controller,
        player_catalog_controller,
        player_comparison_controller,
        favorite_controller,
        round_controller,
        lineup_controller,
        ranking_controller,
        market_controller,
    ):
        super().__init__()
        self.auth_controller = auth_controller
        self.player_catalog_controller = player_catalog_controller
        self.player_comparison_controller = player_comparison_controller
        self.favorite_controller = favorite_controller
        self.round_controller = round_controller
        self.lineup_controller = lineup_controller
        self.ranking_controller = ranking_controller
        self.market_controller = market_controller
        self.main_window = None

        self.setWindowTitle("SofaFut")
        self.setMinimumSize(900, 700)
        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(48, 42, 48, 42)
        layout.addStretch(1)

        panel = QWidget()
        panel.setMaximumWidth(520)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setSpacing(12)

        title = QLabel("SofaFut")
        title.setProperty("role", "title")
        panel_layout.addWidget(title)
        panel_layout.addWidget(QLabel("Entre ou cadastre-se para montar sua escalação."))

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("usuario")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("senha")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        panel_layout.addWidget(self.username_input)
        panel_layout.addWidget(self.password_input)

        buttons = QHBoxLayout()
        login_button = QPushButton("Entrar")
        login_button.clicked.connect(self._login)
        cadastro_button = QPushButton("Cadastrar")
        cadastro_button.clicked.connect(self._cadastrar)
        buttons.addWidget(login_button)
        buttons.addWidget(cadastro_button)
        panel_layout.addLayout(buttons)

        layout.addWidget(panel, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        self.setCentralWidget(root)
        self.setStyleSheet(STYLE)

    def _login(self):
        username = self.username_input.text().strip()
        senha = self.password_input.text().strip()

        if not username or not senha:
            self._erro("Preencha usuario e senha.")
            return

        mensagem = self.auth_controller.login(username, senha)
        if mensagem != "Usuario logado":
            self._erro(mensagem)
            return

        from src.views.pyside.main_window import MainWindow

        self.main_window = MainWindow(
            username=username,
            auth_controller=self.auth_controller,
            player_catalog_controller=self.player_catalog_controller,
            player_comparison_controller=self.player_comparison_controller,
            favorite_controller=self.favorite_controller,
            round_controller=self.round_controller,
            lineup_controller=self.lineup_controller,
            ranking_controller=self.ranking_controller,
            market_controller=self.market_controller,
        )
        self.main_window.showMaximized()
        self.close()

    def _cadastrar(self):
        username = self.username_input.text().strip()
        senha = self.password_input.text().strip()

        if not username or not senha:
            self._erro("Preencha usuario e senha.")
            return

        mensagem = self.auth_controller.cadastrar(username=username, senha=senha)
        QMessageBox.information(self, "SofaFut", mensagem)

    def _erro(self, mensagem):
        QMessageBox.warning(self, "SofaFut", mensagem)
