# AgroNexa Backend — Guía de ejecución

## Requisitos previos

- Python 3.11+
- MongoDB corriendo en `localhost:27017`
- Git

---

## 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Backend-AgroNexa
```

---

## 2. Crear y activar entorno virtual

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
FLASK_ENV=development
FLASK_APP=run.py
PORT=5000

MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=agronexa_db

JWT_SECRET_KEY=super_secret_key_change_me
JWT_ACCESS_TOKEN_EXPIRES=3600

CORS_ORIGINS=http://localhost:4200

CLOUDINARY_CLOUD_NAME=djtlci73u
CLOUDINARY_API_KEY=master
CLOUDINARY_API_SECRET=uC8nHawwU1PtOK_e08SZw83hzBs
```

---

## 5. Levantar el servidor

```bash
python run.py
```

Servidor disponible en:

```
http://localhost:5000
```

Al iniciar, el sistema crea automáticamente los índices de MongoDB y registra los 4 planes de suscripción.

---

## 6. Probar la API

### Registrar usuario

```http
POST http://localhost:5000/api/auth/register
Content-Type: application/json

{
  "nombre": "Oscar",
  "apellido": "Chavez",
  "correo": "oscar@gmail.com",
  "password": "123456",
  "telefono": "999999999",
  "rol": "productor"
}
```

### Iniciar sesión

```http
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "correo": "oscar@gmail.com",
  "password": "123456"
}
```

Respuesta:

```json
{
  "success": true,
  "data": {
    "token": "<jwt-token>",
    "rol": "productor",
    "plan": "basico"
  }
}
```

Usar el token en las siguientes peticiones:

```
Authorization: Bearer <jwt-token>
```

---

### Crear parcela

```http
POST http://localhost:5000/api/parcelas
Authorization: Bearer <token>
Content-Type: application/json

{
  "nombre": "Parcela Norte",
  "ubicacion": { "lat": -9.12, "lng": -75.22 },
  "area": 2.5,
  "unidadArea": "ha",
  "cultivo": "cacao",
  "variedad": "CCN-51",
  "edadCultivo": "3 a 5 años",
  "cantidadPlantas": 500,
  "sistemaCultivo": "agroforestal",
  "referencia": "A 10 minutos del caserío"
}
```

---

### Registrar muestra

```http
POST http://localhost:5000/api/muestras
Authorization: Bearer <token>
Content-Type: application/json

{
  "parcelaId": "<id-de-la-parcela>",
  "parteAfectada": "fruto",
  "etapaCultivo": "fructificacion",
  "nivelAfectacion": "moderado",
  "observaciones": "Manchas en frutos de la parte baja",
  "sintomas": ["manchas oscuras", "pudricion", "polvo blanco"],
  "datosSuelo": {
    "ph": 5.5,
    "nitrogeno": "medio",
    "fosforo": "bajo",
    "potasio": "medio",
    "humedad": "alta"
  },
  "datosAmbiente": {
    "temperatura": 27,
    "humedadAmbiental": 85,
    "lluviasRecientes": true,
    "sombraExcesiva": true
  }
}
```

---

### Generar diagnóstico

```http
POST http://localhost:5000/api/diagnosticos/generar/<muestraId>
Authorization: Bearer <token>
```

---

### Subir imagen

```http
POST http://localhost:5000/api/imagenes/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <archivo>
muestraId: <id-de-la-muestra>
tipo: fruto
descripcion: Fruto con manchas oscuras
```

---

### Ver planes disponibles

```http
GET http://localhost:5000/api/planes
```

---

### Suscribirse a un plan

```http
POST http://localhost:5000/api/suscripciones
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan": "plus"
}
```

Planes disponibles: `basico`, `plus`, `asociacion`, `institucional`

---

## 7. Endpoints completos

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| POST | /api/auth/register | No | Registrar usuario |
| POST | /api/auth/login | No | Iniciar sesión |
| GET | /api/auth/me | Si | Usuario autenticado |
| GET | /api/users/me | Si | Ver perfil |
| PUT | /api/users/me | Si | Actualizar perfil |
| GET | /api/users | Si | Listar usuarios |
| GET | /api/users/:id | Si | Ver usuario |
| PUT | /api/users/:id/status | Si | Cambiar estado |
| POST | /api/parcelas | Si | Crear parcela |
| GET | /api/parcelas | Si | Listar parcelas |
| GET | /api/parcelas/:id | Si | Detalle parcela |
| PUT | /api/parcelas/:id | Si | Actualizar parcela |
| DELETE | /api/parcelas/:id | Si | Eliminar parcela |
| GET | /api/parcelas/:id/muestras | Si | Muestras de parcela |
| POST | /api/muestras | Si | Registrar muestra |
| GET | /api/muestras | Si | Listar muestras |
| GET | /api/muestras/:id | Si | Detalle muestra |
| PUT | /api/muestras/:id | Si | Actualizar muestra |
| DELETE | /api/muestras/:id | Si | Eliminar muestra |
| GET | /api/muestras/:id/diagnostico | Si | Diagnóstico de muestra |
| GET | /api/muestras/:id/imagenes | Si | Imágenes de muestra |
| POST | /api/diagnosticos/generar/:id | Si | Generar diagnóstico |
| GET | /api/diagnosticos/:id | Si | Ver diagnóstico |
| POST | /api/imagenes/upload | Si | Subir imagen |
| DELETE | /api/imagenes/:id?muestraId= | Si | Eliminar imagen |
| GET | /api/planes | No | Ver planes |
| POST | /api/suscripciones | Si | Suscribirse |
| GET | /api/suscripciones/actual | Si | Suscripción activa |
| PUT | /api/suscripciones/cambiar-plan | Si | Cambiar plan |
