from models.client import Client

class UserDataBase:

    def __init__(self):

        self.__usuarios_cadastrados = {}

    def add_user(self, user : Client):

        self.__usuarios_cadastrados[user.nome] = user

    def search_user(self, username):
        return self.__usuarios_cadastrados.get(username)