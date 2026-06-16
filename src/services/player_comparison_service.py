class PlayerComparisonService:
    def estatisticas_jogador(self, jogador):
        return self._estatisticas_fake(jogador)

    def comparar(self, jogador_a, jogador_b):
        estatisticas_a = self.estatisticas_jogador(jogador_a)
        estatisticas_b = self.estatisticas_jogador(jogador_b)

        metricas = [
            ("Posicao", jogador_a.posicao or "-", jogador_b.posicao or "-"),
            ("Time", jogador_a.nome_time or "-", jogador_b.nome_time or "-"),
            ("Valor de mercado", jogador_a.valor_mercado or 0, jogador_b.valor_mercado or 0),
            ("Gols", estatisticas_a["gols"], estatisticas_b["gols"]),
            ("Assistencias", estatisticas_a["assistencias"], estatisticas_b["assistencias"]),
            ("Faltas", estatisticas_a["faltas"], estatisticas_b["faltas"]),
            ("Cartoes amarelos", estatisticas_a["cartoes_amarelos"], estatisticas_b["cartoes_amarelos"]),
            ("Cartoes vermelhos", estatisticas_a["cartoes_vermelhos"], estatisticas_b["cartoes_vermelhos"]),
            ("Gols sofridos", estatisticas_a["gols_sofridos"], estatisticas_b["gols_sofridos"]),
        ]

        return {
            "jogador_a": jogador_a,
            "jogador_b": jogador_b,
            "metricas": metricas,
        }

    def _estatisticas_fake(self, jogador):
        base = self._base_deterministica(jogador)
        posicao = (jogador.posicao or "").casefold()

        gols = base % 12
        assistencias = (base // 3) % 10
        gols_sofridos = 0

        if "goalkeeper" in posicao or "goleiro" in posicao:
            gols = 0
            assistencias = base % 2
            gols_sofridos = (base // 2) % 35
        elif "defender" in posicao or "zagueiro" in posicao:
            gols = base % 5
            gols_sofridos = (base // 4) % 20

        return {
            "gols": gols,
            "assistencias": assistencias,
            "faltas": (base // 5) % 45,
            "cartoes_amarelos": (base // 7) % 8,
            "cartoes_vermelhos": (base // 13) % 2,
            "gols_sofridos": gols_sofridos,
        }

    def _base_deterministica(self, jogador):
        texto = f"{jogador.api_id or ''}:{jogador.nome}:{jogador.nome_time}:{jogador.posicao}"
        return sum(ord(caractere) for caractere in texto)
