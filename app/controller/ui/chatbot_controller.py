from flask import Blueprint, render_template, request, jsonify
from app.controller.model.chatbot_controller import ChatBotModel

def chatbot_blueprint():
    # Creamos el Blueprint
    bp = Blueprint('chatbot', __name__)
    
    # Instantciamos el modelo del chatbot
    bot = ChatBotModel()

    # RUTA 1: Pagina principal
    @bp.route('/chatbot', methods=['GET'])
    def index():
        return render_template('chatbot.html')
    
    return bp