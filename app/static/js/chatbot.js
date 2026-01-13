/* app/static/js/chatbot.js - VERSIÓN MVC FINAL (Texto Definitivo) */

console.log("⚡ Cargando Chatbot V5...");

const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// 1. MENSAJE DE BIENVENIDA
const WELCOME_MESSAGE = `
    ¡Hola! Me llamo Service-Ball, ¡y estoy aquí para ayudarte con tu aventura Pokemon! Ahora mismo dispongo de las siguientes funcionalidades: 
    <br><br>
    1 - Dime un Pokemon y te digo sus debilidades y fortalezas. <br>
    2 - ¿Te interesa la evolución de tu Pokemon? Dime el Pokemon del que quieras saber sus evoluciones. <br>
    3 - Dime el Pokemon del que quieras saber su región. <br>
    4 - El amor está en el aire... Dime dos Pokemon y te digo su compatibilidad amorosa.
    <br><br>
    <small>
    <b>COMO USARME:</b><br>
    • Para opciones 1, 2 y 3: <b>Num-Pokemon</b> (Ej: <b>1-Pikachu</b>)<br>
    • Para opción 4: <b>4-Pokemon1-Pokemon2</b> (Ej: <b>4-Bulbasaur-Charmander</b>)
    </small>
`;

// 2. INICIO
if (chatMessages && chatMessages.children.length === 0) {
    runWelcomeAnimation();
}

// --- FUNCIONES VISUALES ---
function runWelcomeAnimation() {
    const typingId = showTypingIndicator(chatMessages);
    // Esperamos 1.5s para dar efecto de "pensando"
    setTimeout(() => {
        removeTypingIndicator(typingId);
        addMessage(WELCOME_MESSAGE, 'bot');
    }, 1500);
}

function showTypingIndicator(container) {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.className = 'message bot';
    div.id = id;
    div.innerHTML = '<div class="typing-indicator">...</div>'; 
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) element.remove();
}

function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    div.innerHTML = `<div class="message-content">${text}</div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// --- LÓGICA DE ENVÍO MVC ---
async function handleUserMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    // 1. Pintamos mensaje usuario
    addMessage(text, 'user');
    messageInput.value = '';

    // 2. Indicador escribiendo
    const loadingId = showTypingIndicator(chatMessages);

    try {
        // 3. Enviamos al Controller
        const response = await fetch('/chatbot/procesar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mensaje: text })
        });
        
        const data = await response.json();
        
        removeTypingIndicator(loadingId);
        
        // 4. Mostramos respuesta
        if (data.error) {
            addMessage(`❌ ${data.msg}`, 'bot');
        } else {
            addMessage(data.respuesta, 'bot');
        }

    } catch (error) {
        removeTypingIndicator(loadingId);
        addMessage("Error de conexión. Inténtalo de nuevo.", 'bot');
    }
}

// Eventos
if(sendButton && messageInput){
    sendButton.addEventListener('click', handleUserMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleUserMessage();
    });
}