# 🎓 Sistema de Carnetización SENA — Centro de Biotecnología Industrial

Sistema web para la generación, gestión y administración de carnets institucionales para aprendices del **SENA Regional Valle del Cauca**, desarrollado como proyecto de investigación aplicada con metodología SCRUM.

---

## 📋 Descripción General

Esta aplicación permite al Centro de Biotecnología Industrial automatizar todo el ciclo de vida de un carnet institucional: desde la carga masiva de datos vía plantilla Excel, el procesamiento inteligente de fotografías con eliminación de fondo por IA, hasta la generación del carnet físico (anverso y reverso) listo para impresión a 300 DPI.

El sistema cuenta con dos roles diferenciados: **Administrador** y **Aprendiz**, cada uno con su propio flujo de trabajo y panel de control.

---

## ✨ Funcionalidades Principales

### Panel Administrador
- Dashboard con métricas en tiempo real (aprendices registrados, carnets generados, estado de fotos)
- Registro individual de aprendices con validación completa de datos SENA
- **Carga masiva por Excel** con detección automática de duplicados (umbral configurable al 80%)
- Generación individual y **masiva de carnets por ficha** (anverso + reverso combinados)
- Consulta y búsqueda de aprendices con filtros por nombre, cédula, ficha, programa y estado de foto
- Gestión de fotos: carga, actualización y eliminación con **backup automático** por fecha
- Gestión de fichas: resumen estadístico por ficha con porcentaje de avance fotográfico
- Archivo de carnets generados, agrupable por ficha o por programa
- Reportes estadísticos por cargo, nivel de formación, programa y ficha
- Administración de backups: visualización, descarga y limpieza automática de respaldos anteriores a 6 meses
- Verificación de carnets por código QR

### Portal Aprendiz
- Consulta de datos personales registrados por cédula
- Carga autónoma de foto de perfil (procesada automáticamente con IA)
- Notificación de estado del carnet

---

## 🧠 Procesamiento Inteligente de Fotografías

El módulo `procesador_fotos.py` implementa una pipeline automática de procesamiento:

1. **Detección de fondo blanco**: si el 70% o más de los píxeles del borde son blancos (RGB ≥ 200), la foto se copia sin modificaciones.
2. **Eliminación de fondo con IA**: para fondos no blancos, utiliza el modelo `u2net_human_seg` de `rembg` con alpha-matting para una segmentación precisa de personas.
3. **Limpieza de residuos**: eliminación de artefactos en bordes usando OpenCV (componentes conectados, análisis HSV).
4. **Redimensionado a formato carnet**: recorte y ajuste proporcional al formato 3×4 (220×270 px).
5. **Fallback con OpenCV**: si `rembg` no está disponible, el sistema recurre a un método alternativo de detección de fondo por color mediano.

---

## 🖨️ Generación del Carnet

El módulo `imagen.py` produce carnets a **300 DPI** en formato 5.5×8.7 cm:

- **Anverso**: logo SENA, foto del aprendiz, nombre, cargo, cédula, RH, código QR (enlace a SofiaSoftPlus), footer con información del centro.
- **Reverso**: texto institucional con justificación automática, firma de la directora, programa y código de ficha.
- **Imagen combinada**: anverso y reverso lado a lado en un único archivo PNG para revisión o impresión.

El sistema de fuentes es robusto: prueba múltiples rutas (Windows/Linux) y cae graciosamente a la fuente por defecto si ninguna está disponible.

---

## 🗄️ Base de Datos

Motor: **SQLite** (`carnet.db`) con la tabla principal `empleados`. El esquema incluye los siguientes campos clave:

| Campo | Descripción |
|---|---|
| `cedula` | Número de documento (clave única) |
| `nis` | Número de Identificación SENA |
| `nombre`, `primer_apellido`, `segundo_apellido` | Nombre completo |
| `nombre_programa` | Programa de formación |
| `codigo_ficha` | Ficha SENA |
| `nivel_formacion` | Técnico / Tecnólogo (inferido automáticamente) |
| `tipo_sangre` | Grupo sanguíneo |
| `foto` | Nombre del archivo de foto procesada |
| `fecha_emision`, `fecha_vencimiento` | Vigencia del carnet |

Se crean índices automáticos sobre `cedula`, `codigo`, `nombre_programa`, `codigo_ficha` y `fecha_emision` para optimizar las consultas.

---

## 🛠️ Stack Tecnológico

| Área | Tecnologías |
|---|---|
| **Backend** | Python 3, Flask |
| **Base de datos** | SQLite, SQL, SQLAlchemy |
| **Procesamiento de imágenes** | Pillow (PIL), OpenCV, rembg (u2net_human_seg) |
| **ETL / Datos** | Pandas, openpyxl (limpieza y carga de datos Excel) |
| **Generación QR** | qrcode |
| **Frontend** | HTML5, CSS3, Jinja2 |
| **Metodología** | SCRUM, Investigación y Desarrollo |
| **Herramientas** | PowerShell (scripts de red y servidor) |

---

## ⚙️ Instalación y Ejecución

### Requisitos previos
- Python 3.9+
- pip

### Instalación de dependencias

```bash
pip install flask flask-sqlalchemy flask-mail pillow opencv-python pandas openpyxl qrcode rembg numpy werkzeug
```

### Ejecución

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`.

Para ejecutar en red local (LAN), utiliza el script `iniciar_servidor.ps1` en Windows. El script `obtener_ip.ps1` permite identificar la dirección IP del equipo servidor.

---

## 🔑 Credenciales de Acceso (Entorno de Desarrollo)

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `sena` | `sena2024` | Administrador |
| `usuario` | `123456` | Administrador |
| `aprendiz` | `aprendiz123` | Aprendiz |


---

## 📊 Flujo de Trabajo Principal

```
Excel SENA → Carga masiva → Validación de duplicados → Registro en BD
                                                              ↓
                                                    Aprendiz sube foto
                                                              ↓
                                                  Pipeline IA de procesamiento
                                                              ↓
                                              Admin genera carnet (individual o por ficha)
                                                              ↓
                                                  Carnet PNG listo para impresión
```

---

## 📡 API REST Interna

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/metricas_dashboard` | GET | Métricas en tiempo real para el dashboard |
| `/api/lista_aprendices_filtrada` | GET | Lista de aprendices con filtros |
| `/api/buscar_aprendiz/<cedula>` | GET | Datos completos de un aprendiz |
| `/api/editar_aprendiz` | POST | Edición de datos de un aprendiz |
| `/api/estadisticas_fichas` | GET | Estadísticas agrupadas por ficha |
| `/api/carnets_generados` | GET | Cédulas con carnet generado en disco |
| `/actualizar_foto_rapido` | POST | Carga/actualización de foto |
| `/eliminar_ficha` | POST | Eliminación de ficha y archivos asociados |
| `/eliminar_empleado/<cedula>` | POST | Eliminación de un aprendiz |

---

## 👥 Equipo de Desarrollo

**Instructor Líder**
- Mayron (Instructor SENA)

**Desarrolladores Auxiliares**

- Alejandro Tamayo
- Alejandro Ducuara
- Juan David Cadena
- Edison Andrés Martínez
- Sergio Bustos
 
---

## 🏛️ Información Institucional

**Institución:** Servicio Nacional de Aprendizaje — SENA  
**Regional:** Valle del Cauca  
**Centro:** Centro de Biotecnología Industrial  
**Ubicación:** Calle 40 #30-44, Palmira, Valle del Cauca  

---

## 📄 Licencia

Proyecto desarrollado con fines institucionales y académicos para el SENA. Todos los derechos reservados al Centro de Biotecnología Industrial — Regional Valle del Cauca.
