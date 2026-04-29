from lineup import Lineup
from client import Client

class TeamFantasy():

    def __init__(self, nome, escalacoes : Lineup.jogadores, dono_user : Client.nome):

        self.__nome = nome
        self.__escalacoes = escalacoes
        self.__dono_user = dono_user

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, nome):
        self.__nome = nome

    @property
    def escalacoes(self):
        return self.__escalacoes

    @escalacoes.setter
    def escalacoes(self, escalacoes):
        self.__escalacoes = escalacoes

    @property
    def dono_user(self):
        return self.__dono_user

    @dono_user.setter
    def dono_user(self, dono_user):
        self.__dono_user = dono_user