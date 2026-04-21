import json, csv
from pathlib import Path
from models.player import Player


class PlayerRepository:

    def __init__(self):
        base_dir = Path(__file__).resolve().parents[2]
        self.file_path = base_dir / "data" / "teste.json"

    def listar_jogadores(self) -> list[Player]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        jogadores = []

        for jogador in data:
            
            jogadores.append(Player(nome=jogador["nome"], time=jogador["time"], idade=jogador["idade"], gols=jogador["gols"], assistencias=jogador["assistencias"],
                                    cartoes_amarelos=jogador["cartoes_vermelhos"], cartoes_vermelhos=jogador["cartoes_vermelhos"],
                                    faltas=jogador["faltas"], gols_sofridos=jogador["gols_sofridos"]))    
        return jogadores
        
