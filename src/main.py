from src.repositories.players_repository import PlayerRepository
from src.services.player_service import PlayerService
from src.models.sorting_params import SortingParams

def main():
    player_repository = PlayerRepository()
    player_service = PlayerService(player_repository)

    jogadores = player_service.listar_jogadores_ordenados(SortingParams.ASSISTENCIAS)

    for jogador in jogadores:
        print(jogador.nome, jogador.assistencias)

if __name__ == "__main__":
    main()