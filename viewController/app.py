import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template
from model.api.pokeapi_cliente import PokeApiCliente

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #he tenido que poner asi porque no me encontraba el index, a ver si podemos ponerlo normal en un futuro
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
cliente = PokeApiCliente()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lista_pokemons")
def pokemons():
    lista = cliente.get_lista_pokemons(10) # pongo 10 para que no me de todos
    return render_template("lista_pokemons.html", pokemons=lista.results)

@app.route("/login")
def login():
    return render_template("login.html")
if __name__ == "__main__":
    app.run(debug=True)
