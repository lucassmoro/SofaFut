import unittest

from src.models.user import User
from src.repositories.users_database import UserDataBase
from src.services.session import Session
from src.services.user_service import UserService


class UserServiceTemplateTest(unittest.TestCase):
    def setUp(self):
        self.database = UserDataBase()
        self.session = Session()
        self.service = UserService(self.database, self.session)
        self.user = User(
            nome="usuario",
            cpf="000",
            email="usuario@email.com",
            senha="senha",
            pontuacao=0,
            saldo=0,
            nome_team_fantasy="Usuario FC",
        )
        self.database.add_user(self.user)
        self.session.login(self.user)

    def test_alterar_email_com_usuario_logado(self):
        mensagem = self.service.alterar_email("usuario", "novo@email.com")

        self.assertEqual(mensagem, "Email atualizado")
        self.assertEqual(self.user.email, "novo@email.com")

    def test_alterar_nome_com_usuario_logado(self):
        mensagem = self.service.alterar_nome("usuario", "novo_usuario")

        self.assertEqual(mensagem, "Username atualizado")
        self.assertIsNone(self.database.search_user("usuario"))
        self.assertIs(self.database.search_user("novo_usuario"), self.user)
        self.assertEqual(self.user.nome, "novo_usuario")

    def test_alterar_senha_com_senha_atual_correta(self):
        mensagem = self.service.alterar_senha("usuario", "senha", "nova_senha")

        self.assertEqual(mensagem, "Senha atualizada")
        self.assertTrue(self.user.verificar_senha("nova_senha"))

    def test_alterar_senha_com_senha_incorreta(self):
        mensagem = self.service.alterar_senha("usuario", "errada", "nova_senha")

        self.assertEqual(mensagem, "Senha incorreta")
        self.assertTrue(self.user.verificar_senha("senha"))

    def test_alteracao_sem_sessao_logada_falha(self):
        self.session.logout()

        with self.assertRaisesRegex(PermissionError, "Sem permissao"):
            self.service.alterar_email("usuario", "novo@email.com")

        self.assertEqual(self.user.email, "usuario@email.com")

    def test_alteracao_de_usuario_inexistente_retorna_mensagem(self):
        usuario_sem_banco = User(
            nome="fantasma",
            cpf="111",
            email="fantasma@email.com",
            senha="senha",
            pontuacao=0,
            saldo=0,
            nome_team_fantasy="Fantasma FC",
        )
        self.session.login(usuario_sem_banco)

        mensagem = self.service.alterar_email("fantasma", "novo@email.com")

        self.assertEqual(mensagem, "Usuario nao encontrado")


if __name__ == "__main__":
    unittest.main()
