# Controlador de Câmeras PTZ com Flask
![Status: Work in Progress](https://img.shields.io/badge/Status-Work%20in%20Progress-yellow)

Uma aplicação web simples construída com Python e Flask para controlar as múltiplas câmeras PTZ (Pan-Tilt-Zoom) do [LabSEA](https://github.com/Lab-SEA) através de uma interface web. A comunicação com as câmeras é feita via (pub/sub) utilizando a biblioteca `is-wire` para abstração da comunicação com o broker, e o stream de vídeo é exibido em tempo real na interface.


## Funcionalidades

-   **Interface Web Responsiva:** Controlar as câmeras PTZ do [LabSEA](https://github.com/Lab-SEA).
-   **Visualização em Tempo Real:** Stream de vídeo da câmera selecionada diretamente na página de controle, utilizando WebSockets.
-   **Controles PTZ Completos:** Comandos de Pan (Esquerda/Direita), Tilt (Cima/Baixo) e Zoom (In/Out) através de botões intuitivos.
-   **Gerenciamento de Múltiplas Câmeras:** Cadastre novas câmeras e selecione qual deseja controlar a partir de uma lista.
-   **Persistência Simples:** As informações das câmeras são salvas em um arquivo `cameras.json`, facilitando o backup e a edição.
-   **Arquitetura Modular:** O código é organizado com o backend (Flask) e o frontend (HTML/CSS/JS) devidamente separados.

## Tecnologias Utilizadas

-   **Backend:**
    -   [Python 3](https://www.python.org/)
    -   [Flask](https://flask.palletsprojects.com/)
    -   [Flask-SocketIO](https://flask-socketio.readthedocs.io/) para comunicação em tempo real.
    -   [Eventlet](http://eventlet.net/) como servidor assíncrono.
    -   [is-wire](https://github.com/labviros/is-wire) para comunicação com o broker de mensagens.
    -   [is-msgs](https://github.com/labvisio/is-msgs) mensagens padronizadas

-   **Frontend:**
    -   HTML5, CSS3, JavaScript

-   **Infraestrutura:**
    -   Protocolo **AMQP** (ex: [RabbitMQ](https://www.rabbitmq.com/)) como broker de mensagens para os comandos PTZ e recebimento dos frames.

## Como Rodar o Projeto 

Você pode rodar esta aplicação de duas maneiras: usando Docker ou manualmente em um ambiente local.

### Opção 1: Rodar com um único comando Docker (Mais Rápido)

Este método usa a imagem pré-construída do Docker Hub e é ideal para rodar a aplicação rapidamente sem clonar o repositório.

1.  **Crie o arquivo `cameras.json`:**
    - Em uma pasta no seu computador, crie um arquivo `cameras.json`. Você pode começar com uma lista vazia: `[]`.

2.  **Execute o container:**
    - Abra um terminal **nessa mesma pasta** e rode o comando:
    ```bash
    docker run -d -p 5000:5000 --name ptz_app -v "$(pwd)/cameras.json:/app/cameras.json" joabfelippe30/web-ptz-controller:v1
    ```
    *(No Command Prompt do Windows, use `"%cd%"` no lugar de `$(pwd)`)*

3.  **Acesse a aplicação** em `http://localhost:5000`.


### Opção 2: Usando Docker Compose

### Pré-requisitos:
- Docker
- Docker Compose

### Passos:

1. Clone o repositório e navegue até a pasta::
    ```bash
    git clone https://github.com/JoabFelippx/ptz-web-controller.git

    cd ptz-web-controller
    ```
2. Configure o arquivo json:

    -   Certifique-se de que o arquivo `cameras.json` existe na raiz do projeto e contém as informações das suas câmeras (o aquivo pode estar vazio).  Se o arquivo não existir, você pode criá-lo com uma lista vazia `[]`.
3. Inicie a aplicação com Dcoker Compose:

    Com esse comando você irá construir a imagem Docker (se ainda não existir) e iniciar o container em segundo plano

    ```bash
    docker-compose up -d
    ```

4. Acesse a aplicação:

    - Abra seu navegador e acesse: `http://localhost:5000`

5. Para parar a aplicação:
    ```bash
    docker-compose down
    ```
### Opção 3: Rodando manualmente
Use essa opção caso queira configurar o ambiente manualmente.
### Pré-requisitos:
- Python 3.9 ou superior
- Pip

### Passos:
1. Clone o repositório e navegue até a pasta:
    ```bash
    git clone https://github.com/JoabFelippx/ptz-web-controller.git

    cd ptz-web-controller
    ```
2. Crie e ative um ambiente virtual:

    - Para Linux 
        ```bash
        python3 -m venv venv
        source venv/bin/activate  
        ```
    - Para Windows
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4. Configure suas câmeras:
    Edite o arquivo `cameras.json` com as informações das duas câmeras (pode deixar o arquivo com uma lista vazia `[]`).

5. Inicie o servidor Flask:
    ```bash
    python app.py
    ```
6. Acesse a aplicação:
    - Abra seu navegador e acesse: `http://localhost:5000`


## Uso

1.  **Acesse a página inicial** para ver a lista de câmeras.

2.  Clique em **"Registrar Nova Câmera"** para adicionar uma nova câmera, preenchendo o Nome, URI do Broker e Gateway ID.

3.  Na página inicial, **clique no card da câmera** que deseja controlar.

4.  Na página de controle, **use os botões** para movimentar a câmera, aplicar zoom ou retorná-la à posição inicial (Home).

5.  Para obter as coordenadas atuais, clique em **"Obter Posição Atual"**.

6. Para excluir uma câmera, clique no botão **"Remover"** no card correspondente na página inicial e confirme a ação.

## Estrutura do Projeto
```plaintext
/ptz-web-controller
|
|-- static/
|   |-- css/
|   |   |-- style.css
|   |-- images/
|   |   |-- LOGO-PROV-SEM-FUNDO.ico
|   |   |-- LOGO-PROV-SEM-FUNDO.png
|   |   |-- LOGO.png
|   |   |-- OLHO-PEIXE-CAMERA.ico
|   |-- js/
|       |-- index.js
|       |-- main.js
|
|-- templates/
|   |-- base.html
|   |-- control.html
|   |-- index.html
|   |-- register.html
|
|-- app.py
|-- camera_controller.py
|-- cameras.json
|-- docker-compose.yml
|-- Dockerfile
|-- README.md
|-- requirements.txt
|-- streamChannel.py
