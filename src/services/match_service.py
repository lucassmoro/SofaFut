import json
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

from src.external.api_client import SofaScoreApiClient
from src.external.api_football_client import ApiFootballClient
from src.external.api_football_client import ApiFootballRateLimitError
from src.models.club import Club
from src.models.match import Match
from src.models.player import Player
from src.models.player_match import MatchPlayerStats
from src.models.rounds import Round

'''
Classe que vai chamar a API
'''


class MatchService():

    CACHE_DIR = Path("data/api_football")

    def __init__(
        self,
        sofa_api: SofaScoreApiClient | None = None,
        api_football: ApiFootballClient | None = None,
    ):
        self.sofa_api = sofa_api
        self.api_football = api_football

    def get_match_info(self, event_id):
        if self.sofa_api is None:
            raise ValueError("SofaScoreApiClient nao configurado")

        evento = self.sofa_api.get_event(event_id)
        estatisticas = self.sofa_api.get_event_statistics(event_id)

        return {
            "evento": evento,
            "estatisticas": estatisticas,
        }

    def buscar_partidas_por_data(
        self,
        data,
        liga_id=None,
        temporada=None,
        time_id=None,
        status=None,
    ):
        return self._api_football().buscar_partidas_por_data(
            data=data,
            liga_id=liga_id,
            temporada=temporada,
            time_id=time_id,
            status=status,
        )

    def buscar_partidas_por_periodo(
        self,
        data_inicio,
        data_fim,
        liga_id=None,
        temporada=None,
        time_id=None,
        status=None,
    ):
        return self._api_football().buscar_partidas_por_periodo(
            data_inicio=data_inicio,
            data_fim=data_fim,
            liga_id=liga_id,
            temporada=temporada,
            time_id=time_id,
            status=status,
        )

    def buscar_partida_por_id(self, fixture_id):
        return self._api_football().buscar_partida_por_id(fixture_id)

    def buscar_estatisticas_jogadores_partida(self, fixture_id, time_id=None):
        return self._api_football().buscar_estatisticas_jogadores_partida(
            fixture_id=fixture_id,
            time_id=time_id,
        )

    def buscar_partidas_por_rodada_api_football(
        self,
        liga_id,
        temporada,
        rodada,
        status=None,
    ):
        return self._api_football().buscar_partidas_por_rodada(
            liga_id=liga_id,
            temporada=temporada,
            rodada=rodada,
            status=status,
        )

    def montar_rodada_por_fixture_api_football(
        self,
        fixture_id,
        numero_rodada,
        jogadores_escalados: list[Player],
    ):
        dados_partida = self.baixar_dados_partida_api_football(fixture_id)

        return self.montar_rodada_por_cache_api_football(
            fixture_id=fixture_id,
            numero_rodada=numero_rodada,
            jogadores_escalados=jogadores_escalados,
            dados_partida=dados_partida,
        )

    def baixar_dados_partida_api_football(self, fixture_id, usar_cache=True):
        caminho_cache = self._caminho_cache_partida(fixture_id)

        if usar_cache and caminho_cache.exists():
            return self.carregar_dados_partida_api_football(fixture_id)

        partida_api = self.buscar_partida_por_id(fixture_id)
        estatisticas_api = self.buscar_estatisticas_jogadores_partida(fixture_id)

        dados_partida = {
            "fixture_id": fixture_id,
            "partida": partida_api,
            "estatisticas_jogadores": estatisticas_api,
        }

        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with caminho_cache.open("w", encoding="utf-8") as arquivo:
            json.dump(dados_partida, arquivo, ensure_ascii=False, indent=2)

        return dados_partida

    def carregar_dados_partida_api_football(self, fixture_id):
        caminho_cache = self._caminho_cache_partida(fixture_id)

        with caminho_cache.open("r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    def listar_jogadores_disponiveis_cache_api_football(self, fixture_id):
        dados_partida = self.carregar_dados_partida_api_football(fixture_id)
        jogadores = []

        for time in dados_partida["estatisticas_jogadores"].get("response", []):
            nome_time = time.get("team", {}).get("name")

            for jogador_api in time.get("players", []):
                stats = jogador_api.get("statistics", [])
                if not stats:
                    continue

                minutos = stats[0].get("games", {}).get("minutes") or 0

                if minutos > 0:
                    jogadores.append(
                        {
                            "nome": jogador_api.get("player", {}).get("name"),
                            "time": nome_time,
                            "posicao": stats[0].get("games", {}).get("position"),
                            "idade": 0,
                            "minutos": minutos,
                        }
                    )

        return jogadores

    def baixar_dados_rodada_api_football(
        self,
        liga_id,
        temporada,
        rodada,
        status=None,
        usar_cache=True,
        max_partidas=None,
    ):
        caminho_cache = self._caminho_cache_rodada(liga_id, temporada, rodada)

        if usar_cache and caminho_cache.exists():
            dados_rodada = self.carregar_dados_rodada_api_football(
                liga_id, temporada, rodada
            )
            partidas_api = dados_rodada.get("partidas_api", {})
        else:
            partidas_api = self.buscar_partidas_por_rodada_api_football(
                liga_id=liga_id,
                temporada=temporada,
                rodada=rodada,
                status=status,
            )
            dados_rodada = {
                "liga_id": liga_id,
                "temporada": temporada,
                "rodada": rodada,
                "partidas_api": partidas_api,
                "partidas": [],
            }

        baixadas = {
            partida_cache["fixture_id"]
            for partida_cache in dados_rodada.get("partidas", [])
        }
        novas_partidas = 0

        for partida in partidas_api.get("response", []):
            fixture_id = partida["fixture"]["id"]

            if fixture_id in baixadas:
                continue

            if max_partidas is not None and novas_partidas >= max_partidas:
                break

            try:
                estatisticas_api = self.buscar_estatisticas_jogadores_partida(
                    fixture_id
                )
            except ApiFootballRateLimitError:
                self._salvar_cache_rodada(caminho_cache, dados_rodada)
                raise

            dados_rodada["partidas"].append(
                {
                    "fixture_id": fixture_id,
                    "partida": {"response": [partida]},
                    "estatisticas_jogadores": estatisticas_api,
                }
            )
            baixadas.add(fixture_id)
            novas_partidas += 1
            self._salvar_cache_rodada(caminho_cache, dados_rodada)

        self._salvar_cache_rodada(caminho_cache, dados_rodada)
        return dados_rodada

    def _salvar_cache_rodada(self, caminho_cache, dados_rodada):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with caminho_cache.open("w", encoding="utf-8") as arquivo:
            json.dump(dados_rodada, arquivo, ensure_ascii=False, indent=2)

    def carregar_dados_rodada_api_football(self, liga_id, temporada, rodada):
        caminho_cache = self._caminho_cache_rodada(liga_id, temporada, rodada)

        with caminho_cache.open("r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    def listar_jogadores_disponiveis_cache_rodada_api_football(
        self,
        liga_id,
        temporada,
        rodada,
    ):
        dados_rodada = self.carregar_dados_rodada_api_football(
            liga_id,
            temporada,
            rodada,
        )
        jogadores = []

        for dados_partida in dados_rodada.get("partidas", []):
            fixture = dados_partida["partida"]["response"][0]
            fixture_id = dados_partida["fixture_id"]
            nome_partida = fixture.get("teams", {}).get("home", {}).get("name")
            nome_partida += " x "
            nome_partida += fixture.get("teams", {}).get("away", {}).get("name")

            for time in dados_partida["estatisticas_jogadores"].get("response", []):
                nome_time = time.get("team", {}).get("name")

                for jogador_api in time.get("players", []):
                    stats = jogador_api.get("statistics", [])
                    if not stats:
                        continue

                    minutos = stats[0].get("games", {}).get("minutes") or 0

                    if minutos > 0:
                        jogadores.append(
                            {
                                "nome": jogador_api.get("player", {}).get("name"),
                                "time": nome_time,
                                "posicao": stats[0].get("games", {}).get("position"),
                                "idade": 0,
                                "minutos": minutos,
                                "fixture_id": fixture_id,
                                "partida": nome_partida,
                            }
                        )

        return jogadores

    def montar_rodada_por_cache_rodada_api_football(
        self,
        liga_id,
        temporada,
        rodada,
        numero_rodada,
        jogadores_escalados: list[Player],
    ):
        dados_rodada = self.carregar_dados_rodada_api_football(
            liga_id,
            temporada,
            rodada,
        )
        rodada_model = Round(numero_rodada)

        for dados_partida in dados_rodada.get("partidas", []):
            partida = self._converter_fixture_para_match(
                partida_api=dados_partida["partida"],
                estatisticas_api=dados_partida["estatisticas_jogadores"],
                jogadores_escalados=jogadores_escalados,
            )
            rodada_model.adicionar_partidas_rodada(partida)

        return rodada_model

    def montar_rodada_por_cache_api_football(
        self,
        fixture_id,
        numero_rodada,
        jogadores_escalados: list[Player],
        dados_partida=None,
    ):
        dados_partida = dados_partida or self.carregar_dados_partida_api_football(
            fixture_id
        )

        partida = self._converter_fixture_para_match(
            partida_api=dados_partida["partida"],
            estatisticas_api=dados_partida["estatisticas_jogadores"],
            jogadores_escalados=jogadores_escalados,
        )

        rodada = Round(numero_rodada)
        rodada.adicionar_partidas_rodada(partida)
        return rodada

    def _caminho_cache_partida(self, fixture_id):
        return self.CACHE_DIR / f"fixture_{fixture_id}.json"

    def _caminho_cache_rodada(self, liga_id, temporada, rodada):
        rodada_normalizada = self._normalizar_nome(rodada).replace(" ", "_")
        return self.CACHE_DIR / f"round_{liga_id}_{temporada}_{rodada_normalizada}.json"

    def _converter_fixture_para_match(
        self,
        partida_api,
        estatisticas_api,
        jogadores_escalados: list[Player],
    ):
        fixtures = partida_api.get("response", [])
        if not fixtures:
            raise ValueError("Partida nao encontrada na API-Football")

        fixture = fixtures[0]
        home_team = fixture["teams"]["home"]
        away_team = fixture["teams"]["away"]

        mandante = Club(home_team["name"], [], 0, 0, 0, 0)
        visitante = Club(away_team["name"], [], 0, 0, 0, 0)
        atuacoes_api = self._indexar_atuacoes_api_football(estatisticas_api)
        jogadores_partida = []

        for jogador in jogadores_escalados:
            nome_normalizado = self._normalizar_nome(jogador.nome)
            jogador_api = atuacoes_api.get(nome_normalizado)

            if jogador_api is None:
                jogador_api = self._buscar_atuacao_por_nome_aproximado(
                    nome_normalizado,
                    atuacoes_api,
                )

            jogadores_partida.append(
                self._converter_atuacao_api_football(jogador, jogador_api)
            )

        return Match(
            mandante=mandante,
            visitante=visitante,
            data=fixture["fixture"]["date"],
            jogadores_partida=jogadores_partida,
        )

    def _indexar_atuacoes_api_football(self, estatisticas_api):
        atuacoes = {}

        for time in estatisticas_api.get("response", []):
            for jogador_api in time.get("players", []):
                nome = jogador_api.get("player", {}).get("name")
                if nome:
                    atuacoes[self._normalizar_nome(nome)] = jogador_api

        return atuacoes

    def _converter_atuacao_api_football(self, jogador, jogador_api):
        if jogador_api is None:
            return MatchPlayerStats(
                jogador=jogador,
                atuou=False,
                titular=False,
                gols=0,
                assistencias=0,
                cartoes_amarelos=0,
                cartoes_vermelhos=0,
                faltas=0,
                gols_sofridos=0,
            )

        stats = jogador_api.get("statistics", [{}])[0]
        games = stats.get("games", {})
        goals = stats.get("goals", {})
        cards = stats.get("cards", {})
        fouls = stats.get("fouls", {})

        minutos = games.get("minutes") or 0

        return MatchPlayerStats(
            jogador=jogador,
            atuou=minutos > 0,
            titular=not games.get("substitute", True),
            gols=goals.get("total") or 0,
            assistencias=goals.get("assists") or 0,
            cartoes_amarelos=cards.get("yellow") or 0,
            cartoes_vermelhos=cards.get("red") or 0,
            faltas=fouls.get("committed") or 0,
            gols_sofridos=goals.get("conceded") or 0,
        )

    def _normalizar_nome(self, nome):
        sem_acento = unicodedata.normalize("NFKD", nome)
        sem_acento = "".join(
            caractere
            for caractere in sem_acento
            if not unicodedata.combining(caractere)
        )
        return sem_acento.casefold().strip()

    def _buscar_atuacao_por_nome_aproximado(self, nome_normalizado, atuacoes):
        melhor_nome = None
        melhor_score = 0

        for nome_api in atuacoes:
            score = SequenceMatcher(None, nome_normalizado, nome_api).ratio()

            if score > melhor_score:
                melhor_nome = nome_api
                melhor_score = score

        if melhor_score >= 0.86:
            return atuacoes[melhor_nome]

        return None

    def _api_football(self):
        if self.api_football is None:
            self.api_football = ApiFootballClient()

        return self.api_football
