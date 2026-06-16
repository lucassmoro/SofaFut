from dataclasses import dataclass

from sofafut.controllers.escalacao_controller import EscalacaoController
from sofafut.controllers.estatisticas_controller import EstatisticasController
from sofafut.controllers.mercado_controller import MercadoController
from sofafut.controllers.perfil_controller import PerfilController
from sofafut.controllers.ranking_controller import RankingController
from sofafut.repositories.memory_repository import MemoryRepository
from sofafut.services.demo_auth_service import DemoAuthService
from sofafut.services.escalacao_service import EscalacaoService
from sofafut.services.estatistica_service import EstatisticaService
from sofafut.services.mercado_service import MercadoService
from sofafut.services.ranking_service import RankingService


@dataclass
class ConsoleApp:
    auth_controller: object
    perfil_controller: PerfilController
    mercado_controller: MercadoController
    escalacao_controller: EscalacaoController
    estatisticas_controller: EstatisticasController
    ranking_controller: RankingController
    usuarios: MemoryRepository
    times: MemoryRepository
    escalacoes: MemoryRepository


class DemoAuthController:
    def __init__(self, auth_service: DemoAuthService) -> None:
        self.auth_service = auth_service

    def registrar(self, nome: str, email: str, senha: str):
        return self.auth_service.registrar(nome, email, senha)

    def autenticar(self, email: str, senha: str):
        return self.auth_service.autenticar(email, senha)


def build_console_app() -> ConsoleApp:
    usuarios = MemoryRepository()
    times = MemoryRepository()
    escalacoes = MemoryRepository()

    auth_service = DemoAuthService(usuarios, times)
    mercado_service = MercadoService(times)
    escalacao_service = EscalacaoService(escalacoes, times)
    estatistica_service = EstatisticaService(escalacoes, times)
    ranking_service = RankingService(times)

    return ConsoleApp(
        auth_controller=DemoAuthController(auth_service),
        perfil_controller=PerfilController(auth_service),
        mercado_controller=MercadoController(mercado_service),
        escalacao_controller=EscalacaoController(escalacao_service),
        estatisticas_controller=EstatisticasController(estatistica_service),
        ranking_controller=RankingController(ranking_service),
        usuarios=usuarios,
        times=times,
        escalacoes=escalacoes,
    )
