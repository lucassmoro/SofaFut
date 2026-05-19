import unittest

from sofafut.demo_console_app import build_console_app
from sofafut.models.clube import Clube
from sofafut.models.estatistica import EstatisticaJogador
from sofafut.models.jogador import JogadorLinha


class MvcFlowTest(unittest.TestCase):
    def test_fluxo_basico_mvc(self) -> None:
        app = build_console_app()
        usuario = app.auth_controller.registrar("Ana", "ana@email.com", "123456")
        clube = Clube(nome="Sofa FC")
        jogador = JogadorLinha(nome="Atleta", valor_mercado=10.0, clube=clube, posicao="ATA")

        time = app.mercado_controller.comprar(usuario.id, jogador)
        escalacao = app.escalacao_controller.criar_escalacao(usuario.id, rodada=1, formacao="4-3-3")
        app.escalacao_controller.escalar_jogador(escalacao.id, jogador, posicao="ATA", capitao=True)

        pontuacao = app.estatisticas_controller.calcular_pontuacao(
            escalacao.id,
            [EstatisticaJogador(jogador_id=jogador.id, atuou=True, gols=1, assistencias=1)],
        )

        ranking = app.ranking_controller.ranking()

        self.assertEqual(time.patrimonio, 90.0)
        self.assertEqual(pontuacao.pontos, 26.0)
        self.assertEqual(ranking[0].usuario_id, usuario.id)


if __name__ == "__main__":
    unittest.main()
