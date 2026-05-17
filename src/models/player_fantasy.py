from src.models.player import Player

class PlayerFantasy:

    def __init__(self, jogador : Player, capitao, atuou, titular, pontuacao):
    
        self.jogador = jogador
        self.capitao = capitao
        self.atuou = atuou
        self.titular = titular
        self.pontuacao = pontuacao

    