from src.repositories.players_repository import PlayerRepository
from src.services.player_service import PlayerService
from src.models.estatistics import Estatisticas
from src.external.api_client import SofaScoreApiClient
from src.services.fantasy_score_service import FantasyScoreService
from src.models.match import Match
from src.models.rounds import Round
from src.models.lineup import Lineup
from src.models.player_match import MatchPlayerStats
from src.models.player_fantasy import PlayerFantasy
from src.models.player import Player
from src.repositories.rounds_repository import RoundRepository

def main():
    # api = SofaScoreApiClient(timeout=10)
    
    # try:
    #     data = api.search("internacional")
    # except Exception as e:
    #     print(f"Erro: {e}")

    fantasy = FantasyScoreService()

    round = Round(0)

    match = Match()


if __name__ == "__main__":
    main()