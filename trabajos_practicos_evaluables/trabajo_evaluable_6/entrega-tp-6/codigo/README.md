# EcoHarmony Park – Inscribirme a actividad (TP6, TDD)

Backend en **Python** hecho con TDD (Red-Green-Refactor). Plan de pruebas y decisiones en
[`../plan-pruebas-tdd-tp-6.md`](../plan-pruebas-tdd-tp-6.md). Estilo de código: **PEP 8** (verificado con `ruff`).

## Requisitos

- Python 3.11 o superior.
- Docker Desktop (para la base PostgreSQL local y gratuita).

## Puesta en marcha

Desde esta carpeta (`codigo/`):

```bash
# 1. Variables de entorno (el .env NO se sube al repositorio)
cp .env.example .env            # cambiar POSTGRES_PASSWORD (3 lineas) y SECRETO_DE_SESIONES (clave larga al azar)

# 2. Base de datos PostgreSQL
docker compose up -d

# 3. Entorno de Python
cd backend
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt -r requirements-dev.txt   # Windows
# en Linux/macOS: .venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt

# 4. Crear el esquema y cargar las 4 actividades en la base de desarrollo
PYTHONPATH=src .venv/Scripts/python.exe -m ecoharmony.preparar_base
```

## Ejecutar la API

```bash
cd backend
PYTHONPATH=src .venv/Scripts/python.exe -m uvicorn --factory ecoharmony.main:crear_aplicacion --port 8000
```

Documentación interactiva (Swagger): <http://localhost:8000/docs>. La API lee el `.env` (base de datos,
secreto de sesiones y SMTP). Si el SMTP **no** está configurado, los emails no se envían: se guardan (texto y QR)
en `codigo/salida_de_emails/`, solo para desarrollo.

| Método y ruta | Qué hace | Respuestas |
|---|---|---|
| `POST /registro` | alta con `email` y `contrasena` | 201 · 422 (datos inválidos) · 409 (email repetido) |
| `POST /sesion` | inicio de sesión; devuelve un `token` (vence a las 8 h) | 200 · 401 |
| `GET /actividades` | las 4 actividades con sus reglas y `disponible` | 200 |
| `GET /actividades/{nombre}/horarios?fecha=AAAA-MM-DD` | turnos con `cupo_restante` y `agotado` | 200 · 404 · 422 |
| `GET /actividades/{nombre}/terminos` | T&C específicos de la actividad | 200 · 404 |
| `POST /inscripciones` (`Authorization: Bearer <token>`) | inscribe; envía el email con un QR por visitante | 201 · 401 · 404 · 409 (sin cupo, DNI ya inscripto) · 422 · 503 (email) |

Cualquier error inesperado responde 500 con un mensaje genérico (no filtra detalles internos).

## Ejecutar el front (React)

```bash
cd frontend
npm install
npm run dev
```

Abre <http://localhost:5173>. Necesita la API corriendo en `http://localhost:8000` (otra dirección: variable
`VITE_API_URL`, ver `frontend/.env.example`). Para probarlo completo hace falta la base y la API arriba (pasos de arriba).

```bash
npm test          # pruebas del front (Vitest + Testing Library)
npm run build     # build de produccion en frontend/dist
```

Pantallas: acceso (registro e inicio de sesión), actividades, día y horario (con cupo restante), visitantes,
términos y condiciones de la actividad con resumen, y confirmación con el código de reserva. Diseño **Liquid Glass**
con la paleta y la fuente Lato indicadas por el PO. La sesión se recuerda en el navegador (`localStorage`) y vence a las 8 h.

## Ver la base con DBeaver

Nueva conexión → **PostgreSQL**:

| Campo | Valor |
|---|---|
| Host | `localhost` |
| Puerto | `5433` (el de `POSTGRES_PUERTO` en `.env`) |
| Base de datos | `ecoharmony` |
| Usuario / contraseña | los de `.env` |

La base `ecoharmony_test` es solo para las pruebas automáticas: **se vacía en cada corrida**.

## Pruebas

```bash
cd backend
.venv/Scripts/python.exe -m pytest              # todo (las pruebas de base se saltean si Docker no esta levantado)
.venv/Scripts/python.exe -m pytest -m "not db"  # sin base de datos
.venv/Scripts/python.exe -m ruff check .        # PEP 8
```

Categorías (ver el plan de pruebas): **U** unitarias (sin dependencias), **C** contrato/integración local
(`-m db`: PostgreSQL y la librería `qrcode`), **X** externas (email real, no están en la corrida normal).

## Estructura

```
codigo/
├── docker-compose.yml          PostgreSQL 16 local
├── .env.example                variables (copiar a .env)
├── backend/
│   ├── sql/schema.sql          esquema (SQL plano, legible en DBeaver)
│   ├── src/ecoharmony/         dominio, servicio, adaptadores y API
│   └── tests/                  un archivo por grupo del plan de pruebas
└── frontend/
    └── src/                    React: api/, dominio/ (reglas puras), componentes/ (pantallas) y App
```

## Email real

`ServicioEmailSmtp` envía por SMTP con STARTTLS, así que sirve para **Gmail** (contraseña de aplicación) o
**Brevo**: solo cambian las variables `SMTP_*` y `EMAIL_REMITENTE` del `.env`. Nunca subir credenciales al
repositorio (es público).
