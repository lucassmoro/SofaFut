import hashlib
import errno

class Client:
    def __init__(self, nome, cpf, email, senha)

        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.__senha = self._generate_hash(senha)

    def _generate_hash(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def verificar_senha(self, tentativa_senha):
        return self._generate_hash(tentativa_senha) == self.__senha
    

class UserDataBase:

    def __init__(self):

        self.__usuarios_cadastrados = {}

    def add_user(self, user : Client):

        self.__usuarios_cadastrados[user.nome] = user

    def search_user(self, username):
        return self.__usuarios_cadastrados.get(username)
    

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

    
