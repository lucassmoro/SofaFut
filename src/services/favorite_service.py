class FavoriteService:
    def favoritar_jogador(self, user, jogador):
        if self._buscar_jogador(user.jogadores_favoritos, jogador) is None:
            user.jogadores_favoritos.append(jogador)
        return user.jogadores_favoritos

    def remover_jogador(self, user, jogador):
        favorito = self._buscar_jogador(user.jogadores_favoritos, jogador)
        if favorito is not None:
            user.jogadores_favoritos.remove(favorito)
        return user.jogadores_favoritos

    def listar_jogadores(self, user):
        return list(user.jogadores_favoritos)

    def favoritar_clube(self, user, nome_clube):
        nome = self._normalizar_nome_clube(nome_clube)
        if nome and nome not in user.clubes_favoritos:
            user.clubes_favoritos.append(nome)
        return user.clubes_favoritos

    def remover_clube(self, user, nome_clube):
        nome = self._normalizar_nome_clube(nome_clube)
        if nome in user.clubes_favoritos:
            user.clubes_favoritos.remove(nome)
        return user.clubes_favoritos

    def listar_clubes(self, user):
        return list(user.clubes_favoritos)

    def _buscar_jogador(self, jogadores, jogador):
        for favorito in jogadores:
            if favorito is jogador:
                return favorito

            if jogador.api_id is not None and favorito.api_id == jogador.api_id:
                return favorito

            mesma_chave = (
                self._normalizar(favorito.nome) == self._normalizar(jogador.nome)
                and self._normalizar(favorito.nome_time)
                == self._normalizar(jogador.nome_time)
            )
            if mesma_chave:
                return favorito

        return None

    def _normalizar_nome_clube(self, nome_clube):
        return (nome_clube or "").strip()

    def _normalizar(self, valor):
        return (valor or "").casefold().strip()
