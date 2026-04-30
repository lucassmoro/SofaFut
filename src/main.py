from src.repositories.players_repository import PlayerRepository
from src.services.player_service import PlayerService
from src.models.estatistics import Estatisticas
from src.external.api_client import SofaScoreApiClient

def main():
    api = SofaScoreApiClient(timeout=10)
    
    try:
        data = api.search("internacional")
    except Exception as e:
        print(f"Erro: {e}")




if __name__ == "__main__":
    main()