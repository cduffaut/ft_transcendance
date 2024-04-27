let ws; // Variable globale pour la connexion WebSocket

// Fonction pour initialiser la connexion WebSocket
function initializeWebSocket() {
    const url = `ws://127.0.0.1:8001/wsGame/1/`; // URL du serveur WebSocket
    ws = new WebSocket(url);

    ws.onopen = () => {
        console.log("Connexion établie.");
        attachKeydownListener();
    };

    ws.onmessage = (event) => {
        console.log("Message reçu : " + event.data);
    };

    ws.onclose = () => {
        console.log("Connexion fermée.");
    };

    ws.onerror = (error) => {
        console.log("Erreur: ", error);
    };
}

// Fonction pour envoyer des messages via WebSocket
function sendMessage(action) {
    const playerID = document.getElementById('playerID').value; // Suppose que playerID est toujours présent
    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log(`sending message: "${playerID + action}" to ws://127.0.0.1:8001/wsGame/1/`);
        ws.send(playerID + action);
    } else
        console.log("La connexion WebSocket n'est pas ouverte ou disponible.");
}

// Fonction pour attacher l'écouteur d'événements keydown
function attachKeydownListener() {
    document.addEventListener('keydown', (event) => {
        if (event.key === "ArrowUp")
            sendMessage("u");
        else if (event.key === "ArrowDown")
            sendMessage("d");
    });
}

initializeWebSocket();
