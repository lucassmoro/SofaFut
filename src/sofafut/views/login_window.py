from collections.abc import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from sofafut.infrastructure.settings import PROJECT_ROOT


class BackgroundWidget(QWidget):
    def __init__(self, image_path: str) -> None:
        super().__init__()
        self._background = QPixmap(image_path)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        if not self._background.isNull():
            target = self.rect()
            scaled_height = int(self._background.height() * target.width() / self._background.width())
            if scaled_height < target.height():
                scaled_height = target.height()
                scaled_width = int(self._background.width() * target.height() / self._background.height())
            else:
                scaled_width = target.width()
            scaled = self._background.scaled(
                scaled_width,
                scaled_height,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (target.width() - scaled.width()) // 2
            y = (target.height() - scaled.height()) // 2
            painter.fillRect(target, QColor(38, 13, 51))
            painter.drawPixmap(x, y, scaled)

        painter.fillRect(self.rect(), QColor(38, 13, 51, 72))
        painter.fillRect(self.rect(), QColor(0, 63, 105, 42))


class LoginWindow(QMainWindow):
    login_requested = Signal(str, str)
    cadastro_requested = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SofaFut")
        self._configure_window_size()
        self._build_ui()

    def _configure_window_size(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            self.setMinimumSize(1120, 820)
            self.resize(1120, 820)
            return

        available_size = screen.availableGeometry().size()
        self.setMinimumSize(900, 760)
        self.resize(available_size)

    def _build_ui(self) -> None:
        background_path = PROJECT_ROOT / "data" / "images" / "ChatGPT Image May 17, 2026, 11_36_06 PM.png"
        root = BackgroundWidget(str(background_path))
        root.setObjectName("root")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(48, 42, 48, 42)
        root_layout.setSpacing(0)

        panel = QFrame()
        panel.setObjectName("authPanel")
        panel.setMaximumWidth(560)
        panel.setMinimumWidth(460)
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(38)
        shadow.setOffset(0, 16)
        shadow.setColor(QColor(38, 13, 51, 145))
        panel.setGraphicsEffect(shadow)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(38, 36, 38, 36)
        panel_layout.setSpacing(20)

        title = QLabel("SofaFut")
        title.setObjectName("title")
        subtitle = QLabel("Acesse sua conta para montar e acompanhar seu time.")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        panel_layout.addWidget(title)
        panel_layout.addWidget(subtitle)
        panel_layout.addSpacing(2)
        panel_layout.addWidget(self._build_login_section())
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setObjectName("divider")
        panel_layout.addWidget(divider)
        panel_layout.addWidget(self._build_cadastro_section())

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addStretch(1)
        row.addWidget(panel, 0)
        row.addStretch(1)

        root_layout.addStretch(1)
        root_layout.addLayout(row)
        root_layout.addStretch(1)

        self.setCentralWidget(root)
        self.setStyleSheet(
            """
            QLabel#title {
                color: #003f69;
                font-size: 36px;
                font-weight: 700;
            }
            QLabel#subtitle {
                color: #106b87;
                font-size: 15px;
            }
            QLabel[role="sectionTitle"] {
                color: #003f69;
                font-size: 19px;
                font-weight: 700;
            }
            QLabel[role="helpText"] {
                color: #106b87;
                font-size: 13px;
            }
            QLabel[role="statusText"] {
                color: #260d33;
                min-height: 16px;
            }
            QFrame#authPanel {
                background: rgba(250, 248, 244, 238);
                border: 1px solid rgba(179, 172, 164, 215);
                border-radius: 12px;
            }
            QFrame#divider {
                color: #b3aca4;
            }
            QLineEdit {
                border: 1px solid #b3aca4;
                border-radius: 6px;
                padding: 7px 12px;
                min-height: 18px;
                font-size: 14px;
                background: #ffffff;
                color: #260d33;
                selection-background-color: #157a8c;
            }
            QLineEdit:focus {
                border: 2px solid #157a8c;
            }
            QPushButton {
                background: #003f69;
                border: 0;
                border-radius: 6px;
                color: #ffffff;
                font-weight: 700;
                padding: 8px 18px;
                min-width: 176px;
                min-height: 28px;
            }
            QPushButton:hover {
                background: #106b87;
            }
            QPushButton#secondaryButton {
                background: #157a8c;
            }
            QPushButton#secondaryButton:hover {
                background: #106b87;
            }
            QLabel[role="fieldLabel"] {
                color: #260d33;
                font-size: 13px;
                font-weight: 700;
                min-height: 18px;
                min-width: 58px;
            }
            """
        )

    def _build_login_section(self) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        section_title = QLabel("Login")
        section_title.setProperty("role", "sectionTitle")
        layout.addWidget(section_title)

        self.login_user_input = QLineEdit()
        self.login_user_input.setPlaceholderText("usuario")
        self.login_user_input.setFixedHeight(38)
        self.login_password_input = QLineEdit()
        self.login_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password_input.setPlaceholderText("senha")
        self.login_password_input.setFixedHeight(38)
        self.login_status_label = QLabel("")
        self.login_status_label.setProperty("role", "statusText")

        layout.addWidget(self._field_block("User", self.login_user_input))
        layout.addWidget(self._field_block("Senha", self.login_password_input))
        layout.addWidget(self.login_status_label)
        layout.addLayout(self._button_row("Entrar", self._handle_login))

        self.login_password_input.returnPressed.connect(self._handle_login)
        return section

    def _build_cadastro_section(self) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        section_title = QLabel("Cadastro")
        section_title.setProperty("role", "sectionTitle")
        help_text = QLabel("Caso nao tenha conta, cadastre-se.")
        help_text.setProperty("role", "helpText")
        layout.addWidget(section_title)
        layout.addWidget(help_text)

        self.cadastro_user_input = QLineEdit()
        self.cadastro_user_input.setPlaceholderText("usuario")
        self.cadastro_user_input.setFixedHeight(38)
        self.cadastro_password_input = QLineEdit()
        self.cadastro_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.cadastro_password_input.setPlaceholderText("senha")
        self.cadastro_password_input.setFixedHeight(38)
        self.cadastro_status_label = QLabel("")
        self.cadastro_status_label.setProperty("role", "statusText")

        layout.addWidget(self._field_block("User", self.cadastro_user_input))
        layout.addWidget(self._field_block("Senha", self.cadastro_password_input))
        layout.addWidget(self.cadastro_status_label)
        layout.addLayout(self._button_row("Cadastrar", self._handle_cadastro, secondary=True))

        self.cadastro_password_input.returnPressed.connect(self._handle_cadastro)
        return section

    def _field_block(self, label_text: str, input_widget: QLineEdit) -> QWidget:
        block = QWidget()
        block.setMaximumWidth(420)
        block.setFixedHeight(42)
        block.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(block)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        label = QLabel(label_text)
        label.setProperty("role", "fieldLabel")
        label.setFixedWidth(58)
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        input_widget.setMinimumWidth(300)
        layout.addWidget(label)
        layout.addWidget(input_widget, 1)
        return block

    def _button_row(self, label: str, callback: Callable[[], None], secondary: bool = False) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addStretch()
        button = QPushButton(label)
        button.setFixedHeight(42)
        if secondary:
            button.setObjectName("secondaryButton")
        button.clicked.connect(callback)
        row.addWidget(button)
        return row

    def _handle_login(self) -> None:
        self.login_requested.emit(
            self.login_user_input.text(),
            self.login_password_input.text(),
        )

    def _handle_cadastro(self) -> None:
        self.cadastro_requested.emit(
            self.cadastro_user_input.text(),
            self.cadastro_password_input.text(),
        )

    def show_login_error(self, message: str) -> None:
        self.login_status_label.setText(message)

    def clear_login_status(self) -> None:
        self.login_status_label.setText("")

    def show_cadastro_error(self, message: str) -> None:
        self.cadastro_status_label.setText(message)

    def show_cadastro_success(self, username: str) -> None:
        self.cadastro_status_label.setText(f"Usuario {username} cadastrado.")
        self.cadastro_password_input.clear()
        QMessageBox.information(self, "Cadastro", "Usuario cadastrado com sucesso.")
