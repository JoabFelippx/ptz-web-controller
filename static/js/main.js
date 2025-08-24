document.addEventListener('DOMContentLoaded', () => {
    // --- Configuração dos Elementos e Variáveis ---
    const controlPanel = document.getElementById('ptz-control-panel');
    const cameraId = document.getElementById('camera-id')?.value;
    const statusMessageEl = document.getElementById('status-message');
    const videoStreamEl = document.getElementById('video-stream-image');

    if (!cameraId) {
        return;
    }

    // --- Lógica de WebSocket para o Stream de Vídeo (sem alterações) ---
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

    // --- Função ÚNICA para enviar todos os comandos PTZ ---
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

    // --- Função de UI (sem alterações) ---
    const displayStatus = (message, type = 'info') => {
        if (!statusMessageEl) return;
        statusMessageEl.innerHTML = `<div class="alert alert-${type}" role="alert">${message}</div>`;
        setTimeout(() => { statusMessageEl.innerHTML = ''; }, 4000);
    };

    // --- Event Listener ÚNICO para todos os botões ---
    if (controlPanel) {
        controlPanel.addEventListener('click', (event) => {
            // Delegação de evento: captura cliques em qualquer botão com a classe .ptz-btn
            const button = event.target.closest('.ptz-btn');
            if (button && button.dataset.command) {
                sendPtzCommand(button.dataset.command);
            }
        });
    }
});