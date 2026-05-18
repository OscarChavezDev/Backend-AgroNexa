# AgroNexa Backend

Backend del sistema **AgroNexa**, una plataforma agrotech orientada al registro de parcelas, muestras de campo, análisis de síntomas, datos del suelo, imágenes y generación de diagnósticos preliminares para cultivos.

AgroNexa permite que productores, asociaciones e instituciones gestionen información agrícola, realicen seguimiento de parcelas, registren muestras, reciban recomendaciones preventivas y consulten el historial de diagnósticos por parcela.

---

## 1. Descripción del proyecto

**AgroNexa** es una solución tecnológica para el monitoreo agrícola.

El sistema permite que el usuario registre parcelas, agregue muestras de campo, suba imágenes del cultivo, ingrese síntomas visibles, registre datos del suelo como pH, NPK y humedad, y obtenga una orientación inicial sobre posibles enfermedades o riesgos del cultivo.

El backend proporciona una API REST organizada, segura y escalable para conectarse con la aplicación frontend.

---

## 2. Objetivo del backend

El backend permitirá:

- Registrar usuarios.
- Iniciar sesión con JWT.
- Manejar roles de usuario.
- Registrar parcelas agrícolas.
- Guardar ubicación geográfica de parcelas.
- Registrar muestras de campo.
- Subir imágenes asociadas a muestras.
- Registrar síntomas visibles.
- Registrar datos de suelo.
- Generar diagnósticos preliminares.
- Guardar historial por parcela.
- Gestionar planes y suscripciones.
- Preparar la arquitectura para una futura integración con Machine Learning.

---

## 3. Arquitectura recomendada

El backend usará una arquitectura modular basada en dominios, aplicando una versión ligera de Clean Architecture.

Flujo general:

```txt
Routes
  ↓
Controllers
  ↓
Services
  ↓
Repositories
  ↓
MongoDB
```

### Responsabilidad de cada capa

| Capa | Responsabilidad |
|---|---|
| Routes | Define los endpoints de la API |
| Controllers | Recibe peticiones HTTP y valida datos básicos |
| Services | Contiene la lógica de negocio |
| Repositories | Ejecuta consultas hacia MongoDB |
| Database | Maneja conexión, índices y configuración |
| Middleware | Protege rutas y valida roles |
| Utils | Contiene respuestas, validadores y helpers |

---

## 4. Tecnologías utilizadas

### Backend

- Python 3.11+
- Flask
- Flask-JWT-Extended
- Flask-Bcrypt
- Flask-CORS
- PyMongo
- Python Dotenv

### Base de datos

- MongoDB

### Storage de imágenes

- Cloudinary recomendado
- AWS S3 como alternativa
- Storage local solo para desarrollo o prototipo

### Seguridad

- JWT para autenticación.
- Bcrypt para encriptar contraseñas.
- Middleware para rutas protegidas.
- Control de acceso por roles.
- Validación de datos de entrada.

---

## 5. Estructura del proyecto

```txt
agronexa-backend/
│
├── app/
│   ├── __init__.py
│   │
│   ├── config/
│   │   ├── config.py
│   │   └── mongodb.py
│   │
│   ├── extensions/
│   │   ├── jwt.py
│   │   └── bcrypt.py
│   │
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── routes.py
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── models.py
│   │   │
│   │   ├── users/
│   │   │   ├── routes.py
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── models.py
│   │   │
│   │   ├── parcelas/
│   │   │   ├── routes.py
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── models.py
│   │   │
│   │   ├── muestras/
│   │   │   ├── routes.py
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── models.py
│   │   │
│   │   ├── diagnostico/
│   │   │   ├── routes.py
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── rules.py
│   │   │
│   │   ├── imagenes/
│   │   │   ├── routes.py
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   └── repository.py
│   │   │
│   │   └── suscripciones/
│   │       ├── routes.py
│   │       ├── controller.py
│   │       ├── service.py
│   │       ├── repository.py
│   │       └── models.py
│   │
│   ├── middleware/
│   │   ├── auth_middleware.py
│   │   └── role_middleware.py
│   │
│   ├── utils/
│   │   ├── response.py
│   │   ├── validators.py
│   │   └── helpers.py
│   │
│   ├── database/
│   │   ├── mongo.py
│   │   └── indexes.py
│   │
│   └── main.py
│
├── tests/
│   ├── test_auth.py
│   ├── test_parcelas.py
│   └── test_muestras.py
│
├── .env
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

---

## 6. Módulos del sistema

### 6.1 Auth

Módulo encargado del registro, inicio de sesión y autenticación.

Funciones:

- Registrar usuario.
- Validar correo único.
- Encriptar contraseña.
- Iniciar sesión.
- Generar token JWT.
- Obtener usuario autenticado.

Endpoints sugeridos:

```txt
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

---

### 6.2 Users

Módulo encargado de administrar los datos del usuario.

Funciones:

- Ver perfil.
- Actualizar perfil.
- Cambiar estado del usuario.
- Consultar usuarios por rol.
- Actualizar plan del usuario.

Endpoints sugeridos:

```txt
GET    /api/users/me
PUT    /api/users/me
GET    /api/users
GET    /api/users/:id
PUT    /api/users/:id/status
```

---

### 6.3 Parcelas

Módulo encargado del registro y administración de parcelas.

Funciones:

- Crear parcela.
- Listar parcelas del usuario.
- Ver detalle de parcela.
- Actualizar parcela.
- Eliminar o desactivar parcela.
- Registrar ubicación GPS.
- Guardar datos agrícolas básicos.

Endpoints sugeridos:

```txt
POST   /api/parcelas
GET    /api/parcelas
GET    /api/parcelas/:id
PUT    /api/parcelas/:id
DELETE /api/parcelas/:id
```

---

### 6.4 Muestras

Módulo encargado del registro de muestras o reportes de campo.

Funciones:

- Crear muestra.
- Asociar muestra a una parcela.
- Registrar parte afectada.
- Registrar síntomas visibles.
- Registrar datos del suelo.
- Registrar condiciones ambientales.
- Asociar imágenes.
- Listar muestras por usuario.
- Listar muestras por parcela.

Endpoints sugeridos:

```txt
POST   /api/muestras
GET    /api/muestras
GET    /api/muestras/:id
GET    /api/parcelas/:id/muestras
PUT    /api/muestras/:id
DELETE /api/muestras/:id
```

---

### 6.5 Diagnóstico

Módulo encargado de generar diagnósticos preliminares.

Funciones:

- Analizar síntomas.
- Evaluar datos del suelo.
- Evaluar condiciones de riesgo.
- Generar enfermedad probable.
- Calcular nivel de riesgo.
- Generar recomendaciones.
- Guardar diagnóstico asociado a la muestra.

Endpoints sugeridos:

```txt
POST /api/diagnosticos/generar/:muestraId
GET  /api/diagnosticos/:id
GET  /api/muestras/:id/diagnostico
```

---

### 6.6 Imágenes

Módulo encargado de la carga y administración de imágenes.

Funciones:

- Subir imagen.
- Guardar URL de imagen.
- Asociar imagen a una muestra.
- Eliminar imagen.
- Listar imágenes por muestra.

Endpoints sugeridos:

```txt
POST   /api/imagenes/upload
GET    /api/muestras/:id/imagenes
DELETE /api/imagenes/:id
```

---

### 6.7 Suscripciones

Módulo encargado de planes y suscripciones.

Funciones:

- Consultar planes.
- Activar plan gratuito.
- Iniciar prueba gratuita.
- Registrar suscripción.
- Consultar suscripción activa.
- Cambiar plan.
- Validar límites por plan.

Endpoints sugeridos:

```txt
GET  /api/planes
POST /api/suscripciones
GET  /api/suscripciones/actual
PUT  /api/suscripciones/cambiar-plan
```

---

## 7. Roles del sistema

```txt
productor
asociacion
institucion
```

### Productor

Puede:

- Crear cuenta.
- Registrar parcelas.
- Registrar muestras.
- Subir imágenes.
- Ingresar datos de suelo.
- Generar diagnósticos preliminares.
- Ver historial.
- Acceder a planes.

### Asociación

Puede:

- Gestionar productores asociados.
- Consultar reportes consolidados.
- Acceder a métricas por zona.
- Ver casos registrados.
- Solicitar soporte técnico.
- Exportar reportes.

### Institución

Puede:

- Monitorear zonas agrícolas.
- Consultar reportes territoriales.
- Acceder a datos consolidados.
- Gestionar usuarios por roles.
- Coordinar capacitaciones.
- Revisar indicadores generales.

---

## 8. Planes de servicio

### 8.1 Plan Básico

Precio:

```txt
Gratis
```

Incluye:

- Hasta 2 parcelas registradas.
- 3 muestras o diagnósticos al mes.
- Orientación preliminar.
- Recomendaciones preventivas básicas.
- Historial limitado por parcela.

---

### 8.2 Productor Plus

Precio:

```txt
S/ 15 al mes
```

Incluye:

- 1 mes de prueba gratis.
- Parcelas ilimitadas.
- Muestras ilimitadas.
- Registro de imágenes por muestra.
- Datos de suelo: pH, NPK y humedad.
- Alertas tempranas personalizadas.
- Historial completo por parcela.
- Soporte y revisión técnica prioritaria.

---

### 8.3 Asociación

Precio:

```txt
S/ 200 al mes
```

Incluye:

- 1 mes de prueba gratis.
- Panel multi-productor.
- Gestión de productores asociados.
- Reportes por parcela y por zona.
- Métricas consolidadas.
- Seguimiento de casos técnicos.
- Alertas por zonas de riesgo.
- Exportación de reportes.
- Capacitación inicial incluida.

---

### 8.4 Institucional

Precio:

```txt
S/ 350 al mes
```

Incluye:

- 1 mes de prueba gratis.
- Monitoreo territorial.
- Gestión avanzada por roles.
- Panel institucional.
- Reportes consolidados por zona.
- Integración de datos de suelo.
- Seguimiento de productores y asociaciones.
- Capacitaciones técnicas.
- Soporte institucional.

---

## 9. Estructura de colecciones en MongoDB

### 9.1 users

```json
{
  "_id": "ObjectId",
  "nombre": "Oscar",
  "apellido": "Chavez",
  "correo": "test@gmail.com",
  "password": "hash",
  "telefono": "999999999",
  "rol": "productor",
  "plan": "basico",
  "estado": "activo",
  "createdAt": "date",
  "updatedAt": "date"
}
```

---

### 9.2 parcelas

```json
{
  "_id": "ObjectId",
  "userId": "ObjectId",
  "nombre": "Parcela Norte",
  "ubicacion": {
    "lat": -9.12,
    "lng": -75.22
  },
  "area": 2.5,
  "unidadArea": "ha",
  "cultivo": "cacao",
  "variedad": "CCN-51",
  "edadCultivo": "3 a 5 años",
  "cantidadPlantas": 500,
  "sistemaCultivo": "agroforestal",
  "referencia": "A 10 minutos del caserío",
  "estado": "activo",
  "createdAt": "date",
  "updatedAt": "date"
}
```

---

### 9.3 muestras

```json
{
  "_id": "ObjectId",
  "parcelaId": "ObjectId",
  "userId": "ObjectId",
  "fechaObservacion": "date",
  "parteAfectada": "fruto",
  "etapaCultivo": "fructificacion",
  "nivelAfectacion": "moderado",
  "observaciones": "Manchas en frutos de la parte baja de la planta",
  "sintomas": [
    "manchas oscuras",
    "pudricion",
    "polvo blanco"
  ],
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
  },
  "imagenes": [
    {
      "url": "https://storage.com/muestra_001/fruto_1.jpg",
      "tipo": "fruto",
      "descripcion": "Fruto con manchas oscuras"
    }
  ],
  "estado": "registrado",
  "createdAt": "date",
  "updatedAt": "date"
}
```

---

### 9.4 diagnosticos

```json
{
  "_id": "ObjectId",
  "muestraId": "ObjectId",
  "parcelaId": "ObjectId",
  "userId": "ObjectId",
  "resultado": {
    "riesgo": "alto",
    "enfermedad": "moniliasis",
    "confianza": 0.82
  },
  "motivo": "Síntomas asociados a fruto afectado, polvo blanco y pudrición.",
  "recomendaciones": [
    "Retirar frutos afectados",
    "No dejar frutos enfermos en el suelo",
    "Realizar poda sanitaria",
    "Solicitar revisión técnica si el daño avanza"
  ],
  "createdAt": "date"
}
```

---

### 9.5 suscripciones

```json
{
  "_id": "ObjectId",
  "userId": "ObjectId",
  "plan": "plus",
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

### 9.6 planes

```json
{
  "_id": "ObjectId",
  "codigo": "plus",
  "nombre": "Productor Plus",
  "precio": 15,
  "moneda": "PEN",
  "periodo": "mensual",
  "trialDias": 30,
  "limites": {
    "parcelas": -1,
    "muestras": -1
  },
  "caracteristicas": [
    "Parcelas ilimitadas",
    "Muestras ilimitadas",
    "Registro de imágenes por muestra",
    "Datos de suelo: pH, NPK y humedad"
  ],
  "estado": "activo"
}
```

---

## 10. Variables de entorno

Crear un archivo `.env` en la raíz del proyecto.

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
```

---

## 11. Instalación

### Clonar repositorio

```bash
git clone <url-del-repositorio>
cd agronexa-backend
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

Linux o Mac:

```bash
source venv/bin/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar servidor

```bash
python run.py
```

Servidor disponible en:

```txt
http://localhost:5000
```

---

## 12. Dependencias sugeridas

Contenido sugerido para `requirements.txt`:

```txt
Flask
Flask-Cors
Flask-JWT-Extended
Flask-Bcrypt
pymongo
python-dotenv
cloudinary
marshmallow
pytest
```

---

## 13. Reglas iniciales de diagnóstico

El prototipo puede generar diagnósticos mediante reglas predefinidas.

### Moniliasis

```txt
Si parte afectada = fruto
y síntomas incluyen polvo blanco o fruto momificado
entonces enfermedad probable = moniliasis.
```

### Escoba de bruja

```txt
Si parte afectada = rama o brote
y síntomas incluyen brotes deformados o ramas anormales
entonces enfermedad probable = escoba de bruja.
```

### Pudrición parda

```txt
Si parte afectada = fruto
y síntomas incluyen manchas oscuras y pudrición
y la humedad es alta
entonces enfermedad probable = pudrición parda.
```

### Riesgo alto

```txt
Si el nivel de afectación es severo,
o la humedad del suelo es alta,
o hay varios síntomas críticos,
entonces el riesgo será alto.
```

---

## 14. Flujo principal del sistema

```txt
1. El usuario crea una cuenta o inicia sesión.
2. El productor registra una parcela.
3. El productor registra una nueva muestra.
4. La muestra incluye síntomas, imágenes y datos del suelo.
5. El sistema genera un diagnóstico preliminar.
6. El diagnóstico se guarda en el historial.
7. El usuario revisa recomendaciones.
8. Si el riesgo es alto, se recomienda revisión técnica.
```

---

## 15. Respuesta estándar de la API

### Respuesta exitosa

```json
{
  "success": true,
  "message": "Operación realizada correctamente",
  "data": {}
}
```

### Respuesta con error

```json
{
  "success": false,
  "message": "No se pudo procesar la solicitud",
  "error": {}
}
```

---

## 16. Ejemplo de endpoint

### Crear parcela

```http
POST /api/parcelas
Authorization: Bearer <token>
Content-Type: application/json
```

Body:

```json
{
  "nombre": "Parcela Norte",
  "ubicacion": {
    "lat": -9.12,
    "lng": -75.22
  },
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

Respuesta:

```json
{
  "success": true,
  "message": "Parcela registrada correctamente",
  "data": {
    "id": "665f123abc456"
  }
}
```

---

## 17. Seguridad

El backend debe considerar:

- Contraseñas encriptadas con Bcrypt.
- Tokens JWT para rutas protegidas.
- Validación de roles.
- Validación de datos de entrada.
- Sanitización de campos.
- Protección de endpoints privados.
- Control de acceso por usuario propietario del recurso.

---

## 18. Índices recomendados en MongoDB

### users

```txt
correo único
telefono opcional
rol
plan
```

### parcelas

```txt
userId
ubicacion 2dsphere
estado
```

### muestras

```txt
userId
parcelaId
createdAt
estado
```

### diagnosticos

```txt
muestraId
parcelaId
userId
resultado.riesgo
resultado.enfermedad
```

### suscripciones

```txt
userId
plan
estado
fechaFin
```

---

## 19. Próximas mejoras

- Panel técnico para revisión de casos.
- Panel institucional con reportes territoriales.
- Exportación de reportes en PDF.
- Notificaciones por correo o WhatsApp.
- Integración real con Machine Learning.
- Geolocalización avanzada de parcelas.
- Dashboard con mapas de riesgo.
- Integración con sensores IoT.
- Carga masiva de productores para asociaciones.
- Pasarela de pagos para suscripciones.

---

## 20. Estado del proyecto

Este backend se desarrollará como base funcional para el prototipo de AgroNexa.

Primera versión esperada:

- Registro e inicio de sesión.
- CRUD de parcelas.
- CRUD de muestras.
- Subida de imágenes.
- Diagnóstico preliminar por reglas.
- Historial de diagnósticos.
- Planes y suscripciones básicas.

---

## 21. Nombre del producto

```txt
AgroNexa
```

Eslogan sugerido:

```txt
Diagnóstico inteligente para cultivos.
```

---

## 22. Nota técnica

La primera versión del sistema generará diagnósticos preliminares a partir de reglas agrícolas definidas con base en síntomas, datos del suelo y condiciones registradas.

La arquitectura está preparada para que, en una etapa posterior, el módulo de diagnóstico pueda ser reemplazado o complementado por un modelo de Machine Learning entrenado con imágenes reales de cultivos.

---

## 23. Autoría

Proyecto desarrollado como prototipo funcional para una solución agrotech enfocada en monitoreo agrícola, diagnóstico preliminar y gestión de parcelas.
