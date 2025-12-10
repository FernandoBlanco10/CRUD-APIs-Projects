from flask import Flask, jsonify, request, abort
import json
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
DB_PATH = './db.json'

# HELPERS

def read_data():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Database file not found.")
        return {"songs": []}

def write_data(data):
    try:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing to database: {e}")

# ROUTES

@app.route('/', methods = ['GET'])
def home():
    return "Welcome to the Flask API!"

# *** GET ALL SONGS ***
@app.route('/songs', methods=['GET'])
def get_all_songs():
    data = read_data()
    return jsonify(data['songs']), 200

# *** GET SONG BY ID ***
@app.route('/songs/<int:song_id>', methods=['GET'])
def get_song(song_id):
    data = read_data()
    song = next((s for s in data.get('songs', []) if s.get('id') == song_id), None)
    if song is None:
        return jsonify({"error": "ID not found in database", "id": song_id}), 404
    return jsonify(song), 200

# *** ADD NEW SONG ***
@app.route('/songs', methods=['POST'])
def add_song():
    data = read_data()
    body = request.json

    if not body or 'titulo' not in body or 'artista' not in body:
        abort(400, description="Missing required fields: title and artist")
    
    new_id = max([song["id"] for song in data["songs"]], default=0) + 1

    new_song = {
        "id": new_id,
        **body
    }

    data['songs'].append(new_song)
    write_data(data)

    return jsonify(new_song), 201

# *** PUT - UPDATE SONG BY ID ***
@app.route('/songs/<int:song_id>', methods=['PUT'])
def update_song(song_id):
    data = read_data()
    body = request.json

    song = next((s for s in data.get('songs', []) if s.get('id') == song_id), None)
    if song is None:
        return jsonify({"error": "ID not found in database", "id": song_id}), 404

    song.update(body)

    write_data(data)

    return jsonify({"message": "Song updated successfully"}), 200

# *** DELETE SONG BY ID ***
@app.route('/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    data = read_data()

    song = next((s for s in data.get('songs', []) if s.get('id') == song_id), None)
    if song is None:
        return jsonify({"error": "ID not found in database", "id": song_id}), 404

    data['songs'] = [s for s in data['songs'] if s.get('id') != song_id]
    write_data(data)

    return jsonify({"message": "Song deleted successfully"}), 200

if __name__ == '__main__':
    app.run(
        host='localhost',  
        port=5001,       
        debug=True
    )
