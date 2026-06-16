# SofaFut - Requisitos e Modelo para Implementacao

Documento consolidado a partir de:

- `3. Requisitos.docx`
- `4. Modelo de casos de uso.docx`
- `5. Modelo de classes.docx`

Observacao: os `.docx` parecem ter sido exportados de uma ferramenta de modelagem UML/SysML. Eles trazem requisitos, casos de uso, atores, classes, atributos e rastreabilidade, mas nao detalham fluxos completos de sucesso/erro para cada caso de uso.

## 1. Visao Geral

O SofaFut e um sistema de fantasy football com cadastro de usuario, montagem de time, mercado de atletas, estatisticas, favoritos, ranking e historico de evolucao. O sistema usa dados estatisticos obtidos por API externa e calcula pontuacoes por rodada com base em regras de negocio.

## 2. Atores

| Ator | Descricao derivada do modelo | Casos de uso associados |
| --- | --- | --- |
| Usuario | Usuario nao autenticado ou usuario geral do sistema. | UC01 Registrar Conta, UC02 Fazer Login |
| Usuario autenticado | Usuario que acessa funcionalidades internas apos autenticacao. | UC01, UC02, UC03, UC04, UC05, UC06, UC07, UC08, UC09, UC10, UC11, UC12, UC13, UC14 |
| API externa | Fonte externa de dados estatisticos e informacoes de partidas/atletas. | UC18 Buscar dados |

## 3. Requisitos Funcionais

| ID | Requisito | Casos de uso relacionados | Regras relacionadas |
| --- | --- | --- | --- |
| RF01 | O sistema deve permitir cadastro e login com User e Senha. | UC01, UC02 | - |
| RF02 | O sistema deve permitir o usuario editar dados de perfil. | UC13 | - |
| RF03 | O sistema deve permitir que o usuario favorite clubes e atletas especificos. | UC07 | - |
| RF04 | O sistema deve permitir o usuario acessar estatisticas individuais, como passes, desarmes e chutes. | UC03 | RNF04 |
| RF05 | O sistema deve permitir compra e venda de jogadores com base no patrimonio, em moedas, disponivel na conta. | UC08 | RN02, RN08 |
| RF06 | O sistema deve permitir que o usuario monte seu time escolhendo uma formacao e preenchendo as posicoes. | UC09 | RN01, RN05 |
| RF07 | O sistema deve atribuir pontuacao ao time escalado pelo usuario. | UC10 | RN03, RN04, RN06, RN07 |
| RF08 | O sistema deve permitir busca de atletas por criterios analiticos. | UC04 | RNF04 |
| RF09 | O sistema deve mostrar a agenda de jogos futuros com destaque para clubes favoritados pelo usuario. | UC06 | RNF04 |
| RF10 | O sistema deve mostrar graficos do crescimento do patrimonio e pontos ao longo das rodadas. | UC12, UC14 | RN07 |
| RF11 | O sistema deve permitir comparacao direta de estatisticas entre dois atletas selecionados. | UC05 | RNF04 |
| RF12 | O sistema deve disponibilizar ranking da pontuacao dos usuarios registrados. | UC11 | RN06, RN07 |

## 4. Requisitos Nao Funcionais

| ID | Requisito | Impacto para implementacao |
| --- | --- | --- |
| RNF01 | As senhas dos usuarios devem ser armazenadas usando algoritmos de hash, por exemplo SHA-256. | Nunca armazenar senha em texto puro. Preferir hash com salt e algoritmo adequado para senha, mesmo que o documento cite SHA-256 como exemplo. |
| RNF02 | Operacoes financeiras de compra/venda devem ser atomicas; se uma parte da transacao falhar, o saldo nao deve ser alterado. | Compra/venda deve ser transacional: validar saldo, atualizar patrimonio e registrar transacao como uma unidade. |
| RNF03 | O codigo deve conter documentacao suficiente para manutencao por terceiros. | APIs internas, regras de pontuacao e integracao externa devem ser documentadas. |
| RNF04 | O sistema deve adquirir dados estatisticos atraves de uma API. | Criar camada de integracao para API externa e isolar formato externo do dominio interno. |
| RNF05 | Dados devem ser armazenados em formatos padronizados. | Persistencia deve usar estruturas consistentes para usuarios, times, atletas, estatisticas, rodadas e transacoes. |

## 5. Regras de Negocio

| ID | Regra | Requisitos impactados | Casos de uso relacionados |
| --- | --- | --- | --- |
| RN01 | O usuario deve escolher um capitao para o time escalado. Os pontos do capitao serao dobrados. | RF06 | UC09, UC16 |
| RN02 | A compra de jogadores so sera realizada se o usuario tiver saldo suficiente; nao sera permitido emprestimos nem dividas. | RF05 | UC08, UC15 |
| RN03 | Cada estatistica, como gol, assistencia e cartao, deve gerar pontuacao conforme regras pre-definidas calculadas com base nos dados DOC01, DOC03, DOC05 e DOC06. Aplica-se fator de reducao de 0.5 sobre suplentes. | RF07 | UC10 |
| RN04 | Um atleta so pontua se tiver atuado na partida. | RF07 | UC10, UC17 |
| RN05 | O usuario deve escalar exatamente o numero de jogadores definido pela formacao. | RF06 | UC09 |
| RN06 | A posicao do usuario e definida pela soma de pontos acumulados; em caso de empate, o desempate e o saldo de moedas. | RF07, RF12 | UC11 |
| RN07 | A pontuacao e calculada por rodada e acumulada ao longo do tempo. | RF07, RF10, RF12 | UC10, UC12, UC14 |
| RN08 | O mercado deve ser fechado 5 minutos antes do inicio da rodada. Quando fechado, o sistema deve impedir compra, venda ou substituicao de atletas ate a reabertura apos processamento dos dados e rankings. | RF05 | UC08 |

## 6. Casos de Uso

| ID | Nome | Ator principal | Requisitos realizados | Includes |
| --- | --- | --- | --- | --- |
| UC01 | Registrar Conta | Usuario, Usuario autenticado | RF01 | - |
| UC02 | Fazer Login | Usuario, Usuario autenticado | RF01 | - |
| UC03 | Acessar Estatisticas | Usuario autenticado | RF04, RNF04 | UC18 Buscar dados |
| UC04 | Filtar Atletas | Usuario autenticado | RF08, RNF04 | - |
| UC05 | Comparar Atletas | Usuario autenticado | RF11, RNF04 | - |
| UC06 | Ver Painel de Confrontos | Usuario autenticado | RF09, RNF04 | - |
| UC07 | Favoritar clubes/atletas | Usuario autenticado | RF03 | - |
| UC08 | Negociar atletas | Usuario autenticado | RF05, RN02, RN08 | UC15 Validar saldo |
| UC09 | Escalar time | Usuario autenticado | RF06, RN01, RN05 | UC16 Escolher capitao |
| UC10 | Calcular pontuacao | Usuario autenticado | RF07, RN03, RN04, RN07 | UC17 Verificar atuacao do atleta |
| UC11 | Ver ranking geral | Usuario autenticado | RF12, RN06 | - |
| UC12 | Ver historico de evolucao | Usuario autenticado | RF10, RN07 | - |
| UC13 | Gerenciar perfil | Usuario autenticado | RF02 | - |
| UC14 | Historico de patrimonio | Usuario autenticado | RF10, RN07 | - |
| UC15 | Validar saldo | Incluido por UC08 | RN02 | - |
| UC16 | Escolher capitao | Incluido por UC09 | RN01 | - |
| UC17 | Verificar atuacao do atleta | Incluido por UC10 | RN04, por inferencia do nome e da regra | - |
| UC18 | Buscar dados | API externa, incluido por UC03 | RNF04, por inferencia da integracao | - |

## 7. Modelo de Classes

### 7.1 Classes e atributos

| Classe | Atributos |
| --- | --- |
| Clube | `cidade: string`, `derrotas: int`, `empates: int`, `estadio: string`, `nome: string`, `tecnico: string`, `vitorias: int` |
| Escalacao | `bloqueada: boolean`, `formacao: string`, `rodada: int` |
| EstatisticaJogador | `assistencias: int`, `atuou: boolean`, `cartoesAmarelos: int`, `cartoesVermelhos: int`, `desarmes: int`, `faltas: int`, `finalizacoes: int`, `gols: int`, `minutos: int`, `passes: int`, `precisaoPasses: float` |
| Favorito | Sem atributos listados no documento. Relaciona usuario a clubes e jogadores favoritos. |
| Jogador | `nacionalidade: string`, `nome: string`, `numeroCamisa: int`, `valorMercado: double` |
| Goleiro | `defesas: int`, `defesasPenalti: int`, `golsSofridos: int` |
| JogadorLinha | `posicao: string` |
| jogadorEscalacao | `capitao: boolean`, `pontuacao: float`, `posicao: string`, `titular: boolean` |
| Partida | `dataHora: Date`, `golsMandante: int`, `golsVisitante: int`, `mandante: Clube`, `rodada: int`, `status: string` |
| PontuacaoRodada | `patrimonioApos: double`, `pontos: float`, `rodada: int` |
| TimeFantasy | `nome: string`, `patrimonio: double`, `pontuacaoTotal: float` |
| TransacaoMercado | `dataHora: Date`, `tipo: string`, `valor: double` |
| Usuario | `dataCadastro: Date`, `email: string`, `nome: string`, `senhaHash: string` |

### 7.2 Heranca

| Subclasse | Superclasse |
| --- | --- |
| Goleiro | Jogador |
| JogadorLinha | Jogador |

### 7.3 Relacionamentos estruturais

| Origem | Relacionamento | Destino | Nome no modelo |
| --- | --- | --- | --- |
| Clube | Aggregation | Favorito | `clubesFavoritos` |
| Jogador | Aggregation | Clube | - |
| Escalacao | Aggregation | TimeFantasy | `escalacoes` |
| jogadorEscalacao | Aggregation | Escalacao | `jogadoresEscalados` |
| EstatisticaJogador | Aggregation | Partida | `atletas` |
| Jogador | Aggregation | EstatisticaJogador | `atleta` |
| Favorito | Aggregation | Usuario | `favoritos` |
| Jogador | Aggregation | jogadorEscalacao | - |
| Jogador | Aggregation | TransacaoMercado | - |
| Jogador | Aggregation | Favorito | `jogadoresFavoritos` |
| PontuacaoRodada | Aggregation | TimeFantasy | `pontuacoes` |
| TimeFantasy | Aggregation | Usuario | `timeFantasy` |
| TransacaoMercado | Aggregation | TimeFantasy | `transacoes` |
| Partida | Association | Clube | `participantes`; partida possui 2 clubes, clube participa de 0..* partidas |

## 8. Informacoes Importantes para Implementacao

### 8.1 Modulos sugeridos

| Area | Responsabilidades |
| --- | --- |
| Autenticacao e perfil | Registro, login, hash de senha, edicao de perfil. |
| Integracao externa | Busca de dados de atletas, clubes, partidas e estatisticas via API. |
| Estatisticas | Consulta, filtro e comparacao de atletas. |
| Favoritos | Favoritar e listar clubes/atletas favoritos. |
| Mercado | Compra/venda de atletas, validacao de saldo, bloqueio por fechamento de mercado e registro atomico de transacoes. |
| Escalacao | Formacao, preenchimento de posicoes, selecao de capitao, validacao do numero de jogadores e bloqueio de substituicoes. |
| Pontuacao | Verificacao de atuacao, aplicacao das regras de pontuacao, capitao dobrado, suplentes com fator 0.5 e acumulado por rodada. |
| Ranking | Ordenacao por pontos acumulados e desempate por saldo de moedas. |
| Historico | Evolucao de patrimonio e pontos por rodada. |

### 8.2 Validacoes obrigatorias

- Cadastro/login devem tratar credenciais de forma segura e persistir `senhaHash`.
- Compra de jogador deve validar saldo suficiente antes de alterar patrimonio.
- Compra/venda deve ser atomica: falha parcial nao pode alterar saldo.
- Mercado fechado deve bloquear compra, venda e substituicao de atletas.
- Escalacao deve respeitar exatamente a quantidade de jogadores da formacao.
- Escalacao deve possuir capitao.
- Pontuacao so deve considerar atleta que atuou.
- Capitao deve ter pontuacao dobrada.
- Suplentes devem receber fator redutor de 0.5.
- Ranking deve desempatar por saldo de moedas.

### 8.3 Dados minimos a persistir

- Usuarios: nome, email, senha hash, data de cadastro.
- Times fantasy: nome, patrimonio, pontuacao total, usuario dono.
- Clubes: nome, cidade, estadio, tecnico, vitorias, empates, derrotas.
- Jogadores: nome, nacionalidade, numero da camisa, valor de mercado, clube e tipo de jogador.
- Estatisticas por jogador/partida: gols, assistencias, cartoes, desarmes, faltas, finalizacoes, passes, precisao de passes, minutos e atuacao.
- Partidas: rodada, data/hora, clubes participantes, placar e status.
- Escalacoes: rodada, formacao, bloqueio e jogadores escalados.
- Jogadores escalados: jogador, posicao, titularidade, capitao e pontuacao.
- Transacoes: tipo, valor, data/hora, jogador e time fantasy.
- Pontuacoes por rodada: rodada, pontos e patrimonio apos a rodada.
- Favoritos: usuario, clubes favoritos e jogadores favoritos.

### 8.4 Pontos de atencao

- Os documentos citam `User e Senha`; na implementacao, padronizar para `email/usuario` e `senha`, conforme o modelo de classe `Usuario`.
- A classe `jogadorEscalacao` aparece com inicial minuscula no modelo. Para codigo orientado a objetos, padronizar como `JogadorEscalacao`.
- O requisito RN03 referencia documentos `DOC01`, `DOC03`, `DOC05` e `DOC06`, mas eles nao estao presentes nesta pasta. As regras numericas exatas de pontuacao dependem desses documentos ou de uma decisao de produto.
- Os casos de uso nao descrevem fluxos alternativos; os fluxos de tela/API devem ser derivados dos requisitos e validados separadamente.
- RNF01 cita SHA-256 como exemplo, mas para senhas e recomendavel usar algoritmo proprio para senha com salt, como bcrypt, Argon2 ou PBKDF2.
