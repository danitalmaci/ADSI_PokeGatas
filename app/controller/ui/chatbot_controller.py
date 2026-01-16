from flask import Blueprint, render_template, request, jsonify
# Importamos el controlador principal y la conexión a BD
from app.controller.pokedex import Pokedex
from app.database.connection import Connection

def chatbot_blueprint():
    # Creamos el Blueprint
    bp = Blueprint('chatbot', __name__)
    
    # RUTA 1: Carga la página HTML (GET)
    @bp.route('/chatbot', methods=['GET'])
    def chatbot():
        return render_template('chatbot.html')
    
    # RUTA 2: Recibe el mensaje del JS (POST)
    # Secuencia: JS -> UI Controller -> Pokedex
    @bp.route('/chatbot/procesar', methods=['POST'])
    def procesar_mensaje():
        data = request.get_json()
        mensaje_usuario = data.get('mensaje', '')
        
        # 1. Instanciamos la conexión (necesaria para Pokedex)
        db = Connection()
        
        # 2. Instanciamos el Controlador Principal
        pokedex = Pokedex(db)
        
        # 3. Llamamos al método del chatbot en Pokedex
        respuesta = pokedex.solicitarConsultaCB(mensaje_usuario)
        
        # 4. Devolvemos la respuesta al JS
        return jsonify(respuesta)
    
    return bp