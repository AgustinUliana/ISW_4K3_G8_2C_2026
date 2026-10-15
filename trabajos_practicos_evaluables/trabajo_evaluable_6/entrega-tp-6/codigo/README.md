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
└── backend/
    ├── sql/schema.sql          esquema (SQL plano, legible en DBeaver)
    ├── src/ecoharmony/         dominio, servicio y adaptadores
    └── tests/                  un archivo por grupo del plan de pruebas
```

## Email real

`ServicioEmailSmtp` envía por SMTP con STARTTLS, así que sirve para **Gmail** (contraseña de aplicación) o
**Brevo**: solo cambian las variables `SMTP_*` y `EMAIL_REMITENTE` del `.env`. Nunca subir credenciales al
repositorio (es público).
