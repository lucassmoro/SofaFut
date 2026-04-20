import hashlib
import errno
import os, pathlib
from external import sofascore_api
from repositories.users_database import UserDataBase

"""
Classe do cliente. Os metodos de alterar dados (email, nome e senha) nao devem
ser chamados sozinhos. Quem faz as verificacoes antes de chamar é a classe UserService
"""

class Client:
    def __init__(self, nome, cpf, email, senha, pontuacao, saldo):

        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.__senha = self._generate_hash(senha)
        self.pontuacao = 0
        self.saldo = 0

    def _generate_hash(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def verificar_senha(self, tentativa_senha):
        return self._generate_hash(tentativa_senha) == self.__senha
    
    def alterar_email(self, novo_email):
        self.email = novo_email
    
    def alterar_nome(self, novo_nome):
        self.nome = novo_nome

    def alterar_senha(self, nova_senha):
        self.__senha = self._generate_hash(nova_senha)
    


    
