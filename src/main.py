from src.controllers import AppController
from src.models.lineup import Lineup


def main():
    controller = AppController()

    controller.cadastrar_usuario(
        username="ana",
        cpf="111",
        email="ana@email.com",
        senha="senha",
        nome_team_fantasy="Ana FC",
    )
    user = controller.user_database.search_user("ana")

    lineup_3 = Lineup(rodada=3, jogadores=[])
    lineup_3.pontuacao = 71

    lineup_1 = Lineup(rodada=1, jogadores=[])
    lineup_1.pontuacao = 45

    lineup_2 = Lineup(rodada=2, jogadores=[])
    lineup_2.pontuacao = 63

    user.team_fantasy.escalacoes[3] = lineup_3
    user.team_fantasy.escalacoes[1] = lineup_1
    user.team_fantasy.escalacoes[2] = lineup_2

    historico = controller.gerar_historico_pontuacao_usuario("ana")

    print("Historico gerado:")
    for escalacao in historico:
        print(f"Lineup rodada={escalacao.rodada}, pontuacao={escalacao.pontuacao}")

    print("\nHistorico formatado:")
    print(controller.exibir_historico_pontuacao_usuario("ana"))


if __name__ == "__main__":
    main()
