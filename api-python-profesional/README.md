# Songs API 🎵

Una API REST profesional y escalable para gestionar colecciones de canciones, construida con Flask y siguiendo las mejores prácticas de desarrollo de software.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Pytest-orange.svg)](tests/)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-Black-black.svg)](https://github.com/psf/black)

## 📋 Descripción

Esta API implementa un sistema CRUD completo para administrar una base de datos de canciones con:

- ✅ **Validación robusta** usando Pydantic
- ✅ **Documentación automática** con Swagger/OpenAPI
- ✅ **Manejo de errores** profesional y logging
- ✅ **Arquitectura modular** y escalable
- ✅ **Testing comprehensivo** con pytest
- ✅ **Configuración por entorno** con variables de entorno
- ✅ **Soporte Unicode** para caracteres especiales
- ✅ **Middleware** para logging y monitoreo
- ✅ **Versionado de API** (v1)
- ✅ **Paginación** automática
- ✅ **Estadísticas** de base de datos

## 🚀 Características Principales

### Arquitectura Profesional
- **Modular**: Separación clara de responsabilidades
- **Type-Safe**: Type hints en todo el código
- **Error-Handling**: Manejo robusto de errores con logging
- **Configurable**: Configuración por entorno
- **Documentada**: API documentation automática

### Funcionalidades API
- **CRUD Completo**: Crear, leer, actualizar y eliminar canciones
- **Paginación**: Soporte para listas grandes de datos
- **Validación**: Validación de datos con Pydantic
- **Estadísticas**: Endpoints para análisis de datos
- **Health Checks**: Monitoreo del estado del sistema
- **CORS**: Configuración para aplicaciones frontend

## 📁 Estructura del Proyecto

```
songs-api/
├── app.py                 # Aplicación principal Flask
├── config/
│   └── settings.py        # Configuración y variables de entorno
├── models/
│   └── song.py           # Modelos de datos con Pydantic
├── services/
│   └── database.py       # Servicio de base de datos
├── utils/
│   └── errors.py         # Manejo de errores y logging
├── tests/
│   ├── conftest.py       # Configuración de pytest
│   └── test_songs_api.py # Tests de la API
├── requirements.txt      # Dependencias del proyecto
├── pytest.ini          # Configuración de pytest
├── .env.example        # Ejemplo de variables de entorno
├── .gitignore         # Archivos a ignorar en Git
├── db.json           # Base de datos JSON de ejemplo
└── README.md         # Este archivo
```

## 🛠️ Instalación y Configuración

### Prerrequisitos

- **Python 3.8+**
- **pip** (gestor de paquetes de Python)

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd songs-api
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en macOS/Linux
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tu configuración preferida
```

### 5. Crear Directorio de Datos

```bash
mkdir -p data
```

### 6. Ejecutar la Aplicación

```bash
# Modo desarrollo
python app.py

# O usar Flask directamente
export FLASK_APP=app.py
flask run
```

La API estará disponible en: `http://localhost:5001`

## 📚 Documentación de la API

### Endpoints Disponibles

#### Base Endpoints
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Health check y información básica |
| GET | `/api/v1/health` | Health check detallado con estadísticas |

#### Songs Management
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/songs` | Obtener todas las canciones (paginado) |
| GET | `/api/v1/songs/{id}` | Obtener canción específica por ID |
| POST | `/api/v1/songs` | Crear nueva canción |
| PUT | `/api/v1/songs/{id}` | Actualizar canción existente |
| DELETE | `/api/v1/songs/{id}` | Eliminar canción |
| GET | `/api/v1/stats` | Estadísticas de la base de datos |

#### Swagger Documentation
| Endpoint | Descripción |
|----------|-------------|
| `/api/docs` | Documentación interactiva de la API |

### Ejemplos de Uso

#### 1. Obtener todas las canciones
```bash
curl -X GET http://localhost:5001/api/v1/songs \
  -H "Accept: application/json"
```

**Respuesta:**
```json
{
  "songs": [
    {
      "id": 1,
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "titulo": "Bohemian Rhapsody",
      "artista": "Queen",
      "album": "A Night at the Opera",
      "año": 1975,
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 50,
  "has_next": false,
  "has_prev": false
}
```

#### 2. Crear nueva canción
```bash
curl -X POST http://localhost:5001/api/v1/songs \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Mi Canción Favorita",
    "artista": "Mi Artista",
    "album": "Mi Álbum",
    "año": 2023
  }'
```

#### 3. Actualizar canción
```bash
curl -X PUT http://localhost:5001/api/v1/songs/1 \
  -H "Content-Type: application/json" \
  -d '{
    "album": "Nuevo Álbum",
    "año": 2024
  }'
```

#### 4. Eliminar canción
```bash
curl -X DELETE http://localhost:5001/api/v1/songs/1
```

#### 5. Obtener estadísticas
```bash
curl -X GET http://localhost:5001/api/v1/stats
```

**Respuesta:**
```json
{
  "total_songs": 150,
  "total_artists": 75,
  "total_albums": 120,
  "year_range": {
    "min_year": 1960,
    "max_year": 2024
  },
  "database_size": 10240
}
```

### Parámetros de Consulta

#### Paginación
- `page` (int): Número de página (default: 1)
- `per_page` (int): Elementos por página (default: 50, max: 100)

**Ejemplo:**
```bash
curl "http://localhost:5001/api/v1/songs?page=2&per_page=20"
```

### Estructura de Datos

#### Song Model
```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "titulo": "Nombre de la canción",
  "artista": "Nombre del artista",
  "album": "Nombre del álbum (opcional)",
  "año": 2023,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

#### Campos Requeridos
- `titulo` (string, 1-200 chars): Título de la canción
- `artista` (string, 1-100 chars): Nombre del artista

#### Campos Opcionales
- `album` (string, max 200 chars): Nombre del álbum
- `año` (integer, 1800-current year): Año de lanzamiento

## 🧪 Testing

### Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=. --cov-report=html

# Ejecutar tests específicos
pytest tests/test_songs_api.py

# Ejecutar con marcadores
pytest -m unit
pytest -m integration
pytest -m slow
```

### Tipos de Tests

- **Unit Tests**: Pruebas de funciones individuales
- **Integration Tests**: Pruebas de integración entre componentes
- **API Tests**: Pruebas completas de endpoints
- **Edge Case Tests**: Pruebas de casos límite y errores

### Cobertura de Tests

El proyecto incluye tests para:
- ✅ Todos los endpoints de la API
- ✅ Validación de datos
- ✅ Manejo de errores
- ✅ Casos límite y edge cases
- ✅ Paginación
- ✅ Unicode y caracteres especiales

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
# Configuración de la aplicación
APP_NAME="Songs API"
APP_VERSION="1.0.0"
DEBUG=true
ENVIRONMENT="development"

# Configuración del servidor
HOST="localhost"
PORT=5001

# Configuración de la base de datos
DATABASE_PATH="./data/db.json"
DATABASE_BACKUP_PATH="./data/db_backup.json"

# Configuración de logging
LOG_LEVEL="INFO"
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Configuración por Entorno

#### Desarrollo
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

#### Producción
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=80
```

#### Testing
```bash
ENVIRONMENT=testing
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_PATH="./tests/fixtures/test_db.json"
```

## 🛡️ Características de Seguridad

- **Validación de entrada**: Validación robusta con Pydantic
- **Manejo de errores**: No se exponen detalles sensibles
- **Límites de tamaño**: Límites en tamaño de requests
- **Headers de seguridad**: Headers apropiados en responses
- **Sanitización**: Sanitización de datos de entrada

## 📊 Logging y Monitoreo

### Logs Disponibles

- **Application Logs**: `logs/app.log`
- **Error Logs**: Registros automáticos de errores
- **Request Logs**: Logging de todas las requests
- **Performance Logs**: Tiempo de respuesta de endpoints

### Formato de Logs

```
2023-12-10 01:30:00 - songs_api - INFO - Request received
2023-12-10 01:30:00 - songs_api - INFO - Request completed in 15.23ms
```

### Métricas

- Tiempo de respuesta por endpoint
- Número de requests por período
- Estadísticas de base de datos
- Health check status

## 🚀 Deployment

### Desarrollo Local
```bash
python app.py
```

### Producción con Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Docker (Futuro)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

### Guías de Contribución

- Seguir PEP 8 para código Python
- Incluir tests para nuevas funcionalidades
- Actualizar documentación
- Usar type hints
- Mantener cobertura de tests > 80%

## 📝 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- **Flask**: Framework web utilizado
- **Pydantic**: Validación de datos
- **Flasgger**: Documentación Swagger
- **Pytest**: Framework de testing
- **Black**: Formateador de código

## 📞 Soporte

Para soporte y preguntas:

- **Issues**: [GitHub Issues](issues/)
- **Documentation**: [API Docs](http://localhost:5001/api/docs)
- **Email**: support@example.com

---

**¡Disfruta desarrollando con Songs API!** 🎵✨

### 🔗 Enlaces Útiles

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [OpenAPI Specification](https://swagger.io/specification/)