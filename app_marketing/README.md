# Marketing IA

**Autor:** Equipo de desarrollo

## Descripción

Aplicación web en Flask que genera campañas de marketing para empresas a partir de una foto de producto:

1. El usuario sube una foto, el nombre de la empresa y el producto o servicio.
2. Un modelo de texto de OpenAI propone **3 guiones** publicitarios.
3. El usuario elige uno de los guiones.
4. Un modelo de imagen de OpenAI genera **3 imágenes** publicitarias a partir de la foto y del guion elegido.

La publicación en redes sociales (TikTok) todavía no está activa. La capa de negocio ya incluye un contrato (`Publicador`) preparado para añadirla.

## Estado del proyecto

| Función | Estado |
|---|---|
| Subida de foto y datos de campaña | Activa |
| Generación de 3 guiones (GPT) | Activa |
| Elección de guion | Activa |
| Generación de 3 imágenes (GPT) | Activa |
| Publicación en TikTok | Pendiente |
| Publicación en Instagram | No planificada |
| Autenticación de usuarios | Pendiente |

## Arquitectura

El proyecto sigue una arquitectura de tres capas:

- **Presentación** (`app/presentacion`): rutas Flask y plantillas HTML.
- **Negocio** (`app/negocio`): reglas del flujo de campaña y contrato de publicación.
- **Datos** (`app/datos`): modelos SQLAlchemy y cliente de OpenAI. Es la única capa que habla con la API externa.

Las capas solo se llaman hacia abajo. La presentación nunca usa directamente OpenAI ni SQLAlchemy de forma compleja.

### Estructura

```text
marketing-app/
├── run.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .dockerignore
├── .gitignore
└── app/
    ├── __init__.py          # create_app (patrón factory)
    ├── config.py            # configuración desde variables de entorno
    ├── extensions.py        # instancia de SQLAlchemy
    ├── datos/
    │   ├── modelos.py       # tablas: campanas, guiones, medios, publicaciones, cuentas_tiktok
    │   └── proveedores.py  # llamadas a OpenAI (guiones e imágenes)
    ├── negocio/
    │   ├── campanas.py     # flujo: crear campaña, elegir guion, generar imágenes
    │   └── publicacion.py  # contrato para redes sociales (sin redes activas)
    └── presentacion/
        ├── rutas.py        # endpoints Flask
        └── templates/      # base.html, index.html, campana.html
```

## Flujo de estados de una campaña

```text
GUIONES_PROPUESTOS --> GENERANDO --> IMAGENES_LISTAS
        ^                  |
        |                  v
        +---------------- ERROR (se puede reintentar eligiendo otro guion)
```

## Requisitos

- Python 3.12 (para ejecución local).
- Docker y Docker Compose (para ejecución en contenedores).
- Una clave de API de OpenAI con acceso a un modelo de texto y a un modelo de imagen.

## Variables de entorno

Copia la plantilla y edítala. El archivo `.env` nunca debe subirse al repositorio.

```bash
cp .env.example .env
```

| Variable | Obligatoria | Descripción |
|---|---|---|
| `SECRET_KEY` | Sí | Clave para sesiones de Flask. Usa una cadena larga y aleatoria. |
| `POSTGRES_DB` | Sí (Docker) | Nombre de la base de datos. |
| `POSTGRES_USER` | Sí (Docker) | Usuario de PostgreSQL. |
| `POSTGRES_PASSWORD` | Sí (Docker) | Contraseña de PostgreSQL. |
| `DOCKERHUB_USER` | Solo para publicar imagen | Usuario de Docker Hub. |
| `OPENAI_API_KEY` | Sí | Clave de API de OpenAI. |
| `OPENAI_TEXT_MODEL` | No | Modelo para guiones. Por defecto `gpt-5`. |
| `OPENAI_IMAGE_MODEL` | No | Modelo para imágenes. Usa `gpt-image-2` si tu cuenta lo tiene. |
| `IMAGE_QUALITY` | No | `low`, `medium` o `high`. Por defecto `low` (más barato). |

Ejemplo de `.env`:

```text
SECRET_KEY=cambia-esta-clave-larga
POSTGRES_DB=marketing
POSTGRES_USER=marketing
POSTGRES_PASSWORD=cambia-esta-clave-db
DOCKERHUB_USER=tu_usuario

OPENAI_API_KEY=sk-...
OPENAI_TEXT_MODEL=gpt-5
OPENAI_IMAGE_MODEL=gpt-image-2
IMAGE_QUALITY=low
```

### Modelos de OpenAI

Los nombres de modelos cambian con frecuencia y dependen de tu cuenta. Antes de usar un valor, revisa la [lista de modelos de OpenAI](https://developers.openai.com/api/docs/models).

Si ves `The model ... does not exist`, cambia la variable en `.env` y reinicia la aplicación.

Para listar los modelos de imagen que tiene tu cuenta:

```bash
python -c "from openai import OpenAI; import os; c=OpenAI(api_key=os.environ['OPENAI_API_KEY']); print([m.id for m in c.models.list() if 'image' in m.id])"
```

## Instalación y ejecución en local (sin Docker)

Usa SQLite, que se crea automáticamente en `marketing.db`.

```bash
cd marketing-app
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # edita OPENAI_API_KEY
python run.py
```

Abre [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Ejecución con Docker en local

Levanta la aplicación y PostgreSQL con Docker Compose.

```bash
docker compose build --no-cache web
docker compose up -d
docker compose ps
docker compose logs --tail=50 web
```

Abre [http://localhost:5000](http://localhost:5000).

Comandos útiles:

```bash
docker compose down          # detiene los contenedores y conserva los datos
docker compose down -v       # detiene todo y borra la base y las imágenes
docker compose up -d --force-recreate web   # recarga las variables de .env
```

## Uso

1. En la página principal, introduce empresa, producto o servicio, y sube una foto (jpg, jpeg, png o webp, máximo 10 MB).
2. Pulsa **Crear campaña**. La aplicación genera 3 guiones.
3. Elige un guion y pulsa **Generar 3 imágenes con IA**. La generación tarda uno o dos minutos.
4. Cuando el estado sea `IMAGENES_LISTAS`, verás las 3 imágenes.

Si la generación falla, el estado pasa a `ERROR`. Puedes elegir otro guion para reintentar.

## Despliegue en AWS EC2

### 1. Publicar la imagen en Docker Hub

```bash
docker login
docker compose build web
docker push TU_USUARIO/marketing-app:4.0
```

### 2. Crear la instancia

- Ubuntu 24.04, `t3.small`, disco de 16 GB, par de claves SSH.
- Security Group:
  - SSH (22) solo desde tu IP.
  - TCP 5000 solo desde tu IP (pruebas).
  - No abras el puerto 5432.

La aplicación no tiene inicio de sesión. No la abras a `0.0.0.0/0`, porque cualquiera podría usar tu saldo de OpenAI.

### 3. Instalar Docker en el servidor

```bash
ssh -i clave.pem ubuntu@IP_PUBLICA
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu && newgrp docker
```

### 4. Copiar los archivos de despliegue

El `.env` con las claves reales solo debe existir en el servidor.

```bash
scp -i clave.pem docker-compose.yml .env ubuntu@IP_PUBLICA:~/
```

### 5. Arrancar

```bash
cd ~
docker compose pull web
docker compose up -d
docker compose ps
docker compose logs --tail=50 web
```

Abre `http://IP_PUBLICA:5000` y comprueba el flujo completo.

## Solución de problemas

| Síntoma | Causa probable |
|---|---|
| `Falta OPENAI_API_KEY` | `.env` no existe o no contiene la clave. |
| `The model '...' does not exist` | El nombre del modelo no está disponible para tu cuenta. Cambia la variable. |
| Error al generar guiones | Clave sin saldo o modelo de texto incorrecto. |
| La generación tarda mucho | Normal: son 3 llamadas de imagen. Usa `IMAGE_QUALITY=low`. |
| `connection refused` a `db` | PostgreSQL aún no está listo. Espera a que aparezca `healthy` en `docker compose ps`. |
| Puerto 5000 ocupado | Cambia el primer número en `ports`, por ejemplo `"5001:5000"`. |
| Cambios en `.env` no tienen efecto | Recrea el contenedor con `docker compose up -d --force-recreate web`. |

## Seguridad y costes

- `OPENAI_API_KEY` y las contraseñas solo deben estar en `.env`. No las incluyas en el Dockerfile ni en la imagen publicada.
- Si una clave se expone, revócala en el panel de OpenAI y crea otra.
- Cada imagen generada tiene coste. Usa `IMAGE_QUALITY=low` para pruebas.
- La aplicación no tiene autenticación. Antes de exponerla a internet, añade un control de acceso.

## Próximos pasos

- Añadir publicación en TikTok: crear `app/datos/tiktok.py` y `app/datos/video.py`, implementar `Publicador` en `app/negocio/publicacion.py` y añadir las rutas OAuth.
- Cifrar los tokens de redes sociales o usar un gestor de secretos (AWS Secrets Manager).
- Añadir autenticación de usuarios.

## Licencia

Pendiente de definir.
