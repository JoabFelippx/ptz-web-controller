document.addEventListener('DOMContentLoaded', () => {
    const gridContainer = document.querySelector('.camera-grid-container');

    if (gridContainer) {
        gridContainer.addEventListener('click', async (event) => {
            
            const deleteButton = event.target.closest('.delete-camera-btn');
            
            if (!deleteButton) {
                return;
            }

            const camId = deleteButton.dataset.camId;
            const camCard = deleteButton.closest('.camera-card');
            const camName = camCard.querySelector('.camera-card-name').textContent;

           
            if (confirm(`Tem certeza que deseja excluir a câmera "${camName}"?`)) {
                try {
                    const response = await fetch(`/api/delete_camera/${camId}`, {
                        method: 'DELETE',
                    });

                    const result = await response.json();

                    if (response.ok) {
                       
                        camCard.style.transition = 'opacity 0.5s ease';
                        camCard.style.opacity = '0';
                        setTimeout(() => camCard.remove(), 500);
            
                        alert(result.message); 
                    } else {
                        throw new Error(result.message);
                    }
                } catch (error) {
                    console.error('Falha ao excluir a câmera:', error);
                    alert(`Erro ao excluir: ${error.message}`);
                }
            }
        });
    }
});
