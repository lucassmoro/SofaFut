# Padroes de Projeto - Diagramas de Classes

Este documento apresenta apenas os diagramas de classes dos padroes de projeto implementados no projeto. Os diagramas focam nas classes que participam de cada padrao, sem representar todo o modelo de dominio do SofaFut.

## 1. Command - UC08 Negociar Atletas

**Objetivo:** encapsular as operacoes de compra e venda de atletas como comandos executaveis pelo `MarketService`.

**Participantes do padrao:**

- `MarketCommand`: interface abstrata do comando.
- `ComprarJogadorCommand`: comando concreto para compra de jogador.
- `VenderJogadorCommand`: comando concreto para venda de jogador.
- `MarketService`: invoker que valida o mercado e executa o comando.
- `User` e `Player`: dados usados pelos comandos.
- `TeamFantasy` e `TransacaoMercado`: objetos de dominio alterados pelos comandos.

```mermaid
classDiagram
    class MarketCommand {
        <<abstract>>
        +executar(service)*
    }

    class ComprarJogadorCommand {
        -user: User
        -jogador: Player
        +__init__(user: User, jogador: Player)
        +executar(service)
    }

    class VenderJogadorCommand {
        -user: User
        -jogador: Player
        +__init__(user: User, jogador: Player)
        +executar(service)
    }

    class MarketService {
        -mercado_aberto: bool
        +executar_comando(command: MarketCommand)
        +comprar(user: User, jogador: Player)
        +vender(user: User, jogador: Player)
        +abrir_mercado()
        +fechar_mercado()
        -_validar_mercado_aberto()
        -_buscar_no_elenco(elenco, jogador)
        -_valor_jogador(jogador)
    }

    class User {
        +team_fantasy: TeamFantasy
    }

    class Player {
        +api_id
        +nome
        +nome_time
        +valor_mercado
    }

    class TeamFantasy {
        +patrimonio
        +elenco
        +transacoes
    }

    class TransacaoMercado {
        +jogador
        +tipo
        +valor
        +patrimonio_apos
    }

    MarketCommand <|-- ComprarJogadorCommand
    MarketCommand <|-- VenderJogadorCommand
    MarketService ..> MarketCommand : executa
    MarketService ..> ComprarJogadorCommand : cria em comprar()
    MarketService ..> VenderJogadorCommand : cria em vender()
    ComprarJogadorCommand --> User
    ComprarJogadorCommand --> Player
    VenderJogadorCommand --> User
    VenderJogadorCommand --> Player
    User --> TeamFantasy
    ComprarJogadorCommand ..> TransacaoMercado : registra compra
    VenderJogadorCommand ..> TransacaoMercado : registra venda
```

## 2. Template Method - UC13 Gerenciar Perfil

**Objetivo:** reutilizar o fluxo comum de alteracao de perfil, deixando cada alteracao concreta implementar apenas o passo especifico.

**Participantes do padrao:**

- `ProfileUpdateTemplate`: classe abstrata que define o algoritmo fixo em `executar()`.
- `AlterarEmailTemplate`: implementa a alteracao de email.
- `AlterarNomeTemplate`: implementa a alteracao de username.
- `AlterarSenhaTemplate`: implementa a alteracao de senha.
- `UserService`: contexto usado pelos templates e fachada chamada pelos controllers.
- `UserDataBase`, `Session` e `User`: dependencias usadas no fluxo comum.

```mermaid
classDiagram
    class ProfileUpdateTemplate {
        <<abstract>>
        -service: UserService
        -username
        +__init__(service, username)
        +executar()
        #_aplicar(user)*
    }

    class AlterarEmailTemplate {
        -novo_email
        +__init__(service, username, novo_email)
        #_aplicar(user)
    }

    class AlterarNomeTemplate {
        -novo_username
        +__init__(service, username, novo_username)
        #_aplicar(user)
    }

    class AlterarSenhaTemplate {
        -senha_atual
        -nova_senha
        +__init__(service, username, senha_atual, nova_senha)
        #_aplicar(user)
    }

    class UserService {
        +user_database: UserDataBase
        +session: Session
        +alterar_email(username, novo_email)
        +alterar_nome(username, novo_username)
        +alterar_senha(username, senha_atual, nova_senha)
        -_verificar_permissao(username)
    }

    class UserDataBase {
        +search_user(username)
        +update_username(username, novo_username)
    }

    class Session {
        +is_logged(username)
    }

    class User {
        +alterar_email(novo_email)
        +alterar_nome(novo_nome)
        +alterar_senha(nova_senha)
        +verificar_senha(tentativa_senha)
    }

    ProfileUpdateTemplate <|-- AlterarEmailTemplate
    ProfileUpdateTemplate <|-- AlterarNomeTemplate
    ProfileUpdateTemplate <|-- AlterarSenhaTemplate
    UserService ..> AlterarEmailTemplate : cria
    UserService ..> AlterarNomeTemplate : cria
    UserService ..> AlterarSenhaTemplate : cria
    ProfileUpdateTemplate --> UserService
    UserService --> UserDataBase
    UserService --> Session
    ProfileUpdateTemplate ..> User : aplica alteracao
```

## 3. Builder - Montagem de Escalacao

**Objetivo:** construir uma `Lineup` de forma controlada, validando quantidade de jogadores e capitao antes de criar o objeto final.

**Participantes do padrao:**

- `LineupBuilder`: builder responsavel por configurar rodada e jogadores antes do `build()`.
- `TeamFantasyService`: cliente que usa o builder para montar a escalacao.
- `Lineup`: produto criado pelo builder.
- `PlayerFantasy`: item usado na composicao da escalacao.

```mermaid
classDiagram
    class LineupBuilder {
        -__rodada
        -__jogadores: list~PlayerFantasy~
        +__init__()
        +com_rodada(rodada: int) LineupBuilder
        +com_jogadores(jogadores: list~PlayerFantasy~) LineupBuilder
        +build() Lineup
    }

    class TeamFantasyService {
        +montar_escalacao(user: User, rodada: int, jogadores: list~PlayerFantasy~)
    }

    class Lineup {
        -__rodada
        -__jogadores: list~PlayerFantasy~
        -__pontuacao
        +rodada
        +jogadores
        +pontuacao
    }

    class PlayerFantasy {
        +jogador
        +capitao
        +pontuacao
    }

    class User {
        +team_fantasy
    }

    class TeamFantasy {
        +escalacoes
    }

    TeamFantasyService ..> LineupBuilder : usa
    LineupBuilder ..> Lineup : constroi
    LineupBuilder --> PlayerFantasy : valida lista
    Lineup --> PlayerFantasy : contem
    TeamFantasyService --> User
    User --> TeamFantasy
    TeamFantasy --> Lineup : armazena
```
