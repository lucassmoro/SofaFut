from repositories.users_database import UserDataBase
from models.client import Client

class AuthService: 

    def __init__(self, user_database : UserDataBase):

        self.user_database = user_database

    def cadastrar(self, username, cpf, email, senha):

        if self.user_database.search_user(username) is None:
            
            self.user_database.add_user(Client(username, cpf, email, senha))

        else:
            print("Usuario com esse username ja cadastrado")

        return "Usuario cadastrado"
    
    def login(self, username, senha):

        if self.user_database.get(username) is not None:

            user = self.user_database.search_user(username)

            if user.verificar_senha(senha):

                return "Usuario Loggado" 
            
            else:
                print("Senha invalida")

        else: 
            print("Usuario nao encontrado")
