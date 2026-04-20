from models.client import Client
from repositories.users_database import UserDataBase
import auth_service

"""Essa classe é a responsavel por executar a edicao dos dados.
Apesar de chamar os metodos de edicao de dados da classe Cliente
ele é responsavel por validar senhas e se o usuario esta presente na base de dados
antes de chamar os metodos de edicao de dados
"""
class UserService:

    def __init__(self, user_database : UserDataBase):
        self.user_database = user_database

    def alterar_email(self, username, novo_email):
        user = self.user_database.search_user(username)

        if user is None:
            return "Usuario nao encontrado"
        
        user.alterar_email(novo_email)
        return "Email atualizado"
    
    def alterar_nome(self, username, novo_username):
        user = self.user_database.search_user(username)

        if user is None:
            return "Usuario nao encontrado"
        
        user.alterar_nome(novo_username)

        return "Username atualizado"
    
    def alterar_senha(self, username, senha_atual, nova_senha):

        user = self.user_database.search_user(username)

        if user is None: 
            return "Usuario nao encontrado"
        
        if user.verificar_senha(senha_atual):
            user.alterar_senha(nova_senha)
        else: 
            return "Senha incorreta"