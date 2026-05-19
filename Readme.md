# AgroNexa Backend

Backend del sistema **AgroNexa**, plataforma agrotech para registro de parcelas, muestras de campo, imágenes, datos del sensor y diagnósticos agrícolas.

---

## 1. Tecnologías

| Herramienta | Uso |
|---|---|
| Python 3.11+ | Lenguaje principal |
| Flask | Framework web |
| Flask-JWT-Extended | Autenticación con tokens JWT |
| Flask-Bcrypt | Encriptación de contraseñas |
| Flask-CORS | Control de acceso entre dominios |
| Flasgger | Documentación Swagger / OpenAPI |
| PyMongo | Conexión con MongoDB |
| Cloudinary | Almacenamiento de imágenes |
| Python Dotenv | Variables de entorno |

---

## 2. Instalación

### Clonar repositorio

```bash
git clone <url-del-repositorio>
cd Backend-AgroNexa
```

### Crear entorno virtual

```bash
python -m venv venv
```

### Activar entorno virtual

Windows:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Configurar variables de entorno

Copiar o crear el archivo `.env` en la raíz del proyecto:

```env
FLASK_ENV=development
FLASK_APP=run.py
PORT=5000

MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=agronexa_db

JWT_SECRET_KEY=super_secret_key_change_me
JWT_ACCESS_TOKEN_EXPIRES=3600

CORS_ORIGINS=http://localhost:4200

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

GOOGLE_MAPS_API_KEY=
```

### Ejecutar servidor

```bash
python run.py
```

Servidor disponible en:

```
http://localhost:5000
```

---

## 3. Documentación Swagger

La documentación interactiva de la API está disponible en:

```
http://localhost:5000/api/docs
```

Generada automáticamente con **Flasgger** a partir de los docstrings de cada endpoint.

Para usar endpoints protegidos desde Swagger:

1. Hacer `POST /api/auth/login` y copiar el `token` de la respuesta.
2. En cada endpoint protegido, hacer clic en el candado o agregar el header:
   ```
   Authorization: Bearer <token>
   ```

---

## 4. Usuario administrador

Al arrancar el servidor por primera vez se crea automáticamente un usuario admin:

```
Correo:   admin@agronexa.com
Password: Admin123!
Rol:      admin
```

---

## 5. Endpoints de la API

### Auth — `/api/auth`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/register` | Registrar usuario | No |
| POST | `/login` | Iniciar sesión | No |
| GET | `/me` | Usuario autenticado | JWT |

### Usuarios — `/api/users`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| GET | `/me` | Ver mi perfil | JWT |
| PUT | `/me` | Actualizar mi perfil | JWT |
| GET | `/` | Listar usuarios | JWT |
| GET | `/<id>` | Ver usuario | JWT |
| PUT | `/<id>/status` | Cambiar estado | JWT |

### Admin — `/api/admin`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| GET | `/usuarios` | Listar todos los usuarios | JWT + admin |
| GET | `/usuarios/<id>` | Detalle de usuario | JWT + admin |
| PUT | `/usuarios/<id>/estado` | Activar / suspender / desactivar | JWT + admin |
| DELETE | `/usuarios/<id>` | Eliminar usuario | JWT + admin |
| GET | `/estadisticas` | Estadísticas de la plataforma | JWT + admin |

### Parcelas — `/api/parcelas`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/` | Crear parcela | JWT |
| GET | `/` | Listar mis parcelas | JWT |
| GET | `/<id>` | Detalle de parcela | JWT |
| PUT | `/<id>` | Actualizar parcela | JWT |
| DELETE | `/<id>` | Eliminar parcela | JWT |
| GET | `/<id>/muestras` | Muestras de una parcela | JWT |

### Muestras — `/api/muestras`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/` | Crear muestra | JWT |
| GET | `/` | Listar mis muestras | JWT |
| GET | `/<id>` | Detalle de muestra | JWT |
| PUT | `/<id>` | Actualizar muestra | JWT |
| DELETE | `/<id>` | Eliminar muestra | JWT |
| GET | `/<id>/diagnostico` | Diagnóstico de la muestra | JWT |
| GET | `/<id>/imagenes` | Imágenes de la muestra | JWT |

### Diagnósticos — `/api/diagnosticos`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/generar/<muestra_id>` | Generar diagnóstico | JWT |
| GET | `/<id>` | Ver diagnóstico | JWT |

### Imágenes — `/api/imagenes`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/upload` | Subir imagen (multipart) | JWT |
| DELETE | `/<id>?muestraId=` | Eliminar imagen | JWT |

### Suscripciones — `/api`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| GET | `/planes` | Listar planes | No |
| POST | `/suscripciones` | Crear suscripción | JWT |
| GET | `/suscripciones/actual` | Mi suscripción activa | JWT |
| PUT | `/suscripciones/cambiar-plan` | Cambiar plan | JWT |

### Configuración — `/api`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| GET | `/config/maps` | API key pública de Google Maps | No |

---

## 6. Estructura de colecciones MongoDB

### users

```json
{
  "nombre": "Oscar",
  "apellido": "Chavez",
  "correo": "oscar@ejemplo.com",
  "password": "<hash bcrypt>",
  "telefono": "999999999",
  "rol": "productor | asociacion | institucion | admin",
  "plan": "basico | plus | asociacion | institucional",
  "estado": "activo | inactivo | suspendido",
  "createdAt": "date",
  "updatedAt": "date"
}
```

### parcelas

```json
{
  "userId": "ObjectId",
  "nombre": "Parcela Norte",
  "cultivo": "cacao",
  "ubicacion": { "lat": -9.12, "lng": -75.22 },
  "referencia": "A 10 minutos del caserío",
  "areaAproximada": 2.5,
  "unidadArea": "ha",
  "observaciones": "Zona con pendiente moderada",
  "variedad": "CCN-51",
  "edadCultivo": "3 a 5 años",
  "cantidadPlantas": 500,
  "sistemaCultivo": "agroforestal",
  "estado": "activo",
  "createdAt": "date",
  "updatedAt": "date"
}
```

Campos obligatorios: `nombre`, `cultivo`, `ubicacion`, `referencia`

### muestras

```json
{
  "parcelaId": "ObjectId",
  "userId": "ObjectId",
  "parteAfectada": "hoja | fruto | tallo | raiz | flor | planta_completa",
  "nivelAfectacion": "leve | moderado | severo",
  "sintomas": ["manchas oscuras", "pudricion"],
  "observaciones": "Apareció después de las lluvias",
  "datosSensor": {
    "ph": 6.5,
    "nitrogeno": 45.0,
    "fosforo": 30.0,
    "potasio": 120.0,
    "humedadSuelo": 65.0,
    "temperaturaSuelo": 22.0,
    "conductividadElectrica": 1.2
  },
  "estado": "registrado | diagnosticado | eliminado",
  "createdAt": "date",
  "updatedAt": "date"
}
```

Campos obligatorios: `parcelaId`, `parteAfectada`, `nivelAfectacion`, `sintomas`

### imagenes_muestra

```json
{
  "muestraId": "ObjectId",
  "userId": "ObjectId",
  "url": "https://res.cloudinary.com/...",
  "publicId": "agronexa/muestras/...",
  "tipoImagen": "hoja | fruto | tallo | planta_completa | suelo",
  "descripcion": "Fruto con manchas oscuras",
  "createdAt": "date"
}
```

### diagnosticos

```json
{
  "muestraId": "ObjectId",
  "parcelaId": "ObjectId",
  "userId": "ObjectId",
  "resultado": {
    "riesgo": "bajo | moderado | alto",
    "enfermedad": "moniliasis | escoba de bruja | pudricion parda | no determinado",
    "confianza": 0.85
  },
  "motivo": "Análisis basado en parte afectada 'fruto', síntomas registrados y datos del sensor.",
  "recomendaciones": ["Retirar frutos afectados", "..."],
  "createdAt": "date"
}
```

### suscripciones

```json
{
  "userId": "ObjectId",
  "plan": "basico | plus | asociacion | institucional",
  "precio": 15,
  "estado": "activo",
  "fechaInicio": "date",
  "fechaFin": "date",
  "trial": true,
  "trialInicio": "date",
  "trialFin": "date",
  "createdAt": "date"
}
```

---

## 7. Roles

| Rol | Descripción |
|---|---|
| `productor` | Usuario de campo: parcelas, muestras, diagnósticos |
| `asociacion` | Gestión de productores asociados |
| `institucion` | Monitoreo territorial |
| `admin` | Administración de la plataforma |

---

## 8. Planes

| Plan | Precio | Límites |
|---|---|---|
| `basico` | Gratis | 2 parcelas, 3 muestras/mes |
| `plus` | S/ 15/mes | Ilimitado + 30 días trial |
| `asociacion` | S/ 200/mes | Multi-productor + 30 días trial |
| `institucional` | S/ 350/mes | Monitoreo territorial + 30 días trial |

---

## 9. Respuesta estándar

```json
{ "success": true, "message": "Operación realizada", "data": {} }
```

```json
{ "success": false, "message": "Descripción del error", "error": {} }
```

---

## 10. Arquitectura

```
Routes → Controllers → Services → Repositories → MongoDB
```

| Capa | Responsabilidad |
|---|---|
| Routes | Define endpoints y aplica JWT |
| Controllers | Recibe HTTP, docstrings Swagger |
| Services | Lógica de negocio y validaciones |
| Repositories | Consultas a MongoDB |
| Middleware | Autenticación y control de roles |
| Utils | Respuestas, validadores, helpers |

---

## 11. Dependencias

```
Flask
Flask-Cors
Flask-JWT-Extended
Flask-Bcrypt
pymongo
python-dotenv
cloudinary
marshmallow
pytest
flasgger
```
