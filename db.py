import sqlite3
import os

DB_PATH = "carnet.db"

def crear_base_datos():
    """Crea la base de datos con todas las columnas necesarias"""
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        
        # ✅ TABLA ACTUALIZADA CON TODOS LOS CAMPOS SENA + nivel_formacion
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empleados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cedula TEXT NOT NULL UNIQUE,
                tipo_documento TEXT NOT NULL,
                cargo TEXT NOT NULL,
                codigo TEXT NOT NULL UNIQUE,
                fecha_emision TEXT NOT NULL,
                fecha_vencimiento TEXT NOT NULL,
                tipo_sangre TEXT NOT NULL,
                foto TEXT,
                nis TEXT,
                primer_apellido TEXT,
                segundo_apellido TEXT,
                nombre_programa TEXT,
                codigo_ficha TEXT,
                centro TEXT,
                nivel_formacion TEXT DEFAULT 'Técnico'
            )
        ''')
        conexion.commit()
        print("✅ Base de datos creada correctamente")
        
        # ✅ AGREGAR COLUMNAS NUEVAS SI NO EXISTEN (para bases de datos existentes)
        agregar_columnas_sena(cursor)
        conexion.commit()
        
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")
    finally:
        conexion.close()

def agregar_columnas_sena(cursor):
    """Agrega las nuevas columnas SENA si no existen"""
    nuevas_columnas = [
        'nis TEXT',
        'primer_apellido TEXT',
        'segundo_apellido TEXT',
        'nombre_programa TEXT',
        'codigo_ficha TEXT',
        'centro TEXT',
        'nivel_formacion TEXT DEFAULT "Técnico"'  # 🆕 NUEVA COLUMNA
    ]
    
    for columna in nuevas_columnas:
        try:
            cursor.execute(f'ALTER TABLE empleados ADD COLUMN {columna}')
            print(f"✅ Columna agregada: {columna}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"⚠️ Columna ya existe: {columna.split()[0]}")
            else:
                print(f"❌ Error agregando columna {columna}: {e}")

def insertar_empleado(datos):
    """Inserta un empleado con todos los campos SENA"""
    if existe_cedula(datos['cedula']):
        raise ValueError("La cédula ya está registrada.")

    if existe_codigo(datos['codigo']):
        raise ValueError("El código ya está registrado.")

    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        
        # ✅ INSERT ACTUALIZADO CON TODOS LOS CAMPOS SENA + nivel_formacion
        cursor.execute('''
            INSERT INTO empleados (
                nombre, cedula, tipo_documento, cargo,
                codigo, fecha_emision, fecha_vencimiento,
                tipo_sangre, foto, nis, primer_apellido,
                segundo_apellido, nombre_programa, codigo_ficha, centro, nivel_formacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datos['nombre'],
            datos['cedula'],
            datos['tipo_documento'],
            datos['cargo'],
            datos['codigo'],
            datos['fecha_emision'],
            datos['fecha_vencimiento'],
            datos['tipo_sangre'],
            datos['foto'],
            datos.get('nis', ''),
            datos.get('primer_apellido', ''),
            datos.get('segundo_apellido', ''),
            datos.get('nombre_programa', ''),
            datos.get('codigo_ficha', ''),
            datos.get('centro', 'Centro de Biotecnología Industrial'),
            datos.get('nivel_formacion', 'Técnico')  # 🆕 NUEVO CAMPO
        ))
        conexion.commit()
        print(f"✅ Empleado {datos['nombre']} insertado correctamente - Nivel: {datos.get('nivel_formacion', 'Técnico')}")
        
    except Exception as e:
        print(f"❌ Error insertando empleado: {e}")
        raise e
    finally:
        conexion.close()

def cargar_empleado(cedula):
    """Carga un empleado por cédula con todos los campos"""
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM empleados WHERE cedula = ?', (cedula,))
        fila = cursor.fetchone()
        if fila:
            # ✅ COLUMNAS ACTUALIZADAS CON CAMPOS SENA + nivel_formacion
            columnas = [
                'id', 'nombre', 'cedula', 'tipo_documento', 'cargo',
                'codigo', 'fecha_emision', 'fecha_vencimiento',
                'tipo_sangre', 'foto', 'nis', 'primer_apellido',
                'segundo_apellido', 'nombre_programa', 'codigo_ficha', 'centro', 'nivel_formacion'
            ]
            empleado = dict(zip(columnas, fila))
            # Asegurar que nivel_formacion tenga un valor por defecto
            if not empleado.get('nivel_formacion'):
                empleado['nivel_formacion'] = 'Técnico'
            return empleado
        return None
    except Exception as e:
        print(f"❌ Error cargando empleado: {e}")
        return None
    finally:
        conexion.close()

def obtener_todos_empleados():
    """Obtiene todos los empleados de la base de datos"""
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM empleados ORDER BY fecha_emision DESC')
        filas = cursor.fetchall()
        
        empleados = []
        if filas:
            columnas = [
                'id', 'nombre', 'cedula', 'tipo_documento', 'cargo',
                'codigo', 'fecha_emision', 'fecha_vencimiento',
                'tipo_sangre', 'foto', 'nis', 'primer_apellido',
                'segundo_apellido', 'nombre_programa', 'codigo_ficha', 'centro', 'nivel_formacion'
            ]
            for fila in filas:
                empleado = dict(zip(columnas, fila))
                # Asegurar que nivel_formacion tenga un valor por defecto
                if not empleado.get('nivel_formacion'):
                    empleado['nivel_formacion'] = 'Técnico'
                empleados.append(empleado)
        
        return empleados
        
    except Exception as e:
        print(f"❌ Error obteniendo empleados: {e}")
        return []
    finally:
        conexion.close()

def existe_codigo(codigo):
    """Verifica si un código ya existe"""
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        cursor.execute('SELECT 1 FROM empleados WHERE codigo = ?', (codigo,))
        resultado = cursor.fetchone()
        return resultado is not None
    except Exception as e:
        print(f"❌ Error verificando código: {e}")
        return False
    finally:
        conexion.close()

def existe_cedula(cedula):
    """Verifica si una cédula ya existe"""
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        cursor.execute('SELECT 1 FROM empleados WHERE cedula = ?', (cedula,))
        resultado = cursor.fetchone()
        return resultado is not None
    except Exception as e:
        print(f"❌ Error verificando cédula: {e}")
        return False
    finally:
        conexion.close()

def actualizar_empleado(cedula, datos):
    """Actualiza los datos de un empleado existente"""
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        
        cursor.execute('''
            UPDATE empleados SET
                nombre = ?, tipo_documento = ?, cargo = ?,
                fecha_vencimiento = ?, tipo_sangre = ?, foto = ?,
                nis = ?, primer_apellido = ?, segundo_apellido = ?,
                nombre_programa = ?, codigo_ficha = ?, centro = ?, nivel_formacion = ?
            WHERE cedula = ?
        ''', (
            datos['nombre'],
            datos['tipo_documento'],
            datos['cargo'],
            datos['fecha_vencimiento'],
            datos['tipo_sangre'],
            datos['foto'],
            datos.get('nis', ''),
            datos.get('primer_apellido', ''),
            datos.get('segundo_apellido', ''),
            datos.get('nombre_programa', ''),
            datos.get('codigo_ficha', ''),
            datos.get('centro', ''),
            datos.get('nivel_formacion', 'Técnico'),  # 🆕 NUEVO CAMPO
            cedula
        ))
        conexion.commit()
        print(f"✅ Empleado con cédula {cedula} actualizado")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando empleado: {e}")
        return False
    finally:
        conexion.close()

def eliminar_empleado(cedula):
    """Elimina un empleado por cédula"""
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        cursor.execute('DELETE FROM empleados WHERE cedula = ?', (cedula,))
        conexion.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Empleado con cédula {cedula} eliminado")
            return True
        else:
            print(f"⚠️ No se encontró empleado con cédula {cedula}")
            return False
            
    except Exception as e:
        print(f"❌ Error eliminando empleado: {e}")
        return False
    finally:
        conexion.close()

def obtener_estadisticas():
    """Obtiene estadísticas básicas de la base de datos"""
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        
        # Total empleados
        cursor.execute('SELECT COUNT(*) FROM empleados')
        total = cursor.fetchone()[0]
        
        # Empleados por cargo
        cursor.execute('SELECT cargo, COUNT(*) FROM empleados GROUP BY cargo')
        por_cargo = dict(cursor.fetchall())
        
        # 🆕 Empleados por nivel de formación
        cursor.execute('SELECT nivel_formacion, COUNT(*) FROM empleados GROUP BY nivel_formacion')
        por_nivel = dict(cursor.fetchall())
        
        # Empleados registrados hoy
        from datetime import date
        hoy = date.today().strftime("%Y-%m-%d")
        cursor.execute('SELECT COUNT(*) FROM empleados WHERE fecha_emision = ?', (hoy,))
        hoy_count = cursor.fetchone()[0]
        
        return {
            'total': total,
            'por_cargo': por_cargo,
            'por_nivel_formacion': por_nivel,  # 🆕 NUEVA ESTADÍSTICA
            'registrados_hoy': hoy_count
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return {'total': 0, 'por_cargo': {}, 'por_nivel_formacion': {}, 'registrados_hoy': 0}
    finally:
        conexion.close()

# ================================================
# 🆕🆕🆕 NUEVAS FUNCIONES PARA GESTIÓN DE FOTOS 🆕🆕🆕
# ================================================

def buscar_empleado_completo(cedula):
    """
    Busca un empleado por cédula con todos los campos del SENA
    Función mejorada para la gestión de fotos
    """
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        
        # Buscar con todos los campos SENA (INCLUYENDO nivel_formacion)
        cursor.execute("""
            SELECT nombre, cedula, tipo_documento, cargo, codigo, 
                   fecha_emision, fecha_vencimiento, tipo_sangre, foto,
                   nis, primer_apellido, segundo_apellido, 
                   nombre_programa, codigo_ficha, centro, nivel_formacion
            FROM empleados 
            WHERE cedula = ? 
            ORDER BY fecha_emision DESC
            LIMIT 1
        """, (cedula,))
        
        row = cursor.fetchone()
        
        if row:
            empleado = {
                'nombre': row[0],
                'cedula': row[1],
                'tipo_documento': row[2] or 'CC',
                'cargo': row[3] or 'APRENDIZ',
                'codigo': row[4],
                'fecha_emision': row[5],
                'fecha_vencimiento': row[6],
                'tipo_sangre': row[7] or 'O+',
                'foto': row[8],
                # Campos adicionales del SENA
                'nis': row[9] or 'N/A',
                'primer_apellido': row[10] or '',
                'segundo_apellido': row[11] or '',
                'nombre_programa': row[12] or 'Programa Técnico',
                'codigo_ficha': row[13] or 'N/A',
                'centro': row[14] or 'Centro de Biotecnología Industrial',
                'nivel_formacion': row[15] or 'Técnico'  # 🆕 NUEVO CAMPO
            }
            
            print(f"✅ Empleado encontrado con datos SENA: {empleado['nombre']}")
            print(f"📋 NIS: {empleado['nis']} | Programa: {empleado['nombre_programa']} | Nivel: {empleado['nivel_formacion']}")
            
            return empleado
        else:
            print(f"❌ No se encontró empleado con cédula: {cedula}")
            return None
            
    except Exception as e:
        print(f"❌ Error buscando empleado: {e}")
        return None
    finally:
        conexion.close()

def obtener_empleados_con_filtros(buscar='', filtro_foto=''):
    """
    Obtiene empleados con filtros de búsqueda y estado de foto
    Para la funcionalidad de gestión de fotos del admin
    """
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        
        # Construir query base
        query = """
            SELECT rowid, nombre, cedula, tipo_documento, cargo, codigo, 
                   fecha_emision, fecha_vencimiento, tipo_sangre, foto,
                   nis, primer_apellido, segundo_apellido, 
                   nombre_programa, codigo_ficha, centro, nivel_formacion
            FROM empleados 
            WHERE 1=1
        """
        params = []
        
        # Aplicar filtros
        if buscar:
            query += " AND (nombre LIKE ? OR cedula LIKE ? OR codigo LIKE ?)"
            buscar_param = f"%{buscar}%"
            params.extend([buscar_param, buscar_param, buscar_param])
        
        if filtro_foto == 'con_foto':
            query += " AND foto IS NOT NULL AND foto != ''"
        elif filtro_foto == 'sin_foto':
            query += " AND (foto IS NULL OR foto = '')"
        
        query += " ORDER BY fecha_emision DESC"
        
        cursor.execute(query, params)
        empleados = []
        
        for row in cursor.fetchall():
            empleado = {
                'id': row[0],
                'nombre': row[1],
                'cedula': row[2],
                'tipo_documento': row[3] or 'CC',
                'cargo': row[4] or 'APRENDIZ',
                'codigo': row[5],
                'fecha_emision': row[6],
                'fecha_vencimiento': row[7],
                'tipo_sangre': row[8] or 'O+',
                'foto': row[9],
                'nis': row[10] or 'N/A',
                'primer_apellido': row[11] or '',
                'segundo_apellido': row[12] or '',
                'nombre_programa': row[13] or 'Programa General',
                'codigo_ficha': row[14] or 'Sin Ficha',
                'centro': row[15] or 'Centro de Biotecnología Industrial',
                'nivel_formacion': row[16] or 'Técnico'
            }
            
            # Verificar si la foto realmente existe en el sistema de archivos
            if empleado['foto']:
                ruta_foto = os.path.join('static/fotos', empleado['foto'])
                empleado['foto_existe'] = os.path.exists(ruta_foto)
            else:
                empleado['foto_existe'] = False
            
            empleados.append(empleado)
        
        return empleados
        
    except Exception as e:
        print(f"❌ Error obteniendo empleados con filtros: {e}")
        return []
    finally:
        conexion.close()

def eliminar_foto_empleado(cedula):
    """
    Elimina la foto de un empleado (solo el campo en la BD)
    El archivo físico se elimina desde app.py
    """
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        
        # Obtener info del empleado antes de eliminar
        cursor.execute("SELECT foto, nombre FROM empleados WHERE cedula = ?", (cedula,))
        resultado = cursor.fetchone()
        
        if not resultado:
            print(f"❌ No se encontró empleado con cédula {cedula}")
            return False, f"No se encontró empleado con cédula {cedula}"
        
        foto_actual, nombre_empleado = resultado
        
        # Actualizar base de datos - quitar la foto
        cursor.execute("UPDATE empleados SET foto = NULL WHERE cedula = ?", (cedula,))
        conexion.commit()
        
        print(f"✅ Foto eliminada de BD para {nombre_empleado} (Cédula: {cedula})")
        return True, foto_actual
        
    except Exception as e:
        print(f"❌ Error eliminando foto de BD: {e}")
        return False, str(e)
    finally:
        conexion.close()

def obtener_estadisticas_fotos():
    """
    Obtiene estadísticas específicas sobre fotos de empleados
    """
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        
        # Total empleados
        cursor.execute('SELECT COUNT(*) FROM empleados')
        total = cursor.fetchone()[0]
        
        # Empleados con foto (en BD)
        cursor.execute("SELECT COUNT(*) FROM empleados WHERE foto IS NOT NULL AND foto != ''")
        con_foto_bd = cursor.fetchone()[0]
        
        # Empleados sin foto
        sin_foto = total - con_foto_bd
        
        # Verificar fotos físicas existentes
        cursor.execute("SELECT foto FROM empleados WHERE foto IS NOT NULL AND foto != ''")
        fotos_bd = cursor.fetchall()
        
        fotos_fisicas = 0
        for (foto,) in fotos_bd:
            if foto and os.path.exists(os.path.join('static/fotos', foto)):
                fotos_fisicas += 1
        
        # Fotos huérfanas (en BD pero archivo no existe)
        fotos_huerfanas = con_foto_bd - fotos_fisicas
        
        return {
            'total_empleados': total,
            'con_foto_bd': con_foto_bd,
            'sin_foto': sin_foto,
            'fotos_fisicas': fotos_fisicas,
            'fotos_huerfanas': fotos_huerfanas
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas de fotos: {e}")
        return {
            'total_empleados': 0,
            'con_foto_bd': 0,
            'sin_foto': 0,
            'fotos_fisicas': 0,
            'fotos_huerfanas': 0
        }
    finally:
        conexion.close()

# ✅ FUNCIÓN PARA MIGRAR DATOS EXISTENTES (OPCIONAL)
def migrar_base_datos():
    """
    Función para migrar una base de datos antigua a la nueva estructura
    Solo ejecutar si tienes datos importantes que no quieres perder
    """
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        
        # Verificar si existe la tabla antigua
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='empleados'")
        if cursor.fetchone():
            print("🔄 Migrando base de datos existente...")
            agregar_columnas_sena(cursor)
            conexion.commit()
            print("✅ Migración completada")
        else:
            print("📋 Creando nueva base de datos...")
            crear_base_datos()
            
    except Exception as e:
        print(f"❌ Error en migración: {e}")
    finally:
        conexion.close()

# 🆕 NUEVA FUNCIÓN: Verificar estructura de la base de datos
def verificar_estructura_db():
    """
    Verifica que la base de datos tenga todos los campos necesarios
    """
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        
        cursor.execute("PRAGMA table_info(empleados)")
        columnas = cursor.fetchall()
        
        print("🔍 ESTRUCTURA ACTUAL DE LA BASE DE DATOS:")
        print("-" * 50)
        
        campos_esperados = [
            'id', 'nombre', 'cedula', 'tipo_documento', 'cargo', 'codigo',
            'fecha_emision', 'fecha_vencimiento', 'tipo_sangre', 'foto',
            'nis', 'primer_apellido', 'segundo_apellido', 'nombre_programa',
            'codigo_ficha', 'centro', 'nivel_formacion'
        ]
        
        campos_existentes = [col[1] for col in columnas]
        
        for campo in campos_esperados:
            if campo in campos_existentes:
                print(f"✅ {campo}")
            else:
                print(f"❌ {campo} - FALTA")
        
        # Verificar específicamente nivel_formacion
        if 'nivel_formacion' in campos_existentes:
            print("\n🎯 ¡Campo 'nivel_formacion' encontrado! La base de datos está lista.")
        else:
            print("\n⚠️ Falta el campo 'nivel_formacion'. Ejecutando actualización...")
            agregar_columnas_sena(cursor)
            conexion.commit()
            print("✅ Campo 'nivel_formacion' agregado exitosamente")
            
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
    finally:
        conexion.close()

# 🆕 NUEVA FUNCIÓN: Actualizar empleados existentes para que tengan nivel_formacion
def actualizar_empleados_sin_nivel():
    """
    Actualiza empleados existentes que no tienen nivel_formacion definido
    """
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        
        # Buscar empleados sin nivel_formacion o con valor NULL
        cursor.execute("SELECT cedula, nombre FROM empleados WHERE nivel_formacion IS NULL OR nivel_formacion = ''")
        empleados_sin_nivel = cursor.fetchall()
        
        if empleados_sin_nivel:
            print(f"🔄 Actualizando {len(empleados_sin_nivel)} empleados sin nivel de formación...")
            
            # Asignar 'Técnico' por defecto
            cursor.execute("UPDATE empleados SET nivel_formacion = 'Técnico' WHERE nivel_formacion IS NULL OR nivel_formacion = ''")
            conexion.commit()
            
            print("✅ Empleados actualizados con nivel 'Técnico' por defecto")
            
            for cedula, nombre in empleados_sin_nivel:
                print(f"   - {nombre} (Cédula: {cedula})")
        else:
            print("✅ Todos los empleados ya tienen nivel de formación definido")
            
    except Exception as e:
        print(f"❌ Error actualizando empleados: {e}")
    finally:
        conexion.close()

# ✅ EJECUTAR VERIFICACIÓN Y ACTUALIZACIÓN AL IMPORTAR
if __name__ == "__main__":
    print("🚀 INICIALIZANDO BASE DE DATOS...")
    crear_base_datos()
    verificar_estructura_db()
    actualizar_empleados_sin_nivel()
    print("✅ Base de datos inicializada correctamente con nivel_formacion")
else:
    # Cuando se importe desde app.py, verificar silenciosamente
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=5)
        cursor = conexion.cursor()
        cursor.execute("PRAGMA table_info(empleados)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if 'nivel_formacion' not in columnas:
            print("🔄 Agregando campo nivel_formacion...")
            agregar_columnas_sena(cursor)
            conexion.commit()
            print("✅ Campo nivel_formacion agregado")
        
        conexion.close()
    except:
        pass  # Silenciosamente continuar si hay problemas

def actualizar_base_datos_completa():
    """
    Actualiza la base de datos para asegurar que tenga todas las columnas necesarias
    EJECUTAR SOLO UNA VEZ al iniciar la aplicación
    """
    try:
        conn = sqlite3.connect('carnet.db')
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='empleados'")
        if not cursor.fetchone():
            print("Creando tabla empleados...")
            # Crear tabla completa desde el inicio
            cursor.execute("""
                CREATE TABLE empleados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    cedula TEXT UNIQUE NOT NULL,
                    tipo_documento TEXT DEFAULT 'CC',
                    cargo TEXT DEFAULT 'APRENDIZ',
                    codigo TEXT UNIQUE,
                    fecha_emision TEXT,
                    fecha_vencimiento TEXT,
                    tipo_sangre TEXT,
                    foto TEXT,
                    nis TEXT,
                    primer_apellido TEXT,
                    segundo_apellido TEXT,
                    nombre_programa TEXT,
                    codigo_ficha TEXT,
                    centro TEXT,
                    nivel_formacion TEXT DEFAULT 'Técnico',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Tabla empleados creada exitosamente")
        else:
            print("Tabla empleados existe, verificando columnas...")
            
            # Obtener columnas existentes
            cursor.execute("PRAGMA table_info(empleados)")
            columnas_existentes = [col[1] for col in cursor.fetchall()]
            print(f"Columnas existentes: {columnas_existentes}")
            
            # Columnas que deben existir
            columnas_necesarias = {
                'nis': 'TEXT',
                'primer_apellido': 'TEXT',
                'segundo_apellido': 'TEXT',
                'nombre_programa': 'TEXT',
                'codigo_ficha': 'TEXT',
                'centro': 'TEXT',
                'nivel_formacion': 'TEXT DEFAULT "Técnico"',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            }
            
            # Agregar columnas faltantes
            for columna, tipo in columnas_necesarias.items():
                if columna not in columnas_existentes:
                    try:
                        cursor.execute(f'ALTER TABLE empleados ADD COLUMN {columna} {tipo}')
                        print(f"✅ Columna agregada: {columna}")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e):
                            print(f"⚠️ Columna ya existe: {columna}")
                        else:
                            print(f"❌ Error agregando columna {columna}: {e}")
        
        # Crear índices para mejorar rendimiento
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_cedula ON empleados(cedula)",
            "CREATE INDEX IF NOT EXISTS idx_codigo ON empleados(codigo)",
            "CREATE INDEX IF NOT EXISTS idx_nombre_programa ON empleados(nombre_programa)",
            "CREATE INDEX IF NOT EXISTS idx_codigo_ficha ON empleados(codigo_ficha)",
            "CREATE INDEX IF NOT EXISTS idx_fecha_emision ON empleados(fecha_emision)"
        ]
        
        for indice in indices:
            cursor.execute(indice)
            print(f"✅ Índice creado: {indice.split('idx_')[1].split(' ')[0] if 'idx_' in indice else 'índice'}")
        
        conn.commit()
        conn.close()
        print("🎉 Base de datos actualizada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando base de datos: {e}")
        return False

# FUNCIÓN PARA VERIFICAR LA INTEGRIDAD DE LOS DATOS
def verificar_datos_empleados():
    """Verifica que los datos se estén guardando correctamente"""
    try:
        conn = sqlite3.connect('carnet.db')
        cursor = conn.cursor()
        
        # Contar total de empleados
        cursor.execute("SELECT COUNT(*) FROM empleados")
        total = cursor.fetchone()[0]
        print(f"Total de empleados en BD: {total}")
        
        # Contar por nivel de formación
        cursor.execute("SELECT nivel_formacion, COUNT(*) FROM empleados GROUP BY nivel_formacion")
        niveles = cursor.fetchall()
        print("Empleados por nivel de formación:")
        for nivel, count in niveles:
            print(f"  {nivel or 'Sin especificar'}: {count}")
        
        # Contar con y sin foto
        cursor.execute("SELECT COUNT(*) FROM empleados WHERE foto IS NOT NULL AND foto != ''")
        con_foto = cursor.fetchone()[0]
        sin_foto = total - con_foto
        print(f"Con foto: {con_foto}, Sin foto: {sin_foto}")
        
        # Últimos 5 registros
        cursor.execute("""
            SELECT nombre, cedula, nombre_programa, nivel_formacion, fecha_emision 
            FROM empleados 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        ultimos = cursor.fetchall()
        print("\nÚltimos 5 registros:")
        for emp in ultimos:
            print(f"  {emp[0]} - {emp[1]} - {emp[2]} - {emp[3]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error verificando datos: {e}")
        return False

# FUNCIÓN PARA LIMPIAR DATOS DUPLICADOS O INCORRECTOS
def limpiar_datos_empleados():
    """Limpia datos duplicados o incorrectos"""
    try:
        conn = sqlite3.connect('carnet.db')
        cursor = conn.cursor()
        
        # Eliminar registros de ejemplo
        cursor.execute("""
            DELETE FROM empleados 
            WHERE cedula LIKE '%ejemplo%' 
               OR cedula LIKE '%12345678%'
               OR nombre LIKE '%ejemplo%'
               OR nombre LIKE '%JUAN CARLOS%'
        """)
        eliminados = cursor.rowcount
        if eliminados > 0:
            print(f"✅ Eliminados {eliminados} registros de ejemplo")
        
        # Actualizar registros sin nivel de formación
        cursor.execute("""
            UPDATE empleados 
            SET nivel_formacion = 'Técnico' 
            WHERE nivel_formacion IS NULL OR nivel_formacion = ''
        """)
        actualizados = cursor.rowcount
        if actualizados > 0:
            print(f"✅ Actualizados {actualizados} registros sin nivel de formación")
        
        # Actualizar registros sin centro
        cursor.execute("""
            UPDATE empleados 
            SET centro = 'Centro de Biotecnología Industrial' 
            WHERE centro IS NULL OR centro = ''
        """)
        actualizados_centro = cursor.rowcount
        if actualizados_centro > 0:
            print(f"✅ Actualizados {actualizados_centro} registros sin centro")
        
        conn.commit()
        conn.close()
        print("🧹 Limpieza de datos completada")
        return True
        
    except Exception as e:
        print(f"Error limpiando datos: {e}")
        return False

# EJECUTAR AL INICIAR LA APLICACIÓN
if __name__ == "__main__":
    print("🚀 Iniciando actualización de base de datos...")
    
    # Actualizar estructura
    if actualizar_base_datos_completa():
        print("✅ Estructura de BD actualizada")
    
    # Limpiar datos incorrectos
    if limpiar_datos_empleados():
        print("✅ Datos limpiados")
    
    # Verificar estado final
    verificar_datos_empleados()
    
    print("🎉 Proceso completado!")

# LLAMAR ESTA FUNCIÓN AL FINAL DE TU app.py, ANTES DEL if __name__ == "__main__":
actualizar_base_datos_completa()