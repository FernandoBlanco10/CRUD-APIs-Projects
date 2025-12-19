# API CRUD - Gestión de Canciones 🎵

**Autor:** Fernando Blanco

Una colección completa de APIs REST para gestionar colecciones de canciones, implementadas en diferentes tecnologías y niveles de complejidad.

[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-orange.svg)](https://flask.palletsprojects.com)
[![Express.js](https://img.shields.io/badge/Express.js-4.x-black.svg)](https://expressjs.com)

## 📋 Descripción

Este proyecto contiene **tres implementaciones diferentes** de una API CRUD para gestionar canciones, cada una con un nivel diferente de complejidad y características:

### 🚀 Implementaciones Disponibles

| API | Tecnología | Puerto | Complejidad | Características |
|-----|------------|--------|-------------|----------------|
| **api-node** | Node.js + Express | 3000 | Básica | CRUD simple, JSON file storage |
| **api-python** | Python + Flask | 5001 | Intermedia | CRUD mejorado, mejor validación |
| **api-python-profesional** | Python + Flask + Pydantic | 5001 | Avanzada | Full-featured, tests, docs, logging |

## 🎯 Características Principales

### Funcionalidades Comunes
- ✅ **CRUD Completo**: Crear, leer, actualizar y eliminar canciones
- ✅ **Base de Datos JSON**: Almacenamiento simple en archivos JSON
- ✅ **Validación de Datos**: Validación de campos requeridos
- ✅ **Manejo de Errores**: Respuestas HTTP apropiadas
- ✅ **Documentación**: Archivos HTTP para testing

### Endpoints Base

Todas las APIs comparten los siguientes endpoints:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Página de bienvenida |
| GET | `/songs` | Obtener todas las canciones |
| GET | `/songs/{id}` | Obtener canción específica |
| POST | `/songs` | Crear nueva canción |
| PUT | `/songs/{id}` | Actualizar canción |
| DELETE | `/songs/{id}` | Eliminar canción |

## 📁 Estructura del Proyecto

```
API CRUD/
├── api-node/              # Implementación Node.js
│   ├── index.js          # Servidor Express
│   ├── db.json           # Base de datos JSON
│   ├── package.json      # Dependencias Node.js
│   └── requests.http     # Documentación HTTP
├── api-python/           # Implementación Python básica
│   ├── main.py           # Aplicación Flask
│   ├── db.json           # Base de datos JSON
│   ├── .gitignore        # Ignorar archivos Python
│   └── requests.http     # Documentación HTTP
└── README.md             # Este archivo
```

## 🛠️ Instalación y Configuración

### Prerrequisitos

- **Node.js 18+** (para api-node)
- **Python 3.8+** (para api-python)
- **npm** o **yarn** (para dependencias Node.js)
- **pip** (para dependencias Python)

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd API-CRUD
```

## 🚀 Instrucciones de Ejecución

### Opción 1: API Node.js (api-node) 🟢

```bash
cd api-node
npm install
npm start
```

**Servidor disponible en:** `http://localhost:3000`

### Opción 2: API Python Básica (api-python) 🟡

```bash
cd api-python
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install Flask
python main.py
```

**Servidor disponible en:** `http://localhost:5001`

## 📚 Documentación de la API

### Ejemplos de Uso con curl

#### 1. Obtener todas las canciones

```bash
# API Node (puerto 3000)
curl -X GET http://localhost:3000/songs

# API Python (puerto 5001)
curl -X GET http://localhost:5001/songs
```

#### 2. Crear nueva canción

```bash
# API Node
curl -X POST http://localhost:3000/songs \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Mi Canción Favorita",
    "artista": "Mi Artista",
    "album": "Mi Álbum",
    "año": 2023
  }'

# API Python
curl -X POST http://localhost:5001/songs \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Mi Canción Favorita",
    "artista": "Mi Artista",
    "album": "Mi Álbum",
    "año": 2023
  }'
```

#### 3. Obtener canción específica

```bash
# API Node
curl -X GET http://localhost:3000/songs/1

# API Python
curl -X GET http://localhost:5001/songs/1
```

#### 4. Actualizar canción

```bash
# API Node
curl -X PUT http://localhost:3000/songs/1 \
  -H "Content-Type: application/json" \
  -d '{
    "album": "Nuevo Álbum",
    "año": 2024
  }'

# API Python
curl -X PUT http://localhost:5001/songs/1 \
  -H "Content-Type: application/json" \
  -d '{
    "album": "Nuevo Álbum",
    "año": 2024
  }'
```

#### 5. Eliminar canción

```bash
# API Node
curl -X DELETE http://localhost:3000/songs/1

# API Python
curl -X DELETE http://localhost:5001/songs/1
```

### Estructura de Datos

#### Modelo de Canción
```json
{
  "id": 1,
  "titulo": "Nombre de la canción",
  "artista": "Nombre del artista",
  "album": "Nombre del álbum (opcional)",
  "año": 2023
}
```

#### Campos Requeridos
- `titulo` (string): Título de la canción
- `artista` (string): Nombre del artista

#### Campos Opcionales
- `album` (string): Nombre del álbum
- `año` (integer): Año de lanzamiento

### Códigos de Estado HTTP

| Código | Descripción | Uso |
|--------|-------------|-----|
| 200 | OK | Operaciones GET exitosas |
| 201 | Created | Operación POST exitosa |
| 400 | Bad Request | Datos inválidos o faltantes |
| 404 | Not Found | Canción no encontrada |
| 500 | Internal Server Error | Error del servidor |

## 🧪 Testing

### Usando HTTP Files

Cada implementación incluye archivos `requests.http` para testing manual:

- **api-node/requests.http** - Testing para API Node.js
- **api-python/requests.http** - Testing para API Python básica

### Testing con Postman

Puedes importar los archivos `.http` en Postman o crear requests manuales siguiendo los ejemplos anteriores.

## 🆚 Comparación de Implementaciones

| Característica | api-node | api-python | api-python-profesional |
|----------------|----------|------------|------------------------|
| **Tecnología** | Node.js + Express | Python + Flask | Python + Flask + Pydantic |
| **Puerto** | 3000 | 5001 | 5001 |
| **Validación** | Básica | Intermedia | Avanzada con Pydantic |
| **Documentación** | HTTP file | HTTP file | Swagger + HTTP file |
| **Tests** | No | No | Pytest completo |
| **Logging** | Básico | Básico | Avanzado |
| **Configuración** | package.json | Manual | Variables de entorno |
| **Arquitectura** | Monolítica | Monolítica | Modular |
| **Error Handling** | Básico | Intermedio | Profesional |
| **Paginación** | No | No | Sí |
| **Estadísticas** | No | No | Sí |
| **Health Checks** | No | No | Sí |

## 🎓 Diferencias Clave

### api-node (Node.js)
- **Ventajas**: Rápido desarrollo, gran ecosistema npm
- **Ideal para**: Proyectos rápidos, desarrolladores JavaScript
- **Puerto**: 3000

### api-python (Flask básica)
- **Ventajas**: Sintaxis Python simple, menos dependencias
- **Ideal para**: Aprendizaje, proyectos pequeños
- **Puerto**: 5001

## 🔧 Configuración Adicional

#### Para api-node:
```bash
npm install -g pm2
pm2 start index.js --name "songs-api"
```

## 📝 Notas Importantes

1. **Puertos**: Las APIs Python (api-python y api-python-profesional) usan el mismo puerto (5001). No las ejecutes simultáneamente.

2. **Base de Datos**: Cada API tiene su propia base de datos JSON independiente.

3. **Compatibilidad**: Todas las APIs comparten la misma estructura de datos y endpoints.

Este es un proyecto personal de Fernando Blanco.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

---

**¡Disfruta desarrollando con las APIs CRUD de Canciones!** 🎵✨

### 🔗 Enlaces Útiles

- [Node.js Documentation](https://nodejs.org/docs/)
- [Express.js Guide](https://expressjs.com/guide/)
- [Python Documentation](https://docs.python.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)