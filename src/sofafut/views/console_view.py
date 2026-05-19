from sofafut.models.time_fantasy import TimeFantasy


class ConsoleView:
    def show_message(self, message: str) -> None:
        print(message)

    def show_ranking(self, ranking: list[TimeFantasy]) -> None:
        print("Ranking geral")
        for posicao, time in enumerate(ranking, start=1):
            print(f"{posicao}. {time.nome} - {time.pontuacao_total:.2f} pts - {time.patrimonio:.2f} moedas")
