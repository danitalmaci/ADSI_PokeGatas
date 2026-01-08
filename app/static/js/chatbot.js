/* app/static/js/chatbot.js - VERSIÓN DEFINITIVA V2 */

console.log("⚡ Cargando Chatbot V2...");

// 1. Referencias directas (sin DOMContentLoaded)
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const WELCOME_MESSAGE = `
    ¡Hola! Me llamo Service-Ball, ¡y estoy aquí para ayudarte con tu aventura Pokemon! Ahora mismo dispongo de las siguientes funcionalidades: <br> 1 - Dime un Pokemon y te digo sus debilidades y fortalezas. <br> 2 - ¿Te interesa la evolución de tu Pokemon? Dime el Pokemon del que quieras saber sus evoluciones. <br> 3 - Dime el Pokemon del que quieras saber su región. <br> 4 - El amor está en el aire... Dime dos Pokemon y te digo su compatibilidad amorosa.
`;

// 2. ESTADO
let chatState = 'MENU'; 
let selectedOption = null;
let tempPokemon = null;

// 3. SECUENCIA DE INICIO (Animación)
if (chatMessages) {
    // Solo si está vacío iniciamos la bienvenida
    if (chatMessages.children.length === 0) {
        runWelcomeAnimation();
    }
}

// --- FUNCIONES ---

function runWelcomeAnimation() {
    // Mostrar "Escribiendo..."
    const typingId = showTypingIndicator(chatMessages);

    // Esperar 1.5s y mostrar mensaje
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
    div.innerHTML = `
        <div class="typing-indicator">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
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

async function handleUserMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    messageInput.value = '';

    // MÁQUINA DE ESTADOS
    if (chatState === 'MENU') {
        if (['1', '2', '3', '4'].includes(text)) {
            selectedOption = text;
            if (text === '4') {
                chatState = 'WAITING_P1_AMOR';
                addMessage("¡Uhh, tema amoroso! ❤️ Dime el nombre del primer Pokémon:", 'bot');
            } else {
                chatState = 'WAITING_POKEMON';
                const questions = {
                    '1': "Dime el Pokémon y analizaré sus Fortalezas y Debilidades.",
                    '2': "¿De qué Pokémon quieres ver la Evolución?",
                    '3': "¿De quién quieres saber la Región?"
                };
                addMessage(questions[text], 'bot');
            }
        } else {
            addMessage("Por favor, escribe solo el número de la opción (1, 2, 3 o 4).", 'bot');
        }
    } else if (chatState === 'WAITING_POKEMON') {
        await callBackend(selectedOption, text);
        resetChat();
    } else if (chatState === 'WAITING_P1_AMOR') {
        tempPokemon = text;
        chatState = 'WAITING_P2_AMOR';
        addMessage(`Vale, tenemos a **${text}**. ¿Con quién quieres comprobar su compatibilidad?`, 'bot');
    } else if (chatState === 'WAITING_P2_AMOR') {
        await callBackend('4', tempPokemon, text);
        resetChat();
    }
}

async function callBackend(option, text1, text2 = '') {
    const loadingId = showTypingIndicator(chatMessages);
    
    try {
        const response = await fetch('/chatbot/ask', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ option: String(option), text: text1, text2: text2 })
        });
        const data = await response.json();
        
        removeTypingIndicator(loadingId);
        
        let resultText = data.result;
        // Formateo simple
        if (option === '1' && typeof data.result === 'object') {
            resultText = `**Tipos:** ${data.result.tipos.join(', ')}<br>**Débil contra:** ${data.result.debil_contra.join(', ')}`;
        } else if (option === '4' && typeof data.result === 'object') {
            resultText = `Compatibilidad: **${data.result.percent}%** ❤️<br>${data.result.msg}`;
        }
        addMessage(resultText, 'bot');
        
    } catch (error) {
        removeTypingIndicator(loadingId);
        addMessage("Error conectando con Service-Ball. 😵", 'bot');
    }
}

function resetChat() {
    chatState = 'MENU';
    selectedOption = null;
    tempPokemon = null;
    setTimeout(() => {
        addMessage("¿En qué más puedo ayudarte? (Escribe 1-4)", 'bot');
    }, 1000);
}

// 4. EVENTOS
if(sendButton && messageInput){
    sendButton.addEventListener('click', handleUserMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleUserMessage();
    });
}