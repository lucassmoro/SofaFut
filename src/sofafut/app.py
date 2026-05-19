from PySide6.QtWidgets import QApplication

from sofafut.controllers.auth_controller import AuthController
from sofafut.views.login_window import LoginWindow
from sofafut.views.main_window import MainWindow


class SofaFutApp:
    def __init__(self) -> None:
        self.qt_app = QApplication.instance() or QApplication([])
        self.auth_controller = AuthController()
        self.login_window = LoginWindow()
        self.main_window: MainWindow | None = None
        self.login_window.login_requested.connect(self._handle_login)
        self.login_window.cadastro_requested.connect(self._handle_cadastro)

    def run(self) -> int:
        self.login_window.showMaximized()
        return self.qt_app.exec()

    def _handle_login(self, username: str, password: str) -> None:
        try:
            user = self.auth_controller.login(username, password)
        except ValueError as exc:
            self.login_window.show_login_error(str(exc))
            return

        self.login_window.clear_login_status()
        self.main_window = MainWindow(user.username)
        self.main_window.showMaximized()
        self.login_window.close()

    def _handle_cadastro(self, username: str, password: str) -> None:
        try:
            user = self.auth_controller.cadastrar(username, password)
        except ValueError as exc:
            self.login_window.show_cadastro_error(str(exc))
            return

        self.login_window.show_cadastro_success(user.username)
