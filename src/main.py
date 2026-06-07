import os

from src.controllers import AppController
from src.models.club import Club
from src.models.player import Player
from src.models.player_fantasy import PlayerFantasy


def main():
    if not os.getenv("API_FOOTBALL_KEY"):
        print("Configure sua chave da API-Football antes de testar:")
        print('export API_FOOTBALL_KEY="sua_chave_aqui"')
        return

    try:
        testar_fluxo_por_rodada()
    except RuntimeError as erro:
        print(f"Erro ao testar API-Football: {erro}")


def testar_fluxo_por_rodada():
    controller = AppController()

    liga_id = _env_int("API_FOOTBALL_LEAGUE_ID", padrao=71)
    temporada = _env_int("API_FOOTBALL_SEASON", padrao=2024)
    numero_rodada = _env_int("SOFAFUT_ROUND_NUMBER", padrao=1)
    rodada_api = _rodada_api_football(numero_rodada)
    max_partidas = _env_int("API_FOOTBALL_MAX_FIXTURES", padrao=2)

    username = "lucas"
    senha = "senha"

    controller.cadastrar_usuario(
        username=username,
        cpf="000",
        email="lucas@email.com",
        senha=senha,
        nome_team_fantasy="SofaFut FC",
    )
    print(controller.login(username, senha))

    print(
        f"\nTemporada escolhida: {temporada}"
        f"\nRodada escolhida: {numero_rodada}"
        f"\nBaixando/cacheando partidas e estatisticas de '{rodada_api}'..."
    )
    dados_rodada = controller.baixar_dados_rodada_api_football(
        liga_id=liga_id,
        temporada=temporada,
        rodada=rodada_api,
        status="FT",
        max_partidas=max_partidas,
    )

    total_partidas = len(dados_rodada.get("partidas_api", {}).get("response", []))
    print(
        f"Partidas com estatisticas em cache: "
        f"{len(dados_rodada.get('partidas', []))}/{total_partidas}"
    )
    print(
        "Para baixar mais partidas da mesma rodada em outra execucao, "
        "aumente API_FOOTBALL_MAX_FIXTURES ou rode novamente."
    )

    jogadores_disponiveis = (
        controller.listar_jogadores_disponiveis_cache_rodada_api_football(
            liga_id,
            temporada,
            rodada_api,
        )
    )
    _print_jogadores_disponiveis(jogadores_disponiveis)

    if len(jogadores_disponiveis) < 11:
        print("\nNao ha jogadores suficientes no cache para montar uma escalacao.")
        return

    jogadores = _criar_jogadores_por_cache(jogadores_disponiveis[:11])
    escalacao_fantasy = [
        PlayerFantasy(jogador, indice == 0, 0)
        for indice, jogador in enumerate(jogadores)
    ]

    rodada_model = controller.montar_rodada_por_cache_rodada_api_football(
        liga_id=liga_id,
        temporada=temporada,
        rodada=rodada_api,
        numero_rodada=numero_rodada,
        jogadores_escalados=jogadores,
    )
    controller.adicionar_rodada(rodada_model)

    pontuacao_total = controller.executar_rodada(
        username=username,
        rodada=numero_rodada,
        jogadores=escalacao_fantasy,
    )

    escalacao = controller.usuario_logado().team_fantasy.escalacoes[numero_rodada]

    print(f"\nPontuacao total da rodada {numero_rodada}: {pontuacao_total}")
    print("Pontuacao por jogador:")

    for jogador_fantasy in escalacao.jogadores:
        jogador = jogador_fantasy.jogador
        capitao = " (capitao)" if jogador_fantasy.capitao else ""
        print(
            f"- {jogador.nome}{capitao}: "
            f"{jogador_fantasy.pontuacao} pontos"
        )


def _criar_jogadores_por_cache(jogadores_disponiveis):
    jogadores = [
        Player(
            nome=jogador["nome"],
            time=None,
            posicao=jogador["posicao"] or "desconhecida",
            idade=jogador["idade"],
        )
        for jogador in jogadores_disponiveis
    ]
    clube = Club("Escalacao via cache da rodada", jogadores, 0, 0, 0, 0)

    for jogador in jogadores:
        jogador.time = clube

    return jogadores


def _print_jogadores_disponiveis(jogadores, limite=40):
    print("\nJogadores disponiveis no cache da rodada:")

    for indice, jogador in enumerate(jogadores[:limite], start=1):
        print(
            f"{indice}. {jogador['nome']} - {jogador['time']} - "
            f"{jogador['posicao']} - {jogador['minutos']} minutos - "
            f"{jogador['partida']}"
        )


def _env_int(nome, padrao=None):
    valor = os.getenv(nome)
    if not valor:
        return padrao
    return int(valor)


def _rodada_api_football(numero_rodada):
    if numero_rodada < 1 or numero_rodada > 38:
        raise RuntimeError("A rodada precisa estar entre 1 e 38")

    return f"Regular Season - {numero_rodada}"


if __name__ == "__main__":
    main()
