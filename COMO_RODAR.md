# Como rodar o SofaFut

Este guia mostra como executar o projeto no Windows PowerShell e no terminal Linux Fedora.

## Windows PowerShell

Abra o PowerShell na pasta do projeto:

```powershell
cd C:\Users\Usuario\SofaFut
```

Crie e ative o ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativacao do ambiente virtual, execute uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Depois ative novamente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependencias:

```powershell
python -m pip install -r requirements.txt
```

Execute o programa em modo grafico:

```powershell
python -m src.main
```

## Linux Fedora

Abra o terminal na pasta do projeto:

```bash
cd /caminho/para/SofaFut
```

Garanta que Python, pip e suporte a ambiente virtual estejam instalados:

```bash
sudo dnf install python3 python3-pip python3-virtualenv
```

Crie e ative o ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependencias:

```bash
python -m pip install -r requirements.txt
```

Execute o programa em modo grafico:

```bash
python -m src.main
```

## Modo console

O modo console roda no terminal, sem abrir a interface grafica. Ele executa um fluxo automatico de teste do sistema.

No Windows PowerShell:

```powershell
$env:SOFAFUT_VIEW="console"
python -m src.main
```

Para voltar ao modo grafico na mesma sessao:

```powershell
Remove-Item Env:\SOFAFUT_VIEW
python -m src.main
```

No Linux Fedora:

```bash
SOFAFUT_VIEW=console python -m src.main
```

## Chave da API Football

Algumas telas e fluxos usam dados da API Football. Para baixar dados novos, configure a variavel de ambiente `API_FOOTBALL_KEY`.

No Windows PowerShell:

```powershell
$env:API_FOOTBALL_KEY="sua_chave_aqui"
python -m src.main
```

No Linux Fedora:

```bash
export API_FOOTBALL_KEY="sua_chave_aqui"
python -m src.main
```

Sem essa chave, o sistema pode funcionar apenas com dados ja existentes em cache.
