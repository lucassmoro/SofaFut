import tempfile
import unittest
from pathlib import Path

from sofafut.controllers.auth_controller import AuthController
from sofafut.controllers.main_controller import MainController
from sofafut.demo_console_app import build_console_app
from sofafut.models.clube import Clube
from sofafut.models.estatistica import EstatisticaJogador
from sofafut.models.jogador import JogadorLinha
from sofafut.services.auth_service import AuthService
from sofafut.services.favorites_service import FavoritesService


class UseCasesTest(unittest.TestCase):
    def test_gestao_de_perfil_persistente(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = AuthService(Path(temp_dir) / "users.json")
            service.cadastrar("ana", "123456", email="ana@old.test", nome="Ana")

            user = service.atualizar_perfil("ana", nome="Ana Maria", email="ana@test.dev", novo_username="anam")

            self.assertEqual(user.username, "anam")
            self.assertEqual(
                service.perfil("anam"),
                {"username": "anam", "nome": "Ana Maria", "email": "ana@test.dev"},
            )
            self.assertEqual(service.login("anam", "123456").username, "anam")

    def test_favoritar_clubes_e_atletas(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = FavoritesService(Path(temp_dir) / "favorites.json")

            service.save_favorites("vini", {"Flamengo"})
            service.add_favorite("vini", "atleta", "jogador-1")
            service.add_favorite("vini", "atleta", "jogador-2")
            service.remove_favorite("vini", "atleta", "jogador-1")

            self.assertEqual(service.get_favorites("vini"), {"Flamengo"})
            self.assertEqual(service.get_favorites_by_type("vini", "atleta"), {"jogador-2"})

    def test_mercado_valida_saldo_duplicidade_e_fechamento(self) -> None:
        app = build_console_app()
        usuario = app.auth_controller.registrar("Ana", "ana@email.com", "123456")
        jogador = JogadorLinha(nome="Atleta", valor_mercado=40.0)

        time = app.mercado_controller.comprar(usuario.id, jogador)

        self.assertEqual(time.patrimonio, 60.0)
        with self.assertRaisesRegex(ValueError, "ja pertence"):
            app.mercado_controller.comprar(usuario.id, jogador)

        app.mercado_controller.fechar_mercado()
        with self.assertRaisesRegex(ValueError, "Mercado fechado"):
            app.mercado_controller.vender(usuario.id, jogador.id)

    def test_escalacao_exige_capitao_e_quantidade_da_formacao(self) -> None:
        app = build_console_app()
        usuario = app.auth_controller.registrar("Ana", "ana@email.com", "123456")
        clube = Clube(nome="Sofa FC")
        jogadores = [
            JogadorLinha(nome=f"Atleta {indice}", valor_mercado=1.0, clube=clube, posicao="LIN")
            for indice in range(11)
        ]
        for jogador in jogadores:
            app.mercado_controller.comprar(usuario.id, jogador)

        escalacao = app.escalacao_controller.criar_escalacao(usuario.id, rodada=1, formacao="4-3-3")
        for jogador in jogadores[:10]:
            app.escalacao_controller.escalar_jogador(escalacao.id, jogador, posicao="LIN")

        with self.assertRaisesRegex(ValueError, "Escolha um capitao"):
            app.escalacao_controller.bloquear(escalacao.id)

        app.escalacao_controller.escolher_capitao(escalacao.id, jogadores[0].id)
        with self.assertRaisesRegex(ValueError, "Escalacao incompleta"):
            app.escalacao_controller.bloquear(escalacao.id)

        app.escalacao_controller.escalar_jogador(escalacao.id, jogadores[10], posicao="GOL")
        bloqueada = app.escalacao_controller.bloquear(escalacao.id)

        self.assertTrue(bloqueada.bloqueada)

    def test_estatisticas_filtram_comparam_verificam_atuacao_e_pontuam_uma_vez(self) -> None:
        app = build_console_app()
        usuario = app.auth_controller.registrar("Ana", "ana@email.com", "123456")
        jogador_a = JogadorLinha(nome="Artilheiro", valor_mercado=10.0, posicao="ATA")
        jogador_b = JogadorLinha(nome="Garcom", valor_mercado=10.0, posicao="MEI")
        app.mercado_controller.comprar(usuario.id, jogador_a)
        app.mercado_controller.comprar(usuario.id, jogador_b)
        escalacao = app.escalacao_controller.criar_escalacao(usuario.id, rodada=1, formacao="1")
        app.escalacao_controller.escalar_jogador(escalacao.id, jogador_a, posicao="ATA", capitao=True)
        app.escalacao_controller.escalar_jogador(escalacao.id, jogador_b, posicao="MEI", titular=False)
        estatisticas = [
            EstatisticaJogador(jogador_id=jogador_a.id, atuou=True, gols=2, assistencias=1),
            EstatisticaJogador(jogador_id=jogador_b.id, atuou=True, gols=0, assistencias=2),
        ]

        filtradas = app.estatisticas_controller.filtrar_atletas(estatisticas, "gols", minimo=1)
        comparativo = app.estatisticas_controller.comparar_atletas(jogador_a.id, jogador_b.id, estatisticas)
        pontuacao = app.estatisticas_controller.calcular_pontuacao(escalacao.id, estatisticas)

        self.assertEqual([item.jogador_id for item in filtradas], [jogador_a.id])
        self.assertTrue(app.estatisticas_controller.verificar_atuacao(jogador_b.id, estatisticas))
        self.assertEqual(comparativo["assistencias"][jogador_b.id], 2)
        self.assertEqual(pontuacao.pontos, 47.0)
        with self.assertRaisesRegex(ValueError, "ja calculada"):
            app.estatisticas_controller.calcular_pontuacao(escalacao.id, estatisticas)

    def test_ranking_e_historico_de_evolucao(self) -> None:
        app = build_console_app()
        usuario = app.auth_controller.registrar("Ana", "ana@email.com", "123456")
        jogador = JogadorLinha(nome="Atleta", valor_mercado=10.0, posicao="ATA")
        app.mercado_controller.comprar(usuario.id, jogador)
        escalacao = app.escalacao_controller.criar_escalacao(usuario.id, rodada=1, formacao="1")
        app.escalacao_controller.escalar_jogador(escalacao.id, jogador, posicao="ATA", capitao=True)
        app.estatisticas_controller.calcular_pontuacao(
            escalacao.id,
            [EstatisticaJogador(jogador_id=jogador.id, atuou=True, gols=1)],
        )

        ranking = app.ranking_controller.ranking()
        historico = app.ranking_controller.historico_evolucao(usuario.id)

        self.assertEqual(ranking[0].usuario_id, usuario.id)
        self.assertEqual(historico, [{"rodada": 1, "pontos": 16.0, "patrimonio": 90.0}])

    def test_main_controller_expõe_fluxos_usados_pela_ui(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            auth = AuthController(AuthService(Path(temp_dir) / "users.json"))
            auth.cadastrar("ui", "123456", email="ui@old.test", nome="UI")
            favorites = FavoritesService(Path(temp_dir) / "favorites.json")
            controller = MainController("ui", favorites_service=favorites, auth_controller=auth)

            controller.save_favorites({"Flamengo"})
            profile = controller.update_profile("Usuario UI", "ui@test.dev", "ui_user")
            players = controller.market_players()[:2]

            controller.add_favorite_athlete(players[0].player_id)
            controller.set_formation("1")
            for player in players:
                controller.buy_player(player.player_id)
                controller.add_lineup_player(player.player_id)
            controller.choose_captain(players[0].player_id)
            controller.lock_lineup()
            result = controller.calculate_round_points()
            filtered_stats = controller.stat_rows("Gols", "1")
            comparison = controller.compare_players(players[0].player_id, players[1].player_id)
            ranking = controller.ranking_rows()
            history = controller.history_rows()

            self.assertEqual(profile["username"], "ui_user")
            self.assertEqual(controller.favorites(), {"Flamengo"})
            self.assertIn(players[0].player_id, controller.favorite_athletes())
            self.assertIn("Rodada 1", result)
            self.assertEqual(len(history), 1)
            self.assertEqual(controller.lineup_players(), [])
            self.assertTrue(all(stat.goals >= 1 for stat in filtered_stats))
            self.assertIn(players[0].name, comparison)
            self.assertTrue(any(row.username == "ui_user" for row in ranking))


if __name__ == "__main__":
    unittest.main()
