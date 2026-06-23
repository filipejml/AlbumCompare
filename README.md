# Spotify Album Comparison

![Spotify Logo](https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg)

Aplicação web para comparar álbuns de um artista, mostrando as músicas comuns e exclusivas de cada álbum. Os dados são obtidos por meio da API do Spotify.

## Funcionalidades

- Pesquisar artistas diretamente na API do Spotify.
- Listar os álbuns de um artista.
- Comparar dois álbuns.
- Mostrar músicas comuns e exclusivas.
- Exibir capas, datas de lançamento, quantidade de faixas e popularidade.
- Reproduzir prévias disponibilizadas pelo Spotify.
- Abrir os álbuns diretamente no Spotify.

## Tecnologias

- Python
- Flask
- Requests
- python-dotenv
- API Web do Spotify
- HTML5, CSS3, Bootstrap e jQuery

## Pré-requisitos

- Python 3 instalado.
- Uma conta no [Spotify for Developers](https://developer.spotify.com/).
- Um aplicativo criado no Spotify Developer Dashboard para obter o Client ID e o Client Secret.

## Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/filipejml/AlbumCompare.git
   cd AlbumCompare
   ```

2. Crie e ative um ambiente virtual.

   No Windows:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   No Linux ou macOS:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r app/requirements.txt
   ```

4. Crie a configuração local a partir do exemplo.

   No Windows:

   ```powershell
   Copy-Item app/.env.example app/.env
   ```

   No Linux ou macOS:

   ```bash
   cp app/.env.example app/.env
   ```

5. Preencha `app/.env` com suas credenciais:

   ```env
   SPOTIFY_CLIENT_ID=seu_client_id
   SPOTIFY_CLIENT_SECRET=seu_client_secret
   SPOTIFY_MARKET=BR
   FLASK_DEBUG=false
   ```

6. Execute a aplicação:

   ```powershell
   cd app
   python app.py
   ```

A aplicação estará disponível em `http://127.0.0.1:5000`.

Para desenvolvimento local, você pode definir `FLASK_DEBUG=true`. Não habilite o modo debug em produção.

`SPOTIFY_MARKET` deve usar um código de país ISO de duas letras, como `BR`, `US` ou `PT`.

## Como usar

1. Digite o nome de um artista.
2. Selecione o artista na lista de resultados.
3. Escolha dois álbuns.
4. Clique em **Compare Albums**.
5. Confira as faixas comuns e exclusivas de cada álbum.

## Segurança

O arquivo `app/.env` contém credenciais locais e não deve ser enviado ao Git. Use somente `app/.env.example` como modelo.

Se credenciais reais já tiverem sido publicadas no histórico do repositório, revogue-as no Spotify Developer Dashboard e gere novas credenciais.

## Licença

Este projeto é disponibilizado sob a licença MIT.

## Autor

Filipe Lopes — [GitHub](https://github.com/filipejml)
