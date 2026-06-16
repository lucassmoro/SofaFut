# Fluxo dos Casos de Uso no Codigo

Este documento descreve o caminho percorrido pelos casos de uso implementados na interface PySide, partindo da acao do usuario na tela ate a finalizacao no controller, service, repositorio ou modelo correspondente.

## Visao geral da arquitetura

O fluxo visual comeca em `SofaFutPySideGui`, que cria a aplicacao Qt e abre `LoginWindow`. Apos login bem-sucedido, `LoginWindow` instancia `MainWindow`, que monta as abas principais da aplicacao.

`MainWindow` cria um `PySideViewContext` compartilhado com:

- usuario logado;
- controllers disponiveis;
- catalogo de jogadores;
- jogadores disponiveis na rodada;
- jogadores de mercado;
- elenco escalado;
- capitao;
- favoritos;
- direcoes de ordenacao das tabelas.

Cada tela em `src/views/pyside/uc*.py` recebe esse contexto e callbacks para atualizar outras abas quando um caso de uso altera estado compartilhado. O padrao geral e:

```text
Interface PySide -> tela do caso de uso -> controller especifico -> AppController -> service/repositorio/modelo -> atualizacao da interface
```

As posicoes vindas da API/cache sao normalizadas no codigo antes de aparecerem na interface ou entrarem no calculo: `G`/`Goalkeeper` vira `goleiro`, `D`/`Defender` vira `defensor`, `M`/`Midfielder` vira `meia` e `F`/`Forward`/`Attacker` vira `atacante`.

## UC01 - Registrar Conta

**Entrada na interface:** tela inicial de login, botao `Cadastrar`.

**Fluxo no codigo:**

1. `LoginWindow._cadastrar` le `username_input` e `password_input`.
2. Se usuario ou senha estiverem vazios, `LoginWindow._erro` mostra a mensagem `Preencha usuario e senha.`.
3. Com dados preenchidos, a tela chama `AuthController.cadastrar(username=username, senha=senha)`.
4. `AuthController.cadastrar` repassa os dados para `AppController.cadastrar_usuario`, preenchendo valores padrao para CPF, email e nome do time fantasy quando necessario.
5. `AppController.cadastrar_usuario` chama `AuthService.cadastrar`.
6. `AuthService.cadastrar` valida e registra o usuario na base de usuarios.
7. A mensagem retornada sobe ate `LoginWindow._cadastrar`.

**Finalizacao:** a interface mostra o resultado em `QMessageBox.information`. A janela continua na tela de login para permitir o acesso com a conta criada.

## UC02 - Fazer Login

**Entrada na interface:** tela inicial de login, botao `Entrar`.

**Fluxo no codigo:**

1. `LoginWindow._login` le usuario e senha.
2. Se algum campo estiver vazio, mostra erro com `LoginWindow._erro`.
3. A tela chama `AuthController.login(username, senha)`.
4. `AuthController.login` delega para `AppController.login`.
5. `AppController.login` chama `AuthService.login`, que autentica o usuario e atualiza a sessao.
6. Se a mensagem retornada for diferente de `Usuario logado`, a tela exibe o erro e interrompe o fluxo.
7. Em caso de sucesso, `LoginWindow._login` cria `MainWindow`, repassando todos os controllers.
8. `MainWindow.__init__` cria `PySideViewContext`, monta as abas e executa carregamentos iniciais:
   - `round_screen.carregar_catalogo`;
   - `ranking_screen.atualizar`;
   - `market_screen.atualizar`.

**Finalizacao:** `MainWindow` e exibida maximizada e a janela de login e fechada.

## UC05 - Comparar Atletas

**Entrada na interface:** aba `Comparar`, selecao de `Atleta A`, `Atleta B` e botao `Comparar`.

**Fluxo no codigo:**

1. O catalogo e carregado antes pela janela principal via `RoundScreen.carregar_catalogo`.
2. Apos o catalogo carregar, `MainWindow` executa o callback `compare_screen.preencher_combos`.
3. `ComparePlayersScreen.preencher_combos` popula os dois `QComboBox` com jogadores do `context.jogadores_catalogo`.
4. Ao clicar em `Comparar`, `ComparePlayersScreen.comparar_jogadores` valida se existem pelo menos dois jogadores no catalogo.
5. A tela recupera os jogadores selecionados pelos indices dos combos.
6. A comparacao e enviada para `PlayerComparisonController.comparar`.
7. `PlayerComparisonController` delega para `AppController.comparar_jogadores`.
8. `AppController` chama `PlayerComparisonService.comparar`, que monta as metricas comparativas.
9. A tela formata valores numericos com `ComparePlayersScreen.formatar_valor`.

**Finalizacao:** `ComparePlayersScreen.comparar_jogadores` preenche `compare_table` com metrica, valor do atleta A e valor do atleta B.

## UC03 - Acessar Estatisticas

**Entrada na interface:** aba `Estatisticas`, selecao de atleta e botao `Ver estatisticas`.

**Fluxo no codigo:**

1. `PlayerStatsScreen.atualizar_atletas` carrega os atletas de `context.jogadores_catalogo`.
2. Se o contexto ainda estiver vazio, a tela consulta `PlayerCatalogController.listar_jogadores`.
3. O combo de atletas e preenchido com nome e clube.
4. Ao clicar em `Ver estatisticas`, `PlayerStatsScreen.mostrar_estatisticas` recupera o atleta selecionado.
5. A tela chama `PlayerComparisonController.estatisticas_jogador`.
6. O controller delega para `AppController.estatisticas_jogador`.
7. `AppController` chama `PlayerComparisonService.estatisticas_jogador`.
8. O service retorna metricas de gols, assistencias, faltas, cartoes e gols sofridos.
9. A tela tambem monta uma tabela com dados basicos do atleta.

**Finalizacao:** a aba mostra dados cadastrais do atleta e suas metricas estatisticas, com posicao em portugues.

## UC04 - Filtrar Atletas

**Entrada na interface:** aba `Atletas`, filtros de nome, clube, posicao, criterio de ordenacao e botao `Filtrar`.

**Fluxo no codigo:**

1. `FilterPlayersScreen.atualizar_opcoes` le o catalogo e popula o combo de posicoes.
2. Ao clicar em `Filtrar`, `FilterPlayersScreen.filtrar` solicita jogadores ordenados por `PlayerCatalogController.listar_jogadores_ordenados`.
3. O controller delega para `AppController.listar_jogadores`.
4. `AppController` chama `PlayerService.listar_jogadores_ordenados`, que normaliza criterio e direcao.
5. A tela aplica os filtros locais de nome, clube e posicao sobre a lista ordenada.
6. O resultado final e enviado para `fill_players_table`.

**Finalizacao:** a tabela da aba Atletas exibe apenas os jogadores que atendem aos filtros, com posicoes em portugues e status informando a quantidade encontrada.

## UC06 - Ver Painel de Confrontos

**Entrada na interface:** aba `Rodada`, selecao de temporada, rodada, maximo de partidas e botao `Carregar rodada`.

**Fluxo no codigo:**

1. `RoundScreen.build` cria os combos de temporada e rodada a partir de `RoundController.listar_temporadas_disponiveis` e `RoundController.listar_rodadas_disponiveis`.
2. Ao clicar em `Carregar rodada`, `RoundScreen.carregar_rodada` le temporada, rodada e maximo de partidas.
3. A tela chama `RoundController.baixar_dados_rodada`.
4. `RoundController.baixar_dados_rodada` converte o numero da rodada para o nome usado pela API com `nome_rodada_api`.
5. O controller chama `AppController.baixar_dados_rodada_api_football`.
6. `AppController` delega para `MatchService.baixar_dados_rodada_api_football`.
7. `MatchService` busca partidas e estatisticas via API/cache e salva o cache da rodada.
8. De volta a tela, `RoundScreen.carregar_rodada` chama `listar_jogadores_rodada`.
9. `RoundScreen.listar_jogadores_rodada` chama `RoundController.listar_jogadores_disponiveis`.
10. O controller delega para `AppController.listar_jogadores_disponiveis_cache_rodada_api_football`.
11. `MatchService.listar_jogadores_disponiveis_cache_rodada_api_football` le o cache e devolve atuacoes disponiveis.
12. A tela salva o resultado em `context.jogadores_disponiveis` e preenche `available_table`.
13. O callback `on_players_loaded` atualiza o catalogo da aba Mercado.
14. O callback `on_round_reset` limpa o elenco da rodada atual no mercado.

**Finalizacao:** a aba Rodada mostra jogadores disponiveis com posicoes em portugues e status com a quantidade de partidas cacheadas. A aba Mercado passa a listar atletas negociaveis da rodada.

**Fluxo para ver jogos e resultados da rodada:**

1. Na aba `Jogos`, o usuario seleciona temporada e rodada.
2. Ao clicar em `Carregar jogos`, `RoundMatchesScreen.carregar_jogos` chama `RoundController.listar_jogos_rodada`.
3. `RoundController.listar_jogos_rodada` usa `carregar_dados_rodada_cache`, lendo somente o cache local da rodada.
4. O controller extrai `fixture`, `teams`, `goals`, `status` e `venue` de `partidas_api.response`.
5. A tela formata data e placar como `mandante x visitante`.
6. `fill_table` preenche a tabela com data, status, mandante, placar, visitante, estadio e cidade.

**Finalizacao dos jogos:** a aba Jogos mostra os resultados das partidas da rodada sem chamar API externa.

## UC18 - Buscar Dados

**Entrada na interface:** ocorre dentro do fluxo da aba `Rodada`, ao carregar dados da rodada.

**Fluxo no codigo:**

1. `RoundScreen.carregar_rodada` inicia a busca.
2. `RoundController.baixar_dados_rodada` prepara os parametros de liga, temporada e rodada.
3. `AppController.baixar_dados_rodada_api_football` encaminha para `MatchService`.
4. `MatchService.baixar_dados_rodada_api_football` consulta a API externa quando necessario e usa cache local quando disponivel.
5. As estatisticas retornadas sao normalizadas e armazenadas no cache da rodada.

**Finalizacao:** os dados ficam disponiveis para `UC06`, `UC08`, `UC09` e `UC10` por meio de `context.jogadores_disponiveis` e dos metodos de montagem de rodada por cache.

## UC07 - Favoritar Clubes/Atletas

**Entrada na interface:** botoes `Favoritar jogador` e `Favoritar clube` na aba Mercado; botoes de remocao na aba Favoritos.

**Fluxo para favoritar jogador:**

1. `MarketScreen.favoritar_jogador_mercado` le a linha selecionada em `market_catalog_table`.
2. A tela recupera o jogador correspondente em `context.jogadores_mercado`.
3. Chama `FavoriteController.favoritar_jogador(context.username, jogador)`.
4. O controller delega para `AppController.favoritar_jogador`.
5. `AppController` chama `FavoriteService.favoritar_jogador`.
6. O service adiciona o jogador a lista de favoritos do usuario, evitando duplicidade.
7. A tela chama o callback `refresh_favorites`.

**Fluxo para favoritar clube:**

1. `MarketScreen.favoritar_clube_mercado` usa o jogador selecionado para obter `jogador.nome_time`.
2. Chama `FavoriteController.favoritar_clube`.
3. O fluxo segue por `AppController.favoritar_clube` ate `FavoriteService.favoritar_clube`.
4. O service normaliza o nome do clube e registra o favorito.
5. A aba Favoritos e atualizada.

**Fluxo para remover favoritos:**

1. `FavoritesScreen.remover_jogador_favorito` ou `FavoritesScreen.remover_clube_favorito` le a linha selecionada.
2. A tela chama o metodo correspondente em `FavoriteController`.
3. O controller delega para `AppController`.
4. `FavoriteService` remove o item.
5. `FavoritesScreen.preencher` recarrega as tabelas.

**Finalizacao:** a aba Favoritos mostra as listas atualizadas de jogadores e clubes favoritos.

## UC08 - Negociar Atletas

**Entrada na interface:** aba `Mercado`, botoes `Comprar selecionado`, `Vender selecionado` e `Confirmar elenco`.

**Fluxo para comprar:**

1. `MarketScreen.comprar_selecionado` le a linha selecionada em `market_catalog_table`.
2. A tela recupera o jogador em `context.jogadores_mercado`.
3. Chama `MarketController.comprar(context.username, jogador)`.
4. `MarketController` delega para `AppController.comprar_jogador`.
5. `AppController.comprar_jogador` busca o usuario autorizado e chama `MarketService.comprar`.
6. `MarketService.comprar` valida mercado aberto, saldo, duplicidade no elenco e limite de elenco.
7. Se a compra for valida, o service debita o patrimonio, adiciona o jogador ao elenco e registra `TransacaoMercado`.
8. A tela chama `MarketScreen.atualizar`.

**Fluxo para vender:**

1. `MarketScreen.vender_selecionado` le a linha selecionada em `market_roster_table`.
2. A tela consulta o elenco atual com `MarketController.listar_elenco`.
3. Chama `MarketController.vender`.
4. O fluxo segue por `AppController.vender_jogador` ate `MarketService.vender`.
5. O service valida mercado aberto, encontra o jogador no elenco, remove o jogador, credita patrimonio e registra transacao.
6. A tela atualiza mercado, escalacao, favoritos e historico.

**Fluxo para confirmar elenco:**

1. `MarketScreen.confirmar_elenco` verifica se `context.jogadores_escalados` possui exatamente 11 jogadores.
2. Se nao possuir, mostra erro.
3. Se possuir, chama `show_lineup`, mudando para a aba Escalacao.
4. Chama `refresh_lineup` com mensagem orientando a escolha do capitao e calculo da pontuacao.

**Finalizacao:** patrimonio, elenco, ultimas transacoes, escalacao e historico ficam sincronizados na interface, mantendo as posicoes em portugues nas tabelas.

## UC15 - Validar Saldo

**Entrada na interface:** incluido no fluxo de compra de `UC08`.

**Fluxo no codigo:**

1. `MarketScreen.comprar_selecionado` envia o jogador selecionado para `MarketController.comprar`.
2. `AppController.comprar_jogador` localiza o usuario autorizado.
3. `MarketService.comprar` calcula o valor do jogador.
4. O service compara o valor com o patrimonio disponivel do usuario.
5. Se o patrimonio for insuficiente, a compra e interrompida com excecao.
6. A excecao retorna para `MarketScreen.comprar_selecionado`.

**Finalizacao:** em caso de saldo insuficiente, nenhuma transacao e registrada e a interface mostra a mensagem de erro. Em caso de saldo suficiente, o fluxo normal de compra continua.

## UC09 - Escalar Time

**Entrada na interface:** aba Mercado ao comprar jogadores e botao `Confirmar elenco`; aba Escalacao para visualizar/remover jogadores.

**Fluxo no codigo:**

1. A escalacao e alimentada indiretamente pelo Mercado.
2. Sempre que o mercado e atualizado, `MarketScreen.atualizar` consulta o elenco com `MarketController.listar_elenco`.
3. O elenco retornado e salvo em `context.jogadores_escalados`.
4. `MarketScreen.atualizar` chama `refresh_lineup`.
5. `LineupScoreScreen.preencher` preenche `lineup_table` com ID, jogador, time, posicao e indicador de capitao.
6. Ao clicar em `Remover`, `LineupScoreScreen.remover_escalado` vende o jogador via `MarketController.vender`.
7. A venda atualiza novamente mercado e escalacao.
8. Ao confirmar elenco no Mercado, `MarketScreen.confirmar_elenco` valida que existem exatamente 11 jogadores.

**Finalizacao:** a aba Escalacao reflete o elenco comprado com posicoes em portugues e, com 11 jogadores, fica pronta para escolha de capitao e calculo de pontuacao.

## UC16 - Escolher Capitao

**Entrada na interface:** aba `Escalacao`, selecao de um jogador e botao `Definir capitao`.

**Fluxo no codigo:**

1. `LineupScoreScreen.definir_capitao` le a linha selecionada em `lineup_table`.
2. Se nenhuma linha estiver selecionada, o metodo retorna sem alterar estado.
3. A tela recupera o jogador correspondente em `context.jogadores_escalados`.
4. Salva o jogador em `context.capitao`.
5. Chama `LineupScoreScreen.preencher`.

**Finalizacao:** a tabela da escalacao marca o capitao com `Sim`. Esse estado sera usado em `UC10` para montar a escalacao fantasy e dobrar a pontuacao do capitao conforme a regra de negocio.

## UC10 - Calcular Pontuacao

**Entrada na interface:** aba `Escalacao`, botao `Calcular pontuacao`.

**Fluxo no codigo:**

1. `LineupScoreScreen.calcular_pontuacao` valida que existem exatamente 11 jogadores em `context.jogadores_escalados`.
2. Valida que `context.capitao` foi definido.
3. Obtem a rodada atual por callback para `RoundScreen.rodada`.
4. Chama `LineupController.criar_escalacao_fantasy`, passando jogadores escalados e capitao.
5. `LineupController` converte os jogadores para objetos fantasy.
6. A tela chama `RoundController.montar_rodada_por_cache`.
7. O controller delega para `AppController.montar_rodada_por_cache_rodada_api_football`.
8. `MatchService.montar_rodada_por_cache_rodada_api_football` monta o modelo de rodada com base no cache e nas atuacoes dos atletas.
9. A tela registra a rodada com `RoundController.adicionar_rodada`.
10. Chama `LineupController.executar_rodada`.
11. `LineupController.executar_rodada` delega para `AppController.executar_rodada`.
12. `AppController.executar_rodada` chama `TeamFantasyService.executar_rodada`.
13. `TeamFantasyService` calcula pontuacao por jogador e total da rodada.
14. A tela busca a escalacao calculada com `LineupController.buscar_escalacao`.
15. `score_text` recebe a pontuacao total e a pontuacao individual de cada jogador.
16. O callback `refresh_ranking` atualiza a aba Ranking.

**Finalizacao:** a pontuacao da rodada aparece na aba Escalacao e o ranking geral e recalculado. A estrategia de pontuacao usa a posicao ja normalizada em portugues.

## UC17 - Verificar Atuacao do Atleta

**Entrada na interface:** incluido no calculo de pontuacao de `UC10`.

**Fluxo no codigo:**

1. `LineupScoreScreen.calcular_pontuacao` chama `RoundController.montar_rodada_por_cache`.
2. O controller delega a montagem para `MatchService.montar_rodada_por_cache_rodada_api_football`.
3. `MatchService` cruza os jogadores escalados com atuacoes registradas no cache da rodada.
4. Apenas atletas com atuacao encontrada sao associados a estatisticas de partida.
5. A rodada montada e usada por `TeamFantasyService.executar_rodada`.

**Finalizacao:** o calculo considera as atuacoes disponiveis no cache da rodada. Se o atleta nao tiver atuado ou nao for encontrado no cache, ele nao recebe estatisticas de partida para pontuar.

## UC11 - Ver Ranking Geral

**Entrada na interface:** aba `Ranking`, botao `Atualizar ranking`, ou atualizacao automatica apos calcular pontuacao.

**Fluxo no codigo:**

1. `RankingScreen.atualizar` chama `RankingController.formatar_ranking_usuarios`.
2. `RankingController` delega para `AppController.exibir_ranking_usuarios`.
3. `AppController` chama `UserService.gerar_ranking_usuarios` e `UserService.formatar_ranking_usuarios`.
4. O service ordena usuarios conforme pontuacao e criterios de desempate implementados no dominio.
5. A string formatada retorna para a tela.

**Finalizacao:** `RankingScreen.atualizar` preenche `ranking_text` com o ranking formatado.

## UC12 - Ver Historico de Evolucao

**Entrada na interface:** aba `Evolucao`, botao `Atualizar evolucao`, ou atualizacao automatica apos mercado/pontuacao.

**Fluxo no codigo:**

1. `EvolutionHistoryScreen.atualizar` chama `RankingController.historico_pontuacao_usuario`.
2. O controller delega para `AppController.gerar_historico_pontuacao_usuario`.
3. `AppController` chama `UserService.gerar_historico_pontuacao_usuario`, que retorna escalacoes ordenadas por rodada.
4. A tela chama `MarketController.historico_patrimonio`.
5. `MarketController` delega para `AppController.historico_patrimonio`.
6. `AppController` chama `MarketService.historico_patrimonio`, retornando transacoes do time fantasy.
7. A tela preenche uma tabela de pontuacao por rodada e uma tabela de patrimonio por transacao.
8. A tela calcula um resumo textual com total de rodadas, pontuacao acumulada no historico, total de transacoes e patrimonio atual.

**Finalizacao:** a aba Evolucao mostra a evolucao de pontos e patrimonio com tabelas e resumo.

## UC14 - Historico de Patrimonio

**Entrada na interface:** aba `Historico`, botao `Atualizar historico`, ou atualizacao automatica apos compra/venda no Mercado.

**Fluxo no codigo:**

1. `AssetHistoryScreen.preencher` chama `MarketController.historico_patrimonio(context.username)`.
2. `MarketController` delega para `AppController.historico_patrimonio`.
3. `AppController` busca o usuario autorizado e chama `MarketService.historico_patrimonio`.
4. `MarketService` retorna as transacoes do time fantasy do usuario.
5. A tela formata data, tipo, jogador, valor e patrimonio apos cada transacao.

**Finalizacao:** `history_table` mostra o historico de transacoes e evolucao de patrimonio.

## UC13 - Gerenciar Perfil

**Entrada na interface:** aba `Perfil`, campos de email, username, senha atual e nova senha.

**Fluxo para alterar email:**

1. `ProfileScreen.alterar_email` valida se o novo email foi informado.
2. A tela chama `UserProfileController.alterar_email`.
3. O controller delega para `AppController.alterar_email`.
4. `AppController` chama `UserService.alterar_email`.
5. `UserService` verifica permissao pela sessao, busca o usuario e altera o email.

**Fluxo para alterar username:**

1. `ProfileScreen.alterar_username` valida se o novo username foi informado.
2. A tela chama `UserProfileController.alterar_nome`.
3. O controller delega para `AppController.alterar_nome`.
4. `UserService.alterar_nome` verifica permissao e chama `UserDataBase.update_username`.
5. Se a alteracao retornar `Username atualizado`, a tela atualiza `context.username`.
6. `MainWindow._atualizar_username` troca o texto do header para o novo username.

**Fluxo para alterar senha:**

1. `ProfileScreen.alterar_senha` valida senha atual e nova senha.
2. A tela chama `UserProfileController.alterar_senha`.
3. O controller delega para `AppController.alterar_senha`.
4. `UserService.alterar_senha` verifica permissao, valida a senha atual e salva a nova senha.

**Finalizacao:** a aba Perfil mostra a mensagem retornada pelo service e, no caso de username, a janela passa a operar com o novo usuario no contexto.

## Fluxos auxiliares de navegacao e estado

### Logout

1. `MainWindow._logout` chama `AuthController.logout`.
2. `AuthController.logout` delega para `AppController.logout`.
3. `AppController.logout` limpa a sessao.
4. `MainWindow` cria uma nova `LoginWindow`.
5. A janela principal e fechada.

### Ordenacao de tabelas

1. As tabelas de Rodada e Mercado conectam `horizontalHeader().sectionClicked` a metodos de ordenacao.
2. `RoundScreen.ordenar_jogadores_disponiveis` ordena `context.jogadores_disponiveis`.
3. `MarketScreen.ordenar_jogadores_mercado` ordena `context.jogadores_mercado`.
4. `next_sort_direction` alterna ordem crescente/decrescente por chave.
5. `sortable_value` normaliza numeros, textos e valores nulos.

## Cobertura dos casos de uso

Os casos UC01, UC02, UC03, UC04, UC05, UC06, UC07, UC08, UC09, UC10, UC11, UC12, UC13, UC14, UC15, UC16, UC17 e UC18 possuem fluxo PySide documentado neste arquivo.
