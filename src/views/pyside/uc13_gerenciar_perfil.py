from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ProfileScreen:
    def __init__(self, context, on_username_changed, show_error):
        self.context = context
        self.on_username_changed = on_username_changed
        self.show_error = show_error
        self.email_input = None
        self.username_input = None
        self.current_password_input = None
        self.new_password_input = None
        self.status = None

    def build(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        form = QFormLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("novo email")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("novo username")
        self.current_password_input = QLineEdit()
        self.current_password_input.setPlaceholderText("senha atual")
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("nova senha")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Email", self.email_input)
        form.addRow("Username", self.username_input)
        form.addRow("Senha atual", self.current_password_input)
        form.addRow("Nova senha", self.new_password_input)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        email_button = QPushButton("Alterar email")
        email_button.clicked.connect(self.alterar_email)
        username_button = QPushButton("Alterar username")
        username_button.clicked.connect(self.alterar_username)
        password_button = QPushButton("Alterar senha")
        password_button.clicked.connect(self.alterar_senha)
        buttons.addWidget(email_button)
        buttons.addWidget(username_button)
        buttons.addWidget(password_button)
        buttons.addStretch(1)
        layout.addLayout(buttons)

        self.status = QLabel("")
        layout.addWidget(self.status)
        layout.addStretch(1)
        return tab

    def alterar_email(self):
        novo_email = self.email_input.text().strip()
        if not novo_email:
            self.show_error("Informe o novo email.")
            return
        mensagem = self.context.user_profile_controller.alterar_email(
            self.context.username,
            novo_email,
        )
        self.status.setText(mensagem)

    def alterar_username(self):
        novo_username = self.username_input.text().strip()
        if not novo_username:
            self.show_error("Informe o novo username.")
            return
        username_anterior = self.context.username
        mensagem = self.context.user_profile_controller.alterar_nome(
            username_anterior,
            novo_username,
        )
        self.status.setText(mensagem)
        if mensagem == "Username atualizado":
            self.context.username = novo_username
            self.on_username_changed(novo_username)

    def alterar_senha(self):
        senha_atual = self.current_password_input.text().strip()
        nova_senha = self.new_password_input.text().strip()
        if not senha_atual or not nova_senha:
            self.show_error("Informe a senha atual e a nova senha.")
            return
        mensagem = self.context.user_profile_controller.alterar_senha(
            self.context.username,
            senha_atual,
            nova_senha,
        )
        self.status.setText(mensagem)
