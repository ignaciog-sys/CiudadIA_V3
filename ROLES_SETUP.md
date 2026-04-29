# 🏙️ CiudadIA - Sistema de Roles (Admin y Ciudadano)

## Cambios Implementados

Se ha implementado un sistema de dos roles de usuario con dashboards y rutas diferenciadas:

### **Usuarios de Prueba**

#### Admin (Administrador)
- **Usuario:** `api_user`
- **Contraseña:** `change_me`
- **Rol:** Admin
- **Acceso:** `/admin/dashboard`
- **Mensaje:** ⚠️ ERES ADMIN - CONTENIDO CONFIDENCIAL

#### Ciudadano
- **Usuario:** `citizen_user`
- **Contraseña:** `citizen_pass`
- **Rol:** Citizen
- **Acceso:** `/citizen/dashboard`
- **Mensaje:** 🏙️ ERES CIUDADANO - CUIDA TU CIUDAD

---

## Cambios Realizados

### Backend (`backend/src/`)

1. **Modelo de Autenticación** (`models/auth.py`)
   - Actualizado para incluir `role` con valores: "admin" o "citizen"

2. **Servicio de Autenticación** (`services/auth_service.py`)
   - `authenticate_demo_user()`: Acepta dos usuarios (admin y citizen)
   - `decode_demo_token()`: Retorna el rol correspondiente a cada token

3. **Routers Nuevos**
   - `routers/admin_router.py`: Rutas exclusivas para administradores
   - `routers/citizen_router.py`: Rutas exclusivas para ciudadanos

4. **App Principal** (`app.py`)
   - Registrados los nuevos routers con validación de roles

---

### Frontend (`frontend/`)

1. **Rutas de Autenticación** (`routes/auth.py`)
   - Login actualizado para guardar `role` y `username` en sesión
   - Redirección automática según rol después del login

2. **Rutas de Páginas** (`routes/pages.py`)
   - Ruta `/` redirige según el rol
   - Nueva ruta `/admin/dashboard` (solo para admins)
   - Nueva ruta `/citizen/dashboard` (solo para ciudadanos)
   - Protección de acceso: Si no tienes el rol correcto, te redirige al login

3. **Templates Nuevos**
   - `templates/admin_dashboard.html`: Panel administrativo con tema morado
   - `templates/citizen_dashboard.html`: Panel de ciudadano con tema verde

---

## Cómo Probar

### 1. **Iniciar la API (Backend)**
```bash
cd backend
pip install -r requirements.txt
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

### 2. **Iniciar el Frontend**
```bash
cd frontend
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

### 3. **Login como Admin**
- Ir a `http://localhost:8001/login`
- Usuario: `api_user`
- Contraseña: `change_me`
- Serás redirigido a `/admin/dashboard` con acceso al panel administrativo

### 4. **Login como Ciudadano**
- Ir a `http://localhost:8001/login`
- Usuario: `citizen_user`
- Contraseña: `citizen_pass`
- Serás redirigido a `/citizen/dashboard` con acceso al panel de ciudadano

### 5. **Validación de Roles**
- Si intentas acceder directamente a `/admin/dashboard` siendo ciudadano, serás redirigido al login
- Si intentas acceder a `/citizen/dashboard` siendo admin, serás redirigido al login

---

## Endpoints de la API

### Admin
- `GET /api/v1/admin/dashboard` - Panel administrativo (solo admin)

### Citizen
- `GET /api/v1/citizen/dashboard` - Panel ciudadano (solo ciudadano)

### Auth
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Información del usuario actual

---

## Próximos Pasos

Para expandir el sistema, considera:

1. **Base de Datos Real**
   - Migrar de usuarios mock a base de datos
   - Implementar tabla de usuarios con roles

2. **Funcionalidades de Admin**
   - Ver todos los tickets de incidencias
   - Clasificar urgencia según modelo ML
   - Marcar tickets como resueltos

3. **Funcionalidades de Ciudadano**
   - Crear nuevos tickets de incidencias
   - Ver estado de sus reportes
   - Subir fotos de las incidencias

4. **Seguridad**
   - Implementar JWT real en lugar de tokens mock
   - Hash de contraseñas con bcrypt
   - Rate limiting

5. **Integración con Modelo ML**
   - Clasificar urgencia automáticamente
   - Análisis de imágenes de incidencias
