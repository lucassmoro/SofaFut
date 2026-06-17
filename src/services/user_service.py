from abc import ABC, abstractmethod

from src.models.user import User
from src.models.lineup import Lineup
from src.repositories.users_database import UserDataBase
from src.services.session import Session
from src.services.team_fantasy_service import TeamFantasyService


class ProfileUpdateTemplate(ABC):
    def __init__(self, service, username):
        self.service = service
        self.username = username

    def executar(self):
        self.service._verificar_permissao(self.username)
        user = self.service.user_database.search_user(self.username)

        if user is None:
            return "Usuario nao encontrado"

        return self._aplicar(user)

    @abstractmethod
    def _aplicar(self, user):
        pass


class AlterarEmailTemplate(ProfileUpdateTemplate):
    def __init__(self, service, username, novo_email):
        super().__init__(service, username)
        self.novo_email = novo_email

    def _aplicar(self, user):
        user.alterar_email(self.novo_email)
        return "Email atualizado"


class AlterarNomeTemplate(ProfileUpdateTemplate):
    def __init__(self, service, username, novo_username):
        super().__init__(service, username)
        self.novo_username = novo_username

    def _aplicar(self, user):
        return self.service.user_database.update_username(
            self.username,
            self.novo_username,
        )


class AlterarSenhaTemplate(ProfileUpdateTemplate):
    def __init__(self, service, username, senha_atual, nova_senha):
        super().__init__(service, username)
        self.senha_atual = senha_atual
        self.nova_senha = nova_senha

    def _aplicar(self, user):
        if user.verificar_senha(self.senha_atual):
            user.alterar_senha(self.nova_senha)
            return "Senha atualizada"

        return "Senha incorreta"


class UserService:

    def __init__(self, user_database : UserDataBase, session : Session):
        self.user_database = user_database
        self.session = session

    def _verificar_permissao(self, username):
        if not self.session.is_logged(username):
            raise PermissionError("Sem permissao")
        

    def alterar_email(self, username, novo_email):
        return AlterarEmailTemplate(self, username, novo_email).executar()
    
    def alterar_nome(self, username, novo_username):
        return AlterarNomeTemplate(self, username, novo_username).executar()
    
    def alterar_senha(self, username, senha_atual, nova_senha):
        return AlterarSenhaTemplate(self, username, senha_atual, nova_senha).executar()
        
    def atribuir_pontuacao(self, username, pontuacao):

        user = self.user_database.search_user(username)

        if user is not None:
            user.pontuacao += pontuacao
            return "Pontuacao atualizada"

        else: 
            return "Usuario nao encontrado"

    def gerar_ranking_usuarios(self) -> list[User]:
        ranking = self.user_database.listar_usuarios()
        ranking.sort(
            key=lambda user: (
                -user.pontuacao,
                -user.saldo,
                user.nome,
            )
        )
        return ranking

    def formatar_ranking_usuarios(self, ranking: list[User]):
        if not ranking:
            return "Ranking de usuarios vazio"

        linhas = []
        for posicao, user in enumerate(ranking, start=1):
            linhas.append(
                f"{posicao}. {user.nome} - "
                f"{user.pontuacao} pontos - saldo {user.saldo:.2f}"
            )

        return "\n".join(linhas)

    def gerar_historico_pontuacao_usuario(self, username) -> list[Lineup]:
        user = self.user_database.search_user(username)

        if user is None:
            return []

        historico = list(user.team_fantasy.escalacoes.values())
        historico.sort(key=lambda escalacao: escalacao.rodada)
        return historico

    def formatar_historico_pontuacao_usuario(
        self,
        historico: list[Lineup],
    ):
        if not historico:
            return "Historico de pontuacao vazio"

        linhas = []
        for escalacao in historico:
            linhas.append(
                f"Rodada {escalacao.rodada}: {escalacao.pontuacao} pontos"
            )

        return "\n".join(linhas)
