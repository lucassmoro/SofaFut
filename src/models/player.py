from src.models.player_position import PlayerPosition
from src.models.team import Team

class Player:

    def __init__(self, nome, time, posicao, idade,  
                 gols, assistencias, cartoes_amarelos,
                  cartoes_vermelhos, faltas, gols_sofridos):
        self.nome = nome
        self.time = time
        self.posicao = posicao
        self.idade = idade
        self.gols = gols
        self.assistencias = assistencias
        self.cartoes_amarelos = cartoes_amarelos
        self.cartoes_vermelhos = cartoes_vermelhos
        self.faltas = faltas
        self.gols_sofridos = gols_sofridos

    