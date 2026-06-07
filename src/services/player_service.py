import json
from pathlib import Path

from src.external.api_football_client import ApiFootballClient
from src.external.api_football_client import ApiFootballRateLimitError
from src.models.estatistics import Estatisticas
from src.models.player import Player
from src.repositories.players_repository import PlayerRepository


class PlayerService:

    CACHE_DIR = Path("data/api_football")
    MAX_PAGINAS_PLAYERS_PLANO_GRATIS = 3

    def __init__(
        self,
        player_repository: PlayerRepository,
        api_football: ApiFootballClient | None = None,
    ):
        self.player_repository = player_repository
        self.api_football = api_football

    def listar_jogadores_ordenados(self, criterio: Estatisticas) -> list[Player]:
        jogadores = self.player_repository.listar_jogadores()
        jogadores.sort(
            key=lambda jogador: getattr(jogador, criterio.value),
            reverse=True,
        )
        return jogadores

    def carregar_jogadores_brasileirao_temporada(
        self,
        temporada,
        liga_id=71,
        usar_cache=True,
        max_paginas=None,
        paginas_por_execucao=1,
    ) -> list[Player]:
        dados = self.baixar_jogadores_liga_temporada(
            liga_id=liga_id,
            temporada=temporada,
            usar_cache=usar_cache,
            max_paginas=max_paginas,
            paginas_por_execucao=paginas_por_execucao,
        )
        jogadores = self._converter_api_football_para_players(dados)
        self.player_repository.definir_jogadores(jogadores)
        return jogadores

    def baixar_jogadores_liga_temporada(
        self,
        liga_id,
        temporada,
        usar_cache=True,
        max_paginas=None,
        paginas_por_execucao=1,
    ):
        caminho_cache = self._caminho_cache_jogadores_temporada(liga_id, temporada)
        dados = None

        if usar_cache and caminho_cache.exists():
            dados = self._carregar_cache_jogadores_temporada_ou_none(caminho_cache)

        if dados is None:
            dados = {
                "liga_id": liga_id,
                "temporada": temporada,
                "paginas_baixadas": [],
                "total_paginas": None,
                "response": [],
            }

        paginas_baixadas = set(dados.get("paginas_baixadas", []))
        pagina = self._proxima_pagina_para_baixar(dados)
        paginas_baixadas_nesta_execucao = 0

        while self._deve_baixar_pagina(dados, pagina, max_paginas):
            if paginas_baixadas_nesta_execucao >= paginas_por_execucao:
                break

            if pagina in paginas_baixadas:
                pagina += 1
                continue

            try:
                resposta = self._api_football().buscar_jogadores_liga_temporada(
                    liga_id=liga_id,
                    temporada=temporada,
                    pagina=pagina,
                )
            except ApiFootballRateLimitError:
                self._salvar_cache_jogadores_temporada(caminho_cache, dados)
                raise

            dados["response"].extend(resposta.get("response", []))
            dados["paginas_baixadas"].append(pagina)
            dados["total_paginas"] = self._inteiro_ou_none(
                resposta.get("paging", {}).get("total")
            )
            dados["ultima_pagina_baixada"] = pagina

            self._remover_jogadores_duplicados_cache(dados)
            self._salvar_cache_jogadores_temporada(caminho_cache, dados)
            paginas_baixadas_nesta_execucao += 1
            pagina += 1

        return dados

    def adicionar_jogadores_descobertos_na_rodada(self, liga_id, temporada, dados_rodada):
        caminho_cache = self._caminho_cache_jogadores_temporada(liga_id, temporada)
        dados = self._carregar_cache_jogadores_temporada_ou_none(caminho_cache)

        if dados is None:
            dados = {
                "liga_id": liga_id,
                "temporada": temporada,
                "paginas_baixadas": [],
                "total_paginas": None,
                "response": [],
            }

        total_antes = len(dados.get("response", []))
        dados["response"].extend(self._extrair_jogadores_de_dados_rodada(dados_rodada))
        self._remover_jogadores_duplicados_cache(dados)
        dados["jogadores_descobertos_por_rodada"] = True
        self._salvar_cache_jogadores_temporada(caminho_cache, dados)

        jogadores = self._converter_api_football_para_players(dados)
        self.player_repository.definir_jogadores(jogadores)
        return len(dados.get("response", [])) - total_antes

    def carregar_jogadores_temporada_cache(self, liga_id, temporada) -> list[Player]:
        caminho_cache = self._caminho_cache_jogadores_temporada(liga_id, temporada)
        dados = self._carregar_cache_jogadores_temporada_ou_none(caminho_cache)

        if dados is None:
            raise RuntimeError(
                f"Cache de jogadores da temporada esta vazio ou invalido: {caminho_cache}"
            )

        jogadores = self._converter_api_football_para_players(dados)
        self.player_repository.definir_jogadores(jogadores)
        return jogadores

    def _converter_api_football_para_players(self, dados):
        jogadores = []

        for jogador_api in dados.get("response", []):
            dados_jogador = jogador_api.get("player", {})
            estatistica = self._primeira_estatistica(jogador_api)
            dados_time = estatistica.get("team", {})
            dados_jogo = estatistica.get("games", {})

            jogadores.append(
                Player(
                    nome=dados_jogador.get("name"),
                    time=None,
                    posicao=dados_jogo.get("position") or "desconhecida",
                    idade=dados_jogador.get("age") or 0,
                    api_id=dados_jogador.get("id"),
                    nome_time=dados_time.get("name"),
                )
            )

        return jogadores

    def _extrair_jogadores_de_dados_rodada(self, dados_rodada):
        jogadores = []

        for dados_partida in dados_rodada.get("partidas", []):
            for time in dados_partida.get("estatisticas_jogadores", {}).get("response", []):
                dados_time = time.get("team", {})

                for jogador_api in time.get("players", []):
                    dados_jogador = jogador_api.get("player", {})
                    estatisticas = jogador_api.get("statistics", [])
                    dados_jogo = estatisticas[0].get("games", {}) if estatisticas else {}

                    if dados_jogador.get("id") is None:
                        continue

                    jogadores.append(
                        {
                            "player": {
                                "id": dados_jogador.get("id"),
                                "name": dados_jogador.get("name"),
                                "age": dados_jogador.get("age") or 0,
                            },
                            "statistics": [
                                {
                                    "team": {
                                        "id": dados_time.get("id"),
                                        "name": dados_time.get("name"),
                                    },
                                    "games": {
                                        "position": dados_jogo.get("position"),
                                    },
                                }
                            ],
                        }
                    )

        return jogadores

    def _primeira_estatistica(self, jogador_api):
        estatisticas = jogador_api.get("statistics", [])
        if not estatisticas:
            return {}
        return estatisticas[0]

    def _proxima_pagina_para_baixar(self, dados):
        paginas_baixadas = dados.get("paginas_baixadas", [])
        if not paginas_baixadas:
            return 1
        return max(paginas_baixadas) + 1

    def _deve_baixar_pagina(self, dados, pagina, max_paginas):
        total_paginas = self._inteiro_ou_none(dados.get("total_paginas"))
        max_paginas = self._limite_paginas_plano_gratis(max_paginas)

        if max_paginas is not None and pagina > max_paginas:
            return False

        if total_paginas is None:
            return True

        return pagina <= total_paginas

    def _limite_paginas_plano_gratis(self, max_paginas):
        if max_paginas is None:
            return self.MAX_PAGINAS_PLAYERS_PLANO_GRATIS

        return min(max_paginas, self.MAX_PAGINAS_PLAYERS_PLANO_GRATIS)

    def _inteiro_ou_none(self, valor):
        if valor is None:
            return None
        return int(valor)

    def _remover_jogadores_duplicados_cache(self, dados):
        jogadores_unicos = {}

        for jogador_api in dados.get("response", []):
            jogador_id = jogador_api.get("player", {}).get("id")
            if jogador_id is not None:
                jogadores_unicos[int(jogador_id)] = jogador_api

        dados["response"] = list(jogadores_unicos.values())

    def _caminho_cache_jogadores_temporada(self, liga_id, temporada):
        return self.CACHE_DIR / f"players_{liga_id}_{temporada}.json"

    def _salvar_cache_jogadores_temporada(self, caminho_cache, dados):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        caminho_temporario = caminho_cache.with_suffix(caminho_cache.suffix + ".tmp")

        with caminho_temporario.open("w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)

        caminho_temporario.replace(caminho_cache)

    def _carregar_cache_jogadores_temporada_ou_none(self, caminho_cache):
        try:
            with caminho_cache.open("r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except (OSError, json.JSONDecodeError):
            return None

    def _api_football(self):
        if self.api_football is None:
            self.api_football = ApiFootballClient()
        return self.api_football
