document.addEventListener('DOMContentLoaded', () => {
    // --- Configuração dos Elementos e Variáveis ---
    const controlPanel = document.getElementById('ptz-control-panel');
    const cameraId = document.getElementById('camera-id')?.value;
    const statusMessageEl = document.getElementById('status-message');
    const videoStreamEl = document.getElementById('video-stream-image');

    if (!cameraId) {
        return;
    }

    // --- Lógica de WebSocket para o Stream de Vídeo ---
    const socket = io('/camera');

    socket.on('connect', () => {
        socket.emit('start_stream', { cam_id: parseInt(cameraId, 10) });
    });

    socket.on('video_frame', (data) => {
        console.log('Recebi um frame!', data);
        videoStreamEl.src = 'data:image/jpeg;base64,' + data.image;
    });

    socket.on('disconnect', () => {
        console.log('Desconectado do servidor WebSocket.');
    });

    // --- Lógica para o Botão de Obter Informações ---
    const getInfoBtn = document.getElementById('get-info-btn');
    const cameraInfoDisplay = document.getElementById('camera-info-display');
    const infoX = document.getElementById('info-x');
    const infoY = document.getElementById('info-y');
    const infoZ = document.getElementById('info-z');

    if (getInfoBtn) {
        getInfoBtn.addEventListener('click', async () => {
            displayStatus('Buscando informações...', 'info');
            cameraInfoDisplay.style.display = 'none'; // Esconde o resultado anterior

            try {
                const response = await fetch(`/api/get_camera_info/${cameraId}`);
                const result = await response.json();

                if (response.ok) {
                    displayStatus(result.message, 'success');
                    
                    // Atualiza os valores na tela
                    infoX.textContent = result.data.x;
                    infoY.textContent = result.data.y;
                    infoZ.textContent = result.data.z;

                    // Mostra a área de informações
                    cameraInfoDisplay.style.display = 'block';
                } else {
                    throw new Error(result.message);
                }
            } catch (error) {
                console.error('Falha ao obter informações:', error);
                displayStatus(`Falha ao obter informações: ${error.message}`, 'danger');
            }
        });
    }

    // --- Função para Enviar Comandos PTZ ---
    const sendPtzCommand = async (command) => {
        displayStatus('Enviando comando...', 'info');
        try {
            const response = await fetch('/api/ptz_command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cam_id: parseInt(cameraId, 10),
                    command: command,
                }),
            });
            const result = await response.json();
            if (response.ok) {
                displayStatus(result.message, 'success');
            } else {
                throw new Error(result.message || 'Erro no servidor.');
            }
        } catch (error) {
            console.error(`Falha ao enviar comando:`, error);
            displayStatus(`Falha ao enviar comando: ${error.message}`, 'danger');
        }
    };

    // --- Função de UI para Exibir Status ---
    const displayStatus = (message, type = 'info') => {
        if (!statusMessageEl) return;
        statusMessageEl.innerHTML = `<div class="alert alert-${type}" role="alert">${message}</div>`;
        setTimeout(() => { statusMessageEl.innerHTML = ''; }, 4000);
    };

    // --- Event Listener para os Botões PTZ ---
    if (controlPanel) {
        controlPanel.addEventListener('click', (event) => {
            const button = event.target.closest('.ptz-btn');
            if (button && button.dataset.command) {
                sendPtzCommand(button.dataset.command);
            }
        });
    }
});
