"""
app.py - API simple de canciones (Flask)
Versión simplificada: sin threading ni typing, comentarios en español.

Usa:
    python -m venv venv
    venv\Scripts\activate  # Windows
    pip install Flask
    python app.py
"""

from flask import Flask, jsonify, request, abort
from pathlib import Path
import json
import os

# -------------------------
# Configuración
# -------------------------
DB_PATH = Path("./db.json")
JSON_INDENT = 4
APP_HOST = "127.0.0.1"
APP_PORT = 5001
DEBUG = True

# -------------------------
# Inicializar app
# -------------------------
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # permitir UTF-8 en jsonify

# -------------------------
# Utilidades de lectura/escritura (simples)
# -------------------------
def ensure_db_exists():
    """Crea el fichero DB con la estructura base si no existe."""
    if not DB_PATH.exists():
        default = {"songs": []}
        write_data(default)


def read_data():
    """
    Lee y devuelve el contenido de la base de datos JSON.
    Si el fichero no existe o está corrupto devuelve {"songs": []}.
    """
    try:
        ensure_db_exists()
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"songs": []}
            return {"songs": list(data.get("songs", []))}
    except (json.JSONDecodeError, FileNotFoundError):
        # Si hay problema devolvemos una lista vacía para no romper la app
        return {"songs": []}
    except Exception as e:
        # Registro simple en consola y devolver estructura vacía
        print(f"[ERROR] Leyendo DB: {e}")
        return {"songs": []}


def write_data(data):
    """
    Escribe el diccionario 'data' al fichero DB_PATH.
    No lanza excepciones hacia el cliente; registra errores en consola.
    """
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=JSON_INDENT)
    except Exception as e:
        print(f"[ERROR] Al escribir en {DB_PATH}: {e}")


# -------------------------
# Helper de respuesta
# -------------------------
def make_response(data=None, message="", status=200):
    """Construye una respuesta JSON consistente."""
    payload = {"message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status


# -------------------------
# Manejo básico de errores HTTP
# -------------------------
@app.errorhandler(400)
def handle_400(e):
    desc = getattr(e, "description", "Bad Request")
    return make_response(message=str(desc), status=400)


@app.errorhandler(404)
def handle_404(e):
    desc = getattr(e, "description", "Not Found")
    return make_response(message=str(desc), status=404)


@app.errorhandler(405)
def handle_405(e):
    return make_response(message="Method Not Allowed", status=405)


@app.errorhandler(500)
def handle_500(e):
    return make_response(message="Internal Server Error", status=500)


# -------------------------
# Rutas
# -------------------------
@app.route("/", methods=["GET"])
def home():
    """Ruta raíz: mensaje simple."""
    return make_response(message="Welcome to the Flask Songs API", status=200)


@app.route("/songs", methods=["GET"])
def get_all_songs():
    """Devuelve la lista completa de canciones."""
    data = read_data()
    return make_response(data=data["songs"], status=200)


@app.route("/songs/<int:song_id>", methods=["GET"])
def get_song(song_id):
    """Devuelve una canción por su id."""
    data = read_data()
    song = next((s for s in data.get("songs", []) if s.get("id") == song_id), None)
    if song is None:
        abort(404, description=f"ID {song_id} no encontrado en la base de datos")
    return make_response(data=song, status=200)


@app.route("/songs", methods=["POST"])
def add_song():
    """
    Crea una nueva canción.
    JSON requerido: { "titulo": str, "artista": str, ...opcionales... }
    """
    body = request.get_json(silent=True)
    if not body:
        abort(400, description="JSON inválido o vacío")

    # Validación mínima
    if "titulo" not in body or "artista" not in body:
        abort(400, description="Faltan campos obligatorios: 'titulo' y 'artista'")

    data = read_data()
    # calcular nuevo id de forma sencilla
    existing_ids = [s.get("id", 0) for s in data.get("songs", []) if isinstance(s.get("id", None), int)]
    new_id = (max(existing_ids) + 1) if existing_ids else 1

    new_song = {"id": new_id}
    new_song.update(body)  # permite campos extras

    data["songs"].append(new_song)
    write_data(data)

    return make_response(data=new_song, message="Canción creada", status=201)


@app.route("/songs/<int:song_id>", methods=["PUT"])
def update_song(song_id):
    """
    Actualiza una canción por id.
    Si el body incluye 'id', se ignora para evitar cambiar el identificador.
    """
    body = request.get_json(silent=True)
    if body is None:
        abort(400, description="JSON inválido o vacío")

    data = read_data()
    for i, s in enumerate(data.get("songs", [])):
        if s.get("id") == song_id:
            body.pop("id", None)  # no permitir cambiar id
            updated = {**s, **body}
            data["songs"][i] = updated
            write_data(data)
            return make_response(data=updated, message="Canción actualizada", status=200)

    abort(404, description=f"ID {song_id} no encontrado en la base de datos")


@app.route("/songs/<int:song_id>", methods=["DELETE"])
def delete_song(song_id):
    """Elimina una canción por id."""
    data = read_data()
    if not any(s.get("id") == song_id for s in data.get("songs", [])):
        abort(404, description=f"ID {song_id} no encontrado en la base de datos")

    data["songs"] = [s for s in data.get("songs", []) if s.get("id") != song_id]
    write_data(data)
    return make_response(message="Canción eliminada", status=200)


# -------------------------
# Inicio de la aplicación
# -------------------------
if __name__ == "__main__":
    ensure_db_exists()
    app.run(host=APP_HOST, port=APP_PORT, debug=DEBUG)
