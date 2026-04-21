from src.models.client import Client

"""
Classe que controla o usuario logado no sistema
"""


class Session:

    def __init__(self):
        self.current__user = None

    def login(self, user : Client):
        self.current__user = user

    def logout(self):
        self.current__user = None

    def is_logged(self, username):
        return self.current__user is not None and self.current__user.nome == username
