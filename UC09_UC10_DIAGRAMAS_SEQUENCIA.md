# UC09 e UC10 - Diagramas de Sequencia

## UC09 - Escalar time

```mermaid
sequenceDiagram
    actor Usuario
    participant Mercado as MarketScreen
    participant Tela as LineupScoreScreen
    participant Market as MarketController
    participant App as AppController
    participant MarketSvc as MarketService
    participant SellCmd as VenderJogadorCommand
    participant Team as TeamFantasy
    participant Refresh as Callback refresh_market

    Usuario->>Mercado: Compra 11 jogadores no mercado
    Mercado->>Market: listar_elenco(username)
    Market-->>Mercado: elenco atual
    Mercado->>Mercado: context.jogadores_escalados = elenco
    Mercado->>Tela: refresh_lineup()
    Tela->>Tela: preencher tabela do elenco

    Usuario->>Mercado: Clica em "Confirmar elenco"
    Mercado->>Mercado: validar len(context.jogadores_escalados) == 11

    alt Elenco incompleto
        Mercado->>Mercado: show_error("Compre exatamente 11 jogadores antes de confirmar.")
    else Elenco completo
        Mercado->>Tela: show_lineup()
        Mercado->>Tela: refresh_lineup("11/11 jogadores. Escolha o capitao e calcule a pontuacao.")
    end

    Usuario->>Tela: Seleciona um jogador na tabela
    Usuario->>Tela: Clica em "Definir capitao"
    Tela->>Tela: selected_rows(lineup_table)

    alt Sem selecao
        Tela-->>Usuario: nenhuma acao
    else Com selecao
        Tela->>Tela: context.capitao = context.jogadores_escalados[linha]
        Tela->>Tela: preencher()
    end

    Usuario->>Tela: Seleciona um jogador na tabela
    Usuario->>Tela: Clica em "Remover"
    Tela->>Tela: selected_rows(lineup_table)

    alt Sem selecao
        Tela-->>Usuario: nenhuma acao
    else Com selecao
        Tela->>Tela: jogador = context.jogadores_escalados[linha]
        Tela->>Market: vender(username, jogador)
        Market->>App: vender_jogador(username, jogador)
        App->>App: _buscar_usuario_autorizado(username)
        App->>MarketSvc: vender(user, jogador)
        MarketSvc->>SellCmd: criar(user, jogador)
        MarketSvc->>MarketSvc: executar_comando e validar mercado

        alt Erro na venda
            MarketSvc-->>Tela: show_error(mensagem)
        else Venda permitida
            MarketSvc->>SellCmd: executar(service)
            SellCmd->>MarketSvc: _buscar_no_elenco(elenco, jogador)

            alt Jogador nao pertence ao elenco
                SellCmd-->>Tela: show_error(mensagem)
            else Venda realizada
                SellCmd->>MarketSvc: _valor_jogador(jogador_elenco)
                SellCmd->>Team: remover jogador, creditar patrimonio e registrar transacao
                SellCmd-->>MarketSvc: team atualizado
                MarketSvc-->>Tela: team atualizado
                Tela->>Refresh: refresh_market()
            end
        end
    end
```

## UC10 - Calcular pontuacao

```mermaid
sequenceDiagram
    actor Usuario
    participant Tela as LineupScoreScreen
    participant Lineup as LineupController
    participant Round as RoundController
    participant App as AppController
    participant MatchSvc as MatchService
    participant RoundRepo as RoundRepository
    participant TeamSvc as TeamFantasyService
    participant RoundModel as Round
    participant Stats as MatchPlayerStats
    participant Fantasy as PlayerFantasy
    participant LineupModel as Lineup
    participant Team as TeamFantasy
    participant Strategy as PontuacaoStrategy
    participant Refresh as Callbacks de atualizacao

    Usuario->>Tela: Clica em "Calcular pontuacao"
    Tela->>Tela: validar elenco completo e capitao

    alt Dados invalidos
        Tela->>Tela: show_error(mensagem)
    else Dados validos
        Tela->>Tela: rodada = get_rodada()
        Tela->>Lineup: criar_escalacao_fantasy(jogadores_escalados, capitao)
        Lineup->>Fantasy: criar jogadores com capitao
        Lineup-->>Tela: jogadores_fantasy

        Tela->>Round: montar_rodada_por_cache(temporada, rodada, jogadores_escalados)
        Round->>App: montar_rodada_por_cache_rodada_api_football(...)
        App->>MatchSvc: montar rodada pelo cache
        MatchSvc->>Stats: converter atuacoes encontradas
        MatchSvc-->>RoundModel: rodada_model
        RoundModel-->>Tela: rodada_model

        Tela->>Round: adicionar_rodada(rodada_model)
        Round->>App: adicionar_rodada(rodada_model)
        App->>RoundRepo: adicionar_rodada(rodada_model)

        Tela->>Lineup: executar_rodada(username, rodada, jogadores_fantasy)
        Lineup->>App: executar_rodada(username, rodada, jogadores_fantasy)
        App->>App: _buscar_usuario_autorizado(username)
        App->>TeamSvc: executar_rodada(user, rodada, jogadores_fantasy, rodadas_repo)
        TeamSvc->>LineupModel: montar escalacao da rodada
        TeamSvc->>Team: salvar escalacao
        TeamSvc->>RoundRepo: buscar_por_numero(rodada)

        loop Para cada atuacao da escalacao
            TeamSvc->>Strategy: calcular(MatchPlayerStats, capitao)
            Strategy-->>Fantasy: pontuacao do jogador
        end

        TeamSvc->>LineupModel: atualizar pontuacao da escalacao
        TeamSvc->>Team: atualizar pontuacao acumulada
        TeamSvc-->>Tela: pontuacao_total
        Tela->>Tela: exibir pontuacao total e individual
        Tela->>Refresh: refresh_ranking() e refresh_evolution()
    end
```
