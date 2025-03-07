
![Spotify Logo](https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg)
Spotify Album Comparison
_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________
Spotify Album Comparison é uma aplicação web que permite comparar álbuns de um artista, mostrando as músicas comuns e únicas entre eles. A aplicação utiliza a API do Spotify para buscar informações sobre artistas, álbuns e músicas.
_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________
Funcionalidades
🔍 Pesquisar artistas diretamente na API do Spotify.

🎵 Listar álbuns de um artista.

🎶 Comparar dois álbuns, mostrando:

Músicas comuns.

Músicas únicas de cada álbum.

🖼️ Exibir capas dos álbuns e fotos dos artistas.

📄 Paginação para álbuns com muitas músicas.

🏠 Botão "Back to Home" para retornar à página inicial.
_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________
Tecnologias Utilizadas
Back-end:

Python

Flask (Framework web)

API do Spotify

Front-end:

HTML5

CSS3 (Bootstrap)

JavaScript (jQuery)

Ferramentas:

Git

Pip (Gerenciador de pacotes Python)
_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________
Pré-requisitos
Antes de começar, você precisará:

Uma conta no Spotify Developer.

Criar um aplicativo no Spotify Developer Dashboard para obter as credenciais (Client ID e Client Secret).

Python 3.x instalado no seu sistema.
_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________
Instalação
Siga os passos abaixo para configurar e executar o projeto localmente.

1. Clonar o Repositório
git clone https://github.com/seu-usuario/spotify-album-comparison.git
cd spotify-album-comparison

2. Criar e Ativar um Ambiente Virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

4. Instalar as Dependências
pip install -r requirements.txt

5. Configurar as Credenciais do Spotify
Crie um arquivo .env na raiz do projeto e adicione suas credenciais do Spotify:
SPOTIFY_CLIENT_ID=seu_client_id
SPOTIFY_CLIENT_SECRET=seu_client_secret

6. Executar a Aplicação
python app.py


A aplicação estará disponível em: http://127.0.0.1:5000.
_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________
Como Usar
Na página inicial, digite o nome de um artista no campo de busca.

Selecione um artista na lista de resultados.

Escolha dois álbuns para comparar.

Clique em "Compare Albums" para ver os resultados.

Na página de resultados, você verá:

As capas dos álbuns.

As músicas comuns.

As músicas únicas de cada álbum.

Use os botões de paginação para navegar entre as músicas (caso haja muitas).

Clique em "Back to Home" para retornar à página inicial.
_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________
Exemplo de Uso
Pesquise por "The Beatles".

Selecione os álbuns "Abbey Road" e "Let It Be".

Veja as músicas comuns e únicas entre os dois álbuns.
_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________
Licença
Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________
Autor
Filipe Lopes

GitHub: filipejml
_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________
Agradecimentos
Spotify por fornecer uma API incrível.

Bootstrap por facilitar o design da interface.

Flask por ser um framework web simples e poderoso.
