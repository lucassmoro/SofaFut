import unittest

from src.models.market_transaction import TipoTransacao
from src.models.player import Player
from src.models.user import User
from src.services.market_service import (
    ComprarJogadorCommand,
    MarketService,
    VenderJogadorCommand,
)


class MarketServiceCommandTest(unittest.TestCase):
    def setUp(self):
        self.service = MarketService()
        self.user = User(
            nome="usuario",
            cpf="000",
            email="usuario@email.com",
            senha="senha",
            pontuacao=0,
            saldo=0,
            nome_team_fantasy="Usuario FC",
        )

    def jogador(self, api_id=1, nome="Jogador", valor=10.0):
        return Player(
            nome=nome,
            posicao="atacante",
            api_id=api_id,
            nome_time="Time",
            valor_mercado=valor,
        )

    def test_comprar_comando_debita_patrimonio_adiciona_elenco_e_registra_transacao(self):
        jogador = self.jogador(valor=25.0)

        team = self.service.executar_comando(ComprarJogadorCommand(self.user, jogador))

        self.assertEqual(team.patrimonio, 85.0)
        self.assertEqual(team.elenco, [jogador])
        self.assertEqual(len(team.transacoes), 1)
        self.assertEqual(team.transacoes[0].tipo, TipoTransacao.COMPRA)
        self.assertEqual(team.transacoes[0].valor, 25.0)
        self.assertEqual(team.transacoes[0].patrimonio_apos, 85.0)

    def test_comprar_com_saldo_insuficiente_nao_altera_estado(self):
        jogador = self.jogador(valor=120.0)

        with self.assertRaisesRegex(ValueError, "Saldo insuficiente"):
            self.service.comprar(self.user, jogador)

        self.assertEqual(self.user.team_fantasy.patrimonio, 110.0)
        self.assertEqual(self.user.team_fantasy.elenco, [])
        self.assertEqual(self.user.team_fantasy.transacoes, [])

    def test_comprar_jogador_duplicado_falha(self):
        jogador = self.jogador(api_id=7, nome="Duplicado")
        self.service.comprar(self.user, jogador)

        with self.assertRaisesRegex(ValueError, "Jogador ja esta no elenco"):
            self.service.comprar(self.user, self.jogador(api_id=7, nome="Duplicado"))

        self.assertEqual(len(self.user.team_fantasy.elenco), 1)
        self.assertEqual(len(self.user.team_fantasy.transacoes), 1)

    def test_vender_comando_remove_jogador_credita_patrimonio_e_registra_transacao(self):
        jogador = self.jogador(valor=30.0)
        self.service.comprar(self.user, jogador)

        team = self.service.executar_comando(VenderJogadorCommand(self.user, jogador))

        self.assertEqual(team.patrimonio, 110.0)
        self.assertEqual(team.elenco, [])
        self.assertEqual(len(team.transacoes), 2)
        self.assertEqual(team.transacoes[-1].tipo, TipoTransacao.VENDA)
        self.assertEqual(team.transacoes[-1].valor, 30.0)
        self.assertEqual(team.transacoes[-1].patrimonio_apos, 110.0)

    def test_vender_jogador_fora_do_elenco_falha(self):
        jogador = self.jogador()

        with self.assertRaisesRegex(ValueError, "Jogador nao pertence ao elenco"):
            self.service.vender(self.user, jogador)

        self.assertEqual(self.user.team_fantasy.patrimonio, 110.0)
        self.assertEqual(self.user.team_fantasy.elenco, [])
        self.assertEqual(self.user.team_fantasy.transacoes, [])

    def test_mercado_fechado_bloqueia_compra_e_venda(self):
        jogador = self.jogador()
        self.assertTrue(self.service.mercado_esta_aberto())
        self.service.fechar_mercado()
        self.assertFalse(self.service.mercado_esta_aberto())

        with self.assertRaisesRegex(ValueError, "Mercado fechado"):
            self.service.comprar(self.user, jogador)

        with self.assertRaisesRegex(ValueError, "Mercado fechado"):
            self.service.vender(self.user, jogador)

        self.assertEqual(self.user.team_fantasy.patrimonio, 110.0)
        self.assertEqual(self.user.team_fantasy.elenco, [])
        self.assertEqual(self.user.team_fantasy.transacoes, [])

        self.service.abrir_mercado()
        self.assertTrue(self.service.mercado_esta_aberto())


if __name__ == "__main__":
    unittest.main()
