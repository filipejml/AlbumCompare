# Spotify Album Comparison

![Spotify Logo](https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg)

Aplicação web em Flask para pesquisar artistas no Spotify e comparar dois de seus álbuns. O resultado apresenta informações dos álbuns e separa as faixas em comuns e exclusivas.

## Funcionalidades

- Pesquisa de artistas pela API Web do Spotify.
- Listagem paginada de álbuns, singles e compilações.
- Comparação entre dois álbuns diferentes.
- Exibição de faixas comuns e exclusivas.
- Comparação tolerante a diferenças de caixa, acentos, pontuação, espaços e créditos `feat.`.
- Distinção entre versões de estúdio, ao vivo, acústicas, remixes e remasterizações.
- Exibição de capa, data de lançamento, número de faixas e popularidade.
- Reprodução da prévia da faixa quando disponibilizada pelo Spotify.
- Link direto para cada álbum no Spotify.
- Tratamento de credenciais ausentes, falhas de rede e erros da API.

## Tecnologias

- Python 3
- Flask
- Requests
- python-dotenv
- API Web do Spotify
- HTML5, CSS3, Bootstrap e jQuery

## Estrutura do projeto

```text
AlbumCompare/
├── app/
│   ├── app.py                 # Aplicação Flask e rotas
│   ├── spotify_service.py     # Comunicação com a API do Spotify
│   ├── track_comparison.py    # Regras de equivalência entre músicas
│   ├── requirements.txt       # Dependências Python
│   ├── .env.example           # Modelo das variáveis de ambiente
│   ├── static/
│   │   └── style.css
│   └── templates/
│       ├── index.html
│       ├── results.html
│       └── error.html
├── tests/
│   ├── test_app.py
│   ├── test_spotify_service.py
│   └── test_track_comparison.py
├── .gitignore
└── README.md
```

## Pré-requisitos

Antes de começar, instale ou providencie:

- Python 3.10 ou mais recente.
- Git, caso queira clonar o repositório.
- Uma conta no [Spotify for Developers](https://developer.spotify.com/).
- Um aplicativo no Spotify Developer Dashboard para obter o **Client ID** e o **Client Secret**.

Confira a instalação do Python:

```powershell
python --version
```

No Linux ou macOS, o comando pode ser:

```bash
python3 --version
```

## Diretório usado nos comandos

Exceto quando uma seção disser o contrário, todos os comandos deste README devem ser executados na raiz do projeto:

```text
AlbumCompare/
```

No ambiente apresentado neste repositório, a raiz corresponde a:

```text
C:\xampp\htdocs\AlbumCompare
```

No PowerShell, você pode entrar nela com:

```powershell
cd C:\xampp\htdocs\AlbumCompare
```

Não é necessário entrar na pasta `app` para instalar dependências, configurar o `.env`, executar a aplicação ou rodar os testes.

## Instalação no Windows com PowerShell

### 1. Clonar e acessar o projeto

Se ainda não possui o projeto:

```powershell
git clone https://github.com/filipejml/AlbumCompare.git
cd AlbumCompare
```

Se o projeto já está em `C:\xampp\htdocs\AlbumCompare`:

```powershell
cd C:\xampp\htdocs\AlbumCompare
```

### 2. Criar o ambiente virtual

Execute na raiz `AlbumCompare`:

```powershell
python -m venv venv
```

### 3. Ativar o ambiente virtual

```powershell
.\venv\Scripts\Activate.ps1
```

Quando estiver ativo, o terminal normalmente exibirá `(venv)` antes do caminho.

Se o PowerShell bloquear a ativação de scripts, execute isto somente na sessão atual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

Ainda na raiz:

```powershell
python -m pip install --upgrade pip
python -m pip install -r app\requirements.txt
```

### 5. Criar o arquivo de configuração

```powershell
Copy-Item app\.env.example app\.env
```

Abra `app\.env` e substitua os valores de exemplo pelas credenciais do Spotify:

```env
SPOTIFY_CLIENT_ID=seu_client_id
SPOTIFY_CLIENT_SECRET=seu_client_secret
SPOTIFY_MARKET=BR
FLASK_DEBUG=false
```

### 6. Executar a aplicação

Na raiz `AlbumCompare`, com o ambiente virtual ativo:

```powershell
python app\app.py
```

Abra no navegador:

```text
http://127.0.0.1:5000
```

Para encerrar o servidor, pressione `Ctrl+C` no terminal.

Para sair do ambiente virtual:

```powershell
deactivate
```

## Instalação no Linux ou macOS

Todos os comandos abaixo também partem da raiz `AlbumCompare`.

### 1. Clonar e acessar o projeto

```bash
git clone https://github.com/filipejml/AlbumCompare.git
cd AlbumCompare
```

### 2. Criar e ativar o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
python -m pip install --upgrade pip
python -m pip install -r app/requirements.txt
```

### 4. Criar e preencher o `.env`

```bash
cp app/.env.example app/.env
```

Edite `app/.env`:

```env
SPOTIFY_CLIENT_ID=seu_client_id
SPOTIFY_CLIENT_SECRET=seu_client_secret
SPOTIFY_MARKET=BR
FLASK_DEBUG=false
```

### 5. Executar a aplicação

```bash
python app/app.py
```

Depois, acesse `http://127.0.0.1:5000`.

## Variáveis de ambiente

O arquivo usado pela aplicação é `app/.env`.

| Variável | Obrigatória | Exemplo | Finalidade |
|---|---:|---|---|
| `SPOTIFY_CLIENT_ID` | Sim | `abc123` | Identifica o aplicativo criado no Spotify. |
| `SPOTIFY_CLIENT_SECRET` | Sim | `xyz456` | Autentica o aplicativo no Spotify. |
| `SPOTIFY_MARKET` | Não | `BR` | Define o catálogo regional. O padrão é `BR`. |
| `FLASK_DEBUG` | Não | `false` | Habilita o modo de desenvolvimento quando definido como `true`. |
| `LOG_LEVEL` | Não | `INFO` | Controla o nível dos logs, como `DEBUG`, `INFO` ou `WARNING`. |

`SPOTIFY_MARKET` deve ser um código ISO de país com duas letras, como `BR`, `US` ou `PT`.

Use `FLASK_DEBUG=true` somente durante o desenvolvimento local. Não habilite o modo debug em produção.

## Como usar a aplicação

1. Inicie o servidor e abra `http://127.0.0.1:5000`.
2. Digite ao menos três caracteres do nome de um artista.
3. Aguarde os resultados e clique no artista desejado.
4. A aplicação carregará os álbuns disponíveis para o mercado configurado.
5. Escolha um álbum no campo **Album 1**.
6. Escolha um álbum diferente no campo **Album 2**.
7. Clique em **Compare Albums**.
8. Na página de resultados, consulte:
   - dados e capas dos dois álbuns;
   - músicas presentes nos dois álbuns;
   - músicas exclusivas do primeiro álbum;
   - músicas exclusivas do segundo álbum;
   - prévias de áudio disponíveis;
   - links para abrir os álbuns no Spotify.
9. Use **Voltar ao Início** para realizar outra comparação.

O Spotify nem sempre fornece uma prévia de áudio. Nesses casos, a aplicação informa que o trecho não está disponível.

### Como as músicas são comparadas

A aplicação primeiro considera o identificador da faixa fornecido pelo Spotify. Quando os identificadores são diferentes ou não estão disponíveis, utiliza uma assinatura normalizada do título.

Essa normalização:

- ignora diferenças entre maiúsculas e minúsculas;
- remove diferenças de acentuação;
- uniformiza pontuação e espaços;
- ignora créditos como `feat.`, `featuring` e `ft.` no título;
- reconhece formas equivalentes de indicar uma remasterização, como `2009 Remaster` e `Remastered 2009`;
- preserva qualificadores relevantes para não considerar automaticamente uma versão ao vivo, acústica, remix ou demo como igual à versão de estúdio;
- usa artista principal e duração, quando disponíveis, para reduzir falsos resultados entre músicas diferentes com o mesmo nome.

Faixas duplicadas são comparadas individualmente. Por exemplo, duas ocorrências de uma música em um álbum e apenas uma no outro resultam em uma ocorrência comum e uma exclusiva.

## Executar os testes

Com o ambiente virtual ativo e estando na raiz `AlbumCompare`:

No Windows:

```powershell
python -m unittest discover -s tests -v
```

No Linux ou macOS:

```bash
python -m unittest discover -s tests -v
```

Os testes usam simulações da API e não precisam consumir suas credenciais reais do Spotify.

## Execuções posteriores

Depois da primeira instalação, não é necessário recriar o ambiente virtual ou reinstalar as dependências a cada execução.

No Windows:

```powershell
cd C:\xampp\htdocs\AlbumCompare
.\venv\Scripts\Activate.ps1
python app\app.py
```

No Linux ou macOS:

```bash
cd /caminho/para/AlbumCompare
source venv/bin/activate
python app/app.py
```

## Solução de problemas

### `No module named flask`, `requests` ou `dotenv`

O ambiente virtual provavelmente não está ativo ou as dependências não foram instaladas. Na raiz do projeto:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r app\requirements.txt
```

### `As credenciais do Spotify não estão configuradas`

Confira se:

- o arquivo está em `app/.env`, e não na raiz;
- `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET` foram preenchidos;
- não há aspas ou espaços extras nos valores;
- a aplicação foi reiniciada após alterar o arquivo.

### Falha de autenticação no Spotify

Confirme as credenciais no Spotify Developer Dashboard. Se elas já foram publicadas em um repositório, revogue-as e gere novas.

### Nenhum álbum aparece

Verifique:

- se o artista selecionado possui lançamentos;
- se `SPOTIFY_MARKET` contém um país válido;
- se os lançamentos estão disponíveis naquele mercado;
- se o terminal exibe alguma mensagem de erro da API.

### Porta 5000 já está sendo usada

Encerre outro servidor Flask com `Ctrl+C` ou identifique o processo que está ocupando a porta antes de iniciar novamente.

### Recriar um ambiente virtual com problema

Com o servidor parado, remova manualmente a pasta `venv`, crie o ambiente novamente e reinstale as dependências:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r app\requirements.txt
```

## Segurança

- Nunca envie `app/.env` para o Git.
- O repositório deve conter somente `app/.env.example`.
- Não compartilhe o Client Secret em capturas de tela, logs ou mensagens.
- Se uma credencial real já foi publicada, removê-la do arquivo atual não basta: revogue-a no Spotify Developer Dashboard e gere outra.

## Licença

Este projeto é disponibilizado sob a licença MIT.

## Autor

Filipe Lopes — [GitHub](https://github.com/filipejml)
