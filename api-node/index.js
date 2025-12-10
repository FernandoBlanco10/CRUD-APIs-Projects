import express from 'express';
import fs, { read } from 'fs'; // Módulo para trabajar con archivos del sistema o del folder
import bodyParser from 'body-parser';

const app = express();
const PORT = 3000;
app.use(bodyParser.json()); // Middleware para parsear JSON

const readData = () => {
    try {
        const data = fs.readFileSync('./db.json', 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        console.error('Error reading the file:', error);
        return null;
    }
}

const writeData = (data) => {
    try {
        fs.writeFileSync('./db.json', JSON.stringify(data), 'utf-8');
    } catch (error) {
        console.error('Error writing to the file:', error);
    }
}

// Ruta de bienvenida

app.get('/', (req, res) => {
    res.send('Bienvenido a mi API con Express y ES Modules!');
})

// **** GET all ****

app.get("/songs", (req, res) => {
    const data = readData();
    res.json(data.songs);
});

// **** GET by ID ****
app.get("/songs/:id", (req,  res) => {
    const data = readData();
    const id = parseInt(req.params.id);
    const song = data.songs.find((song) => song.id === id);
    res.json(song);
});

// **** POST ****
app.post("/songs", (req, res) => {
    const data = readData();
    const body = req.body;
    const newSong = {
        id: data.songs.length + 1,
        ...body, // Todo lo del body lo agregue tal cual
    };
    data.songs.push(newSong);
    writeData(data);
    res.json(newSong);
});

// **** PUT ****
app.put("/songs/:id", (req, res) => {
    const data = readData();
    const body = req.body;
    const id = parseInt(req.params.id);
    const songIndex = data.songs.findIndex((song) => song.id === id);
    data.songs[songIndex] = {
        ...data.songs[songIndex],
        ...body,
    }
    writeData(data);
    res.json({message: 'Song updated successfully'});
});

// **** DELETE ****
app.delete("/songs/:id", (req, res) => {
    const data = readData();
    const id = parseInt(req.params.id);
    const bookIndex = data.songs.findIndex((song) => song.id === id);
    data.songs.splice(bookIndex, 1);
    writeData(data);
    res.json({message: 'Song deleted successfully'});
});

app.listen(PORT , () => {
    console.log(`Server is running on port ${PORT}`);
});

