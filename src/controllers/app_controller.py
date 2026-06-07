from src.external.api_client import SofaScoreApiClient
from src.models.estatistics import Estatisticas
from src.models.player_fantasy import PlayerFantasy
from src.repositories.players_repository import PlayerRepository
from src.repositories.rounds_repository import RoundRepository
from src.repositories.users_database import UserDataBase
from src.services.auth_service import AuthService
from src.services.match_service import MatchService
from src.services.player_service import PlayerService
from src.services.session import Session
from src.services.team_fantasy_service import TeamFantasyService
from src.services.user_service import UserService


class AppController:
    """Ponto de entrada para comandos vindos da interface visual."""

    def __init__(
        self,
        user_database: UserDataBase | None = None,
        player_repository: PlayerRepository | None = None,
        round_repository: RoundRepository | None = None,
        sofa_api: SofaScoreApiClient | None = None,
        session: Session | None = None,
    ):
        self.session = session or Session()
        self.user_database = user_database or UserDataBase()
        self.player_repository = player_repository or PlayerRepository(api_client=sofa_api)
        self.round_repository = round_repository or RoundRepository()

        self.auth_service = AuthService(self.user_database, self.session)
        self.user_service = UserService(self.user_database, self.session)
        self.team_fantasy_service = TeamFantasyService()
        self.player_service = PlayerService(self.player_repository)
        self.match_service = MatchService(sofa_api or SofaScoreApiClient())

    def cadastrar_usuario(
        self,
        username: str,
        cpf: str,
        email: str,
        senha: str,
        nome_team_fantasy: str | None = None,
    ):
        return self.auth_service.cadastrar(
            username=username,
            cpf=cpf,
            email=email,
            senha=senha,
            nome_team_fantasy=nome_team_fantasy,
        )

    def login(self, username: str, senha: str):
        return self.auth_service.login(username, senha)

    def logout(self):
        self.session.logout()
        return "Usuario deslogado"

    def usuario_logado(self):
        return self.session.current_user

    def alterar_email(self, username: str, novo_email: str):
        return self.user_service.alterar_email(username, novo_email)

    def alterar_nome(self, username: str, novo_username: str):
        return self.user_service.alterar_nome(username, novo_username)

    def alterar_senha(self, username: str, senha_atual: str, nova_senha: str):
        return self.user_service.alterar_senha(username, senha_atual, nova_senha)

    def listar_jogadores(self, criterio: Estatisticas | str | None = None):
        if criterio is None:
            return self.player_repository.listar_jogadores()

        if isinstance(criterio, str):
            criterio = Estatisticas[criterio.upper()]

        return self.player_service.listar_jogadores_ordenados(criterio)

    def montar_escalacao(
        self,
        username: str,
        rodada: int,
        jogadores: list[PlayerFantasy],
    ):
        user = self._buscar_usuario_autorizado(username)
        return self.team_fantasy_service.montar_escalacao(user, rodada, jogadores)

    def executar_rodada(
        self,
        username: str,
        rodada: int,
        jogadores: list[PlayerFantasy],
    ):
        user = self._buscar_usuario_autorizado(username)
        self.team_fantasy_service.executar_rodada(
            user=user,
            rodada=rodada,
            jogadores=jogadores,
            rodadas_repo=self.round_repository,
        )
        return user.pontuacao

    def adicionar_rodada(self, rodada):
        self.round_repository.adicionar_rodada(rodada)
        return rodada

    def listar_rodadas(self):
        return self.round_repository.listar_rodadas()

    def buscar_partida(self, event_id: int):
        return self.match_service.get_match_info(event_id)

    def gerar_ranking_usuarios(self):
        return self.user_service.gerar_ranking_usuarios()

    def exibir_ranking_usuarios(self):
        ranking = self.gerar_ranking_usuarios()
        return self.user_service.formatar_ranking_usuarios(ranking)

    def gerar_historico_pontuacao_usuario(self, username: str):
        return self.user_service.gerar_historico_pontuacao_usuario(username)

    def exibir_historico_pontuacao_usuario(self, username: str):
        historico = self.gerar_historico_pontuacao_usuario(username)
        return self.user_service.formatar_historico_pontuacao_usuario(historico)

    def _buscar_usuario_autorizado(self, username: str):
        if not self.session.is_logged(username):
            raise PermissionError("Sem permissao")

        user = self.user_database.search_user(username)
        if user is None:
            raise ValueError("Usuario nao encontrado")

        return user
