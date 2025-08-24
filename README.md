# 📹 Controlador de Câmeras PTZ com Flask
![Status: Work in Progress](https://img.shields.io/badge/Status-Work%20in%20Progress-yellow)

Uma aplicação web simples construída com Python e Flask para controlar múltiplas câmeras PTZ (Pan-Tilt-Zoom) através de uma interface amigável. A comunicação com as câmeras é feita via (pub/sub) utilizando a biblioteca `is-wire` para abstração da comunicação com o broker, e o stream de vídeo é exibido em tempo real na interface.


## ✨ Funcionalidades

-   **Interface Web Responsiva:** Controlar as câmeras PTZ do [LabSEA](https://github.com/Lab-SEA).
-   **Visualização em Tempo Real:** Stream de vídeo da câmera selecionada diretamente na página de controle, utilizando WebSockets.
-   **Controles PTZ Completos:** Comandos de Pan (Esquerda/Direita), Tilt (Cima/Baixo) e Zoom (In/Out) através de botões intuitivos.
-   **Gerenciamento de Múltiplas Câmeras:** Cadastre novas câmeras e selecione qual deseja controlar a partir de uma lista.
-   **Persistência Simples:** As informações das câmeras são salvas em um arquivo `cameras.json`, facilitando o backup e a edição.
-   **Arquitetura Modular:** O código é organizado com o backend (Flask) e o frontend (HTML/CSS/JS) devidamente separados.

## 🛠️ Tecnologias Utilizadas

-   **Backend:**
    -   [Python 3](https://www.python.org/)
    -   [Flask](https://flask.palletsprojects.com/)
    -   [Flask-SocketIO](https://flask-socketio.readthedocs.io/) para comunicação em tempo real.
    -   [Eventlet](http://eventlet.net/) como servidor assíncrono.
    -   [is-wire](https://github.com/labviros/is-wire) para comunicação com o broker de mensagens.
    -   [is-msgs](https://github.com/labvisio/is-msgs) mensagens padronizadas

-   **Frontend:**
    -   HTML5, CSS3, JavaScript
    -   [Bootstrap 5](https://getbootstrap.com/) para a interface e responsividade.
    -   [Bootstrap Icons](https://icons.getbootstrap.com/)
    -   [Socket.IO Client](https://socket.io/docs/v4/client-api/)

-   **Infraestrutura:**
    -   Protocolo **AMQP** (ex: [RabbitMQ](https://www.rabbitmq.com/)) como broker de mensagens para os comandos PTZ e recebimento dos frames.

## 📂 Estrutura do Projeto

```plaintext
/ptz-web-controller
|
|-- app.py                   
|-- camera_controller.py     
|-- cameras.json            
|-- requirements.txt        
|-- README.md                
|
|-- templates/               
|   |-- base.html
|   |-- index.html
|   |-- register.html
|   |-- control.html
|
|-- static/                  
|   |-- css/
|   |   |-- style.css
|   |-- js/
|       |-- main.js
