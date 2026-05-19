from sofafut.controllers.demo_auth_controller import DemoAuthController
from sofafut.controllers.escalacao_controller import EscalacaoController
from sofafut.controllers.estatisticas_controller import EstatisticasController
from sofafut.controllers.mercado_controller import MercadoController
from sofafut.controllers.perfil_controller import PerfilController
from sofafut.controllers.ranking_controller import RankingController
from sofafut.models.clube import Clube
from sofafut.models.jogador import JogadorLinha
from sofafut.repositories.memory_repository import MemoryRepository
from sofafut.services.demo_auth_service import DemoAuthService
from sofafut.services.escalacao_service import EscalacaoService
from sofafut.services.estatistica_service import EstatisticaService
from sofafut.services.mercado_service import MercadoService
from sofafut.services.ranking_service import RankingService
from sofafut.views.console_view import ConsoleView


class SofaFutConsoleApp:
    def __init__(
        self,
        auth_controller: DemoAuthController,
        perfil_controller: PerfilController,
        mercado_controller: MercadoController,
        escalacao_controller: EscalacaoController,
        estatisticas_controller: EstatisticasController,
        ranking_controller: RankingController,
        view: ConsoleView,
    ) -> None:
        self.auth_controller = auth_controller
        self.perfil_controller = perfil_controller
        self.mercado_controller = mercado_controller
        self.escalacao_controller = escalacao_controller
        self.estatisticas_controller = estatisticas_controller
        self.ranking_controller = ranking_controller
        self.view = view

    def run_demo(self) -> None:
        usuario = self.auth_controller.registrar("Vini", "vini@email.com", "123456")
        clube = Clube(nome="Sofa FC", cidade="Sao Paulo", estadio="Arena Sofa")
        jogador = JogadorLinha(
            nome="Camisa 10",
            nacionalidade="Brasil",
            numero_camisa=10,
            valor_mercado=25.0,
            clube=clube,
            posicao="MEI",
        )

        self.mercado_controller.comprar(usuario.id, jogador)
        escalacao = self.escalacao_controller.criar_escalacao(usuario.id, rodada=1, formacao="4-3-3")
        self.escalacao_controller.escalar_jogador(escalacao.id, jogador, posicao="MEI", titular=True, capitao=True)

        ranking = self.ranking_controller.ranking()
        self.view.show_message("SofaFut MVC inicializado.")
        self.view.show_ranking(ranking)


def build_console_app() -> SofaFutConsoleApp:
    usuario_repository = MemoryRepository()
    time_repository = MemoryRepository()
    escalacao_repository = MemoryRepository()

    auth_service = DemoAuthService(usuario_repository, time_repository)
    mercado_service = MercadoService(time_repository)
    escalacao_service = EscalacaoService(escalacao_repository, time_repository)
    estatistica_service = EstatisticaService(escalacao_repository, time_repository)
    ranking_service = RankingService(time_repository)
    view = ConsoleView()

    return SofaFutConsoleApp(
        auth_controller=DemoAuthController(auth_service),
        perfil_controller=PerfilController(auth_service),
        mercado_controller=MercadoController(mercado_service),
        escalacao_controller=EscalacaoController(escalacao_service),
        estatisticas_controller=EstatisticasController(estatistica_service),
        ranking_controller=RankingController(ranking_service),
        view=view,
    )
