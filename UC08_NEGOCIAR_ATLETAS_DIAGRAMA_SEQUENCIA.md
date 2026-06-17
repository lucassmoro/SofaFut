# UC08 - Diagrama de Sequencia: Negociar Atletas

```mermaid
sequenceDiagram
    actor Usuario
    participant Tela as MarketScreen
    participant MarketCtrl as MarketController
    participant AppCtrl as AppController
    participant MarketSvc as MarketService
    participant BuyCmd as ComprarJogadorCommand
    participant SellCmd as VenderJogadorCommand
    participant Team as TeamFantasy
    participant Refresh as Callbacks de atualizacao

    Usuario->>Tela: Seleciona atleta no catalogo e compra
    Tela->>Tela: selected_rows(market_catalog_table)

    alt Nenhuma linha selecionada
        Tela-->>Usuario: nenhuma acao
    else Linha selecionada
        Tela->>Tela: jogador = context.jogadores_mercado[linha]
        Tela->>MarketCtrl: comprar(username, jogador)
        MarketCtrl->>AppCtrl: comprar_jogador(username, jogador)
        AppCtrl->>AppCtrl: _buscar_usuario_autorizado(username)
        AppCtrl->>MarketSvc: comprar(user, jogador)
        MarketSvc->>BuyCmd: criar(user, jogador)
        MarketSvc->>MarketSvc: executar_comando(command)
        MarketSvc->>MarketSvc: _validar_mercado_aberto()

        alt Mercado fechado
            MarketSvc-->>Tela: show_error(mensagem)
        else Mercado aberto
            MarketSvc->>BuyCmd: executar(service)
            BuyCmd->>Team: validar limite, duplicidade e saldo

            alt Compra invalida
                BuyCmd-->>Tela: show_error(mensagem)
            else Compra permitida
                BuyCmd->>MarketSvc: _valor_jogador(jogador)
                BuyCmd->>Team: debitar patrimonio, adicionar jogador e registrar transacao
                BuyCmd-->>MarketSvc: team atualizado
                MarketSvc-->>Tela: team atualizado
                Tela->>Tela: atualizar catalogo, elenco, patrimonio e transacoes
                Tela->>Refresh: atualizar telas dependentes
            end
        end
    end

    Usuario->>Tela: Seleciona atleta do elenco e vende
    Tela->>Tela: selected_rows(market_roster_table)

    alt Nenhuma linha selecionada
        Tela-->>Usuario: nenhuma acao
    else Linha selecionada
        Tela->>MarketCtrl: listar_elenco(username)
        MarketCtrl-->>Tela: elenco atual
        Tela->>Tela: jogador = elenco[linha]
        Tela->>MarketCtrl: vender(username, jogador)
        MarketCtrl->>AppCtrl: vender_jogador(username, jogador)
        AppCtrl->>AppCtrl: _buscar_usuario_autorizado(username)
        AppCtrl->>MarketSvc: vender(user, jogador)
        MarketSvc->>SellCmd: criar(user, jogador)
        MarketSvc->>MarketSvc: executar_comando(command)
        MarketSvc->>MarketSvc: _validar_mercado_aberto()

        alt Mercado fechado
            MarketSvc-->>Tela: show_error(mensagem)
        else Mercado aberto
            MarketSvc->>SellCmd: executar(service)
            SellCmd->>MarketSvc: _buscar_no_elenco(elenco, jogador)

            alt Jogador nao pertence ao elenco
                SellCmd-->>Tela: show_error(mensagem)
            else Venda permitida
                SellCmd->>MarketSvc: _valor_jogador(jogador_elenco)
                SellCmd->>Team: remover jogador, creditar patrimonio e registrar transacao
                SellCmd-->>MarketSvc: team atualizado
                MarketSvc-->>Tela: team atualizado
                Tela->>Tela: atualizar catalogo, elenco, patrimonio e transacoes
                Tela->>Refresh: atualizar telas dependentes
            end
        end
    end

    Usuario->>Tela: Clica em "Confirmar elenco"
    Tela->>Tela: validar len(context.jogadores_escalados) == 11

    alt Elenco incompleto
        Tela->>Tela: show_error("Compre exatamente 11 jogadores antes de confirmar.")
    else Elenco completo
        Tela->>Refresh: show_lineup()
        Tela->>Refresh: refresh_lineup("11/11 jogadores. Escolha o capitao e calcule a pontuacao.")
    end
```
