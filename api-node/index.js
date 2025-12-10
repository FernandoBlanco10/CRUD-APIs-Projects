// app.mjs
import express from 'express';
import fs from 'fs/promises';
import path from 'path';

const app = express();
const PORT = 3000;

// --- Configuración middleware ---
app.use(express.json()); // Parsear JSON del body

// --- Configuración del archivo de datos ---
const DB_FILE = path.resolve('./db.json'); // ruta al archivo JSON

// --- HELPERS / UTILIDADES ---

/**
 * Lee y parsea el archivo db.json.
 * @returns {Promise<Object>} objeto con los datos o lanza error si falla
 */
async function readData() {
  try {
    const raw = await fs.readFile(DB_FILE, 'utf-8');
    return JSON.parse(raw);
  } catch (err) {
    // Si no existe el archivo, devolvemos estructura por defecto
    if (err.code === 'ENOENT') {
      return { songs: [] };
    }
    throw err;
  }
}

/**
 * Escribe el objeto `data` en db.json (formato legible).
 * @param {Object} data
 * @returns {Promise<void>}
 */
async function writeData(data) {
  try {
    await fs.writeFile(DB_FILE, JSON.stringify(data, null, 2), 'utf-8');
  } catch (err) {
    throw err;
  }
}

/**
 * Genera el siguiente id incremental basándose en el array songs.
 * @param {Array} songs
 * @returns {number}
 */
function getNextId(songs) {
  if (!Array.isArray(songs) || songs.length === 0) return 1;
  const maxId = songs.reduce((max, s) => (s.id > max ? s.id : max), 0);
  return maxId + 1;
}

/**
 * Validación sencilla del payload de canción.
 * Ajusta según los campos que esperes (aquí: title y artist opcionales ejemplo).
 * @param {Object} body
 * @returns {Array<string>} lista de errores (vacía si es válido)
 */
function validateSong(body) {
  const errors = [];
  if (!body) {
    errors.push('Body is required.');
    return errors;
  }
  // Ejemplo: aseguramos que exista al menos un título o artista
  if (!body.titulo && !body.artista) {
    errors.push('Se requiere al menos "titulo" o "artista".');
  }
  return errors;
}

// --- RUTAS ---

// Ruta de bienvenida
app.get('/', (req, res) => {
  res.send('Bienvenido a mi API con Express y ES Modules!');
});

// GET /songs -> devuelve todas las canciones
app.get('/songs', async (req, res) => {
  try {
    const data = await readData();
    res.json(data.songs);
  } catch (err) {
    console.error('GET /songs error:', err);
    res.status(500).json({ error: 'Error al leer las canciones.' });
  }
});

// GET /songs/:id -> devuelve una canción por id
app.get('/songs/:id', async (req, res) => {
  try {
    const id = Number(req.params.id);
    if (Number.isNaN(id)) return res.status(400).json({ error: 'ID inválido.' });

    const data = await readData();
    const song = data.songs.find((s) => s.id === id);

    if (!song) return res.status(404).json({ error: 'Canción no encontrada.' });
    res.json(song);
  } catch (err) {
    console.error('GET /songs/:id error:', err);
    res.status(500).json({ error: 'Error al leer la canción.' });
  }
});

// POST /songs -> crea una canción nueva
app.post('/songs', async (req, res) => {
  try {
    const body = req.body;
    const errors = validateSong(body);
    if (errors.length) return res.status(400).json({ errors });

    const data = await readData();
    const newSong = {
      id: getNextId(data.songs),
      ...body,
    };

    data.songs.push(newSong);
    await writeData(data);

    res.status(201).json(newSong);
  } catch (err) {
    console.error('POST /songs error:', err);
    res.status(500).json({ error: 'Error al crear la canción.' });
  }
});

// PUT /songs/:id -> actualiza parcialmente o totalmente una canción
app.put('/songs/:id', async (req, res) => {
  try {
    const id = Number(req.params.id);
    if (Number.isNaN(id)) return res.status(400).json({ error: 'ID inválido.' });

    const body = req.body;
    const errors = validateSong(body);
    if (errors.length) return res.status(400).json({ errors });

    const data = await readData();
    const idx = data.songs.findIndex((s) => s.id === id);
    if (idx === -1) return res.status(404).json({ error: 'Canción no encontrada.' });

    data.songs[idx] = { ...data.songs[idx], ...body };
    await writeData(data);

    res.json({ message: 'Song updated successfully', song: data.songs[idx] });
  } catch (err) {
    console.error('PUT /songs/:id error:', err);
    res.status(500).json({ error: 'Error al actualizar la canción.' });
  }
});

// DELETE /songs/:id -> elimina una canción por id
app.delete('/songs/:id', async (req, res) => {
  try {
    const id = Number(req.params.id);
    if (Number.isNaN(id)) return res.status(400).json({ error: 'ID inválido.' });

    const data = await readData();
    const idx = data.songs.findIndex((s) => s.id === id);
    if (idx === -1) return res.status(404).json({ error: 'Canción no encontrada.' });

    data.songs.splice(idx, 1);
    await writeData(data);

    res.json({ message: 'Song deleted successfully' });
  } catch (err) {
    console.error('DELETE /songs/:id error:', err);
    res.status(500).json({ error: 'Error al eliminar la canción.' });
  }
});

// --- Iniciar servidor ---
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
