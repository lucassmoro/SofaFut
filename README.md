# SofaFut

Arquitetura inicial em MVC para um fantasy game de futebol.

## Estrutura

```text
src/sofafut/
  models/         Entidades e objetos do dominio
  views/          Saida/apresentacao para o usuario
  controllers/    Entrada dos fluxos da aplicacao
  services/       Regras de negocio
  repositories/   Persistencia em memoria
  app.py          Composicao da aplicacao PySide6
  main.py         Ponto de entrada da aplicacao PySide6
  demo_console.py Ponto de entrada do demo antigo em console
  demo_console_app.py Composicao do demo antigo em console
```

## Como executar

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Execute a aplicacao:

```bash
python -m sofafut.main
```

O comando abre a janela de login/cadastro em PySide6.

Execute o demo antigo em console, se precisar validar a composicao MVC inicial:

```bash
python -m sofafut.demo_console
```

Os usuarios cadastrados pela janela ficam em `data/users.json`. As senhas sao armazenadas com hash PBKDF2, nunca em texto puro.

Depois do login, a janela principal abre com:

- aba `Jogos`, mostrando por padrao o dia de hoje da temporada atual;
- filtros para trocar temporada e dia;
- aba `Perfil`, para marcar times favoritos;
- aba `Favoritos`, mostrando apenas jogos dos times favoritos no dia selecionado.

Os favoritos ficam em `data/favorites.json`.

## Como validar sintaxe

```bash
python -m compileall src tests
python -m unittest discover -s tests
```

## Dados da API-Football

A chave da API fica no arquivo local `.env`, que e ignorado pelo Git. Use `.env.example` como modelo caso precise recriar o arquivo.

Para baixar as partidas do Brasileirao Serie A nas temporadas liberadas pelo plano gratuito:

```bash
source .venv/bin/activate
python -m sofafut.scripts.fetch_brasileirao
```

O CSV sera salvo em:

```text
data/brasileirao_2022_2024_partidas.csv
```

O script usa 1 requisicao por temporada no endpoint `fixtures` e mantem um contador local em `data/api_football_requests.json` para evitar ultrapassar o limite diario configurado.

Para baixar uma temporada especifica:

```bash
python -m sofafut.scripts.fetch_brasileirao --seasons 2024
```

## Dados do Sofascore

O Sofascore nao oferece uma API publica oficial garantida para este uso. O coletor abaixo usa endpoints internos do site, portanto pode quebrar ou mudar sem aviso.

Para baixar jogos e estatisticas da temporada atual do Brasileirao Serie A pelo Sofascore:

```bash
python -m sofafut.scripts.fetch_brasileirao_sofascore
```

O CSV separado sera salvo em:

```text
data/sofascore_brasileirao_2026_partidas.csv
```

Cada execucao sobrescreve o CSV da temporada, mantendo os dados mais recentes.
