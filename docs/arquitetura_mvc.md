# Arquitetura MVC

O projeto foi organizado em MVC com uma camada de servicos para manter as regras de negocio fora dos controllers.

## Model

Representa os dados centrais do SofaFut:

- `Usuario`
- `TimeFantasy`
- `Clube`
- `Jogador`, `JogadorLinha`, `Goleiro`
- `Partida`
- `EstatisticaJogador`
- `Escalacao` e `JogadorEscalacao`
- `PontuacaoRodada`
- `TransacaoMercado`
- `Favorito`

## View

Responsavel por apresentar informacoes. A implementacao inicial usa textos simples para console, mas a camada pode ser trocada por HTML, templates ou API sem alterar o dominio.

## Controller

Recebe chamadas da interface e coordena servicos:

- `AuthController`
- `PerfilController`
- `MercadoController`
- `EscalacaoController`
- `EstatisticasController`
- `RankingController`

## Services

Concentram regras de negocio:

- autenticacao e hash de senha
- validacao de saldo
- compra e venda de jogadores
- escalação com capitao
- calculo de pontos
- ranking com desempate por patrimonio

## Repositories

A primeira versao usa repositorios em memoria. Essa decisao mantem o codigo simples para estudo e facilita trocar por banco de dados depois.
