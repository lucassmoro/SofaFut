import hashlib
import errno
import os, pathlib
import SofaFut.src.external.sofascore_api as sofascore_api
from repositories.users_database import UserDataBase

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
    


    
