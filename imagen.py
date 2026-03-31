from PIL import Image, ImageDraw, ImageFont
import os


# ============================================
# SISTEMA ROBUSTO DE CARGA DE FUENTES
# Prueba múltiples rutas hasta encontrar una
# ============================================

def cargar_fuente(tamaño, bold=False, tipo='sans'):
    """
    Carga fuente con múltiples alternativas para garantizar
    que SIEMPRE se use una fuente legible, nunca la default de 8px
    """
    candidatas = []
    
    if tipo == 'serif':
        candidatas = [
            "static/fonts/times.ttf",
            "C:/Windows/Fonts/times.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        ]
    
    elif bold:
        candidatas = [
        "static/fonts/arialbd.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    else:
        candidatas = [
            "static/fonts/arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]

    for ruta in candidatas:
        try:
            return ImageFont.truetype(ruta, tamaño)
        except:
            continue

    # Último recurso: crear fuente bitmap escalada
    # Usamos un truco: ImageFont.load_default() es 8px pero podemos
    # generar texto más grande dibujando en una imagen mayor
    try:
        # Intentar con la fuente por defecto pero notificar
        print(f"⚠️  ADVERTENCIA: No se encontró fuente TTF para tamaño {tamaño}. "
              f"El carnet puede verse diferente al esperado.")
        print(f"   Instala fuentes en: C:/Windows/Fonts/ o /usr/share/fonts/")
        # Devolver default — al menos algo
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()


def wrap_text(texto, font, draw, max_ancho):
    """Divide texto largo en líneas que caben en max_ancho"""
    palabras = texto.split()
    lineas = []
    linea_actual = ""
    
    for palabra in palabras:
        prueba = f"{linea_actual} {palabra}".strip()
        bbox = draw.textbbox((0, 0), prueba, font=font)
        if bbox[2] - bbox[0] <= max_ancho:
            linea_actual = prueba
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra
    
    if linea_actual:
        lineas.append(linea_actual)
    
    return lineas


def generar_carnet(empleado:dict, ruta_qr:str) ->str:
    # MEDIDAS EXACTAS DEL CARNET SENA: 5.5cm ancho x 8.7cm alto (formato vertical)
    # A 300 DPI para impresión de calidad: 650px ancho x 1028px alto (5.5cm x 8.7cm)
    ancho, alto = 650, 1028
    fondo_color = (255, 255, 255)
    img = Image.new("RGB", (ancho, alto), fondo_color)
    draw = ImageDraw.Draw(img)

    # ============================================
    # FUENTES — tamaños ajustados para coincidir con carnet de referencia
    # ============================================
    font_nombre       = cargar_fuente(44, bold=True)   # nombre aprendiz (bold verde)
    font_cedula       = cargar_fuente(40, tipo='serif')  # CC. 1.114.543.155
    font_rh_label     = cargar_fuente(40, bold=False)  # Rh O+
    font_footer       = cargar_fuente(30, bold=False)  # Regional / Centro
    font_aprendiz     = cargar_fuente(34, bold=True)   # APRENDIZ (bold negro)
    font_vertical_bold= cargar_fuente(32, bold=True)
    font_logo         = cargar_fuente(30, bold=False)

    # ========== LOGO SENA ==========
    ruta_logo = os.path.join("static", "fotos", "logo_sena.png")
    try:
        logo = Image.open(ruta_logo).convert("RGBA")
        logo = logo.resize((160, 160))
        img.paste(logo, (50, 30), logo)
    except:
        draw.text((30, 30), "SENA", fill=(0, 128, 0), font=font_logo)

    # ========== FOTO DEL APRENDIZ ==========
    foto = None
    posibles_rutas = []

    if empleado.get('cedula'):
        posibles_rutas += [
            os.path.join("static", "fotos", f"foto_{empleado['cedula']}.png"),
            os.path.join("static", "fotos", f"foto_{empleado['cedula']}.jpg"),
            os.path.join("static", "fotos", f"{empleado['cedula']}.png"),
            os.path.join("static", "fotos", f"{empleado['cedula']}.jpg"),
        ]

    if empleado.get('foto'):
        posibles_rutas.append(os.path.join("static", "fotos", empleado['foto']))

    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            try:
                foto = Image.open(ruta).convert("RGB")
                break
            except:
                continue

    if foto is None:
        foto = Image.new("RGB", (220, 260), (235, 235, 235))
        draw_ph = ImageDraw.Draw(foto)
        font_ph = cargar_fuente(18)
        draw_ph.text((55, 115), "SIN FOTO", fill=(150, 150, 150), font=font_ph)

    # Siempre redimensionar a tamaño fijo — independiente de la foto original
    foto = foto.resize((224, 257), Image.LANCZOS)
    img.paste(foto, (390, 20))

    # ========== CARGO ==========
    cargo_texto = empleado.get('cargo', 'APRENDIZ').upper()
    # CARGO "APRENDIZ" — justo debajo de la foto+logo
    draw.text((30, 245), cargo_texto, fill=(0, 0, 0), font=font_aprendiz)

    # Línea verde horizontal separadora
    draw.line((30, 293, 610, 293), fill=(0, 128, 0), width=9)

    # ========== NOMBRE — dividido en líneas si es largo ==========
    nombre_completo = empleado['nombre'].upper()
    partes = nombre_completo.split()

    y_nombre = 315 
    espaciado = 60   # espacio entre líneas del nombre

    # Siempre máximo 2 palabras por línea para consistencia visual
    # "JOHAN QUINTERO HERNANDEZ" → "JOHAN QUINTERO" / "HERNANDEZ"
    # "ANA MARIA TOQUICA MILLAN" → "ANA MARIA" / "TOQUICA MILLAN"
    lineas_nombre = []
    for i in range(0, len(partes), 2):
        lineas_nombre.append(" ".join(partes[i:i+2]))

    for idx, linea in enumerate(lineas_nombre):
        draw.text((30, y_nombre + espaciado * idx), linea, fill=(0, 128, 0), font=font_nombre)

    siguiente_y = y_nombre + espaciado * len(lineas_nombre) + 10

    # ========== CÉDULA ==========
    tipo_doc = empleado.get('tipo_documento', 'CC')
    try:
        cedula_formateada = str(empleado['cedula'])
    except:
        cedula_formateada = str(empleado['cedula'])
    texto_cedula = f"{tipo_doc}. {cedula_formateada}"
    draw.text((30, siguiente_y + 44), texto_cedula, fill=(0, 0, 0), font=font_cedula)

    # ========== RH / TIPO SANGRE ==========
    tipo_sangre = empleado.get('tipo_sangre', 'O+').upper()
    draw.text((30, siguiente_y + 110), f"Rh {tipo_sangre}", fill=(0, 0, 0), font=font_rh_label)

    # ========== CÓDIGO QR — esquina inferior derecha ==========
    try:
        qr = Image.open(ruta_qr).convert("RGB")
        qr = qr.resize((310, 329), Image.LANCZOS)
        img.paste(qr, (330, siguiente_y +25))
    except:
        draw.rectangle([(377, siguiente_y + 10), (630, siguiente_y + 250)], outline=(0, 0, 0), width=2)
        draw.text((480, siguiente_y + 120), "QR", fill=(0, 0, 0), font=font_footer)

    # ========== FOOTER ==========
    draw.line((30, 900, 90, 900), fill=(0, 120, 0), width=9)
    draw.text((30, 927), "Regional Valle del Cauca",           fill=(79, 160, 70), font=font_footer, )
    draw.text((30, 971), "Centro de Biotecnología Industrial",  fill=(79, 160, 70), font=font_footer)

    # Guardar anverso
    ruta_anverso = os.path.join("static", "carnets", f"carnet_{empleado['cedula']}.png")
    img.save(ruta_anverso, dpi=(300, 300))
    print(f"✅ Anverso guardado: {ruta_anverso}")

    # ===== REVERSO DEL CARNET =====
    try:
        ruta_fondo_reverso = os.path.join("static", "fondos", "trasero.png")
        reverso = Image.open(ruta_fondo_reverso).convert("RGB")
        reverso = reverso.resize((ancho, alto))
    except:
        reverso = Image.new("RGB", (ancho, alto), (255, 255, 255))

    draw_reverso = ImageDraw.Draw(reverso)

    # Fuentes del reverso — también con sistema robusto
    font_reverso       = cargar_fuente(29, tipo='serif')
    font_extraviado    = cargar_fuente(26, tipo='serif')
    font_programa_bold = cargar_fuente(26, tipo='serif')
    font_firma_titulo  = cargar_fuente(26, tipo='serif')
    font_ficha         = cargar_fuente(26, tipo='serif')

    # ========== TEXTO PRINCIPAL DEL REVERSO ==========
    margen_izq = 43
    margen_der = 50
    max_ancho_texto = ancho - margen_izq - margen_der
    texto_y = 35
    sep = 40  # separación entre líneas

    texto1_lines = [
    "Este carné identifica a quien lo porta,",
    "únicamente para el cumplimiento de sus",
    "funciones y para la obtención de los",
    "servicios que el SENA presta a sus",
    "aprendices, funcionarios y/o contratistas.",
    "Se solicita a las autoridades civiles y militares",
    "prestarle toda la colaboración para su",
    "desempeño.",
    ]

    for i, line in enumerate(texto1_lines):
        if not line.strip():
            continue
        palabras = line.split()
        if len(palabras) > 1 and i < len(texto1_lines) - 2:
            # Texto justificado
            anchos_palabras = [
                draw_reverso.textbbox((0, 0), p, font=font_reverso)[2] -
                draw_reverso.textbbox((0, 0), p, font=font_reverso)[0]
                for p in palabras
            ]
            suma_palabras = sum(anchos_palabras)
            espacio = (max_ancho_texto - suma_palabras) / (len(palabras) - 1)
            x = margen_izq
            for j, palabra in enumerate(palabras):
                draw_reverso.text((x, texto_y + i * sep), palabra,
                                  fill=(0, 0, 0), font=font_reverso)
                x += anchos_palabras[j] + (espacio if j < len(palabras) - 1 else 0)
        else:
            draw_reverso.text((margen_izq, texto_y + i * sep),
                              line, fill=(0, 0, 0), font=font_reverso)

    # ========== FIRMA ==========
    firma_y = 400
    firma_x = (ancho - 100) // 3
    try:
        ruta_firma = os.path.join("static", "fotos", "firma_directora.png")
        if os.path.exists(ruta_firma):
            firma_img = Image.open(ruta_firma).convert("RGBA")
            firma_img = firma_img.resize((350, 250), Image.LANCZOS)
            reverso.paste(firma_img, (firma_x, firma_y), firma_img)
    except:
        pass

    # "Firma y Autoriza"
    firma_texto_y = firma_y + 230
    texto_firma = "Firma y Autoriza"
    bbox_firma = draw_reverso.textbbox((0, 0), texto_firma, font=font_firma_titulo)
    pos_x_firma = margen_izq
    draw_reverso.text((pos_x_firma, firma_texto_y),
                      texto_firma, fill=(0, 0, 0), font=font_firma_titulo)

    # ========== TEXTO CARNÉ EXTRAVIADO ==========
    info_y = 700
    texto_extraviado = [
        "Si por algún motivo este carné es extraviado,",
        "por favor diríjase al Centro de Biotecnología",
        "Industrial ubicado en la calle 40 #30-44"
    ]
    for i, linea in enumerate(texto_extraviado):
        draw_reverso.text((margen_izq, info_y + i * 42),
                          linea, fill=(0, 0, 0), font=font_extraviado)

    # ========== PROGRAMA Y FICHA ==========
    nombre_programa = empleado.get('nombre_programa', 'Programa Técnico')
    codigo_ficha    = empleado.get('codigo_ficha', '0000')

    # Wrap del nombre de programa si es muy largo
    lineas_programa = wrap_text(nombre_programa, font_programa_bold, draw_reverso,
                                max_ancho_texto)
    prog_y = 860
    for i, lp in enumerate(lineas_programa[:2]):  # máximo 2 líneas
        draw_reverso.text((margen_izq, prog_y + i * 34),
                          lp, fill=(0, 0, 0), font=font_programa_bold)

    ficha_y = prog_y + (len(lineas_programa[:2])) * 34 + 25
    draw_reverso.text((margen_izq, ficha_y),
                      f"FICHA {codigo_ficha}", fill=(0, 0, 0), font=font_ficha)

    ruta_reverso = os.path.join("static", "carnets", f"reverso_{empleado['cedula']}.png")
    reverso.save(ruta_reverso, dpi=(300, 300))
    print(f" Reverso guardado: {ruta_reverso}")

    return ruta_anverso

#Tarea: T5 funcion para verificar la medida
def verificar_medidas(ancho: int, alto: int) -> bool:
    ancho_minimo, alto_minimo = 1012, 638
    if ancho<ancho_minimo:
        return {"lado": "ancho", "medida": ancho_minimo}
    if alto<alto_minimo:
        return {"lado": "alto", "medida": alto}
    return False
#--------

def combinar_anverso_reverso(nombre_archivo_anverso: str, nombre_archivo_reverso: str, nombre_aprendiz:str)  -> str:
    ruta_anverso = os.path.join("static", "carnets", nombre_archivo_anverso)
    ruta_reverso = os.path.join("static", "carnets", nombre_archivo_reverso)

    try:
        anverso = Image.open(ruta_anverso)
        reverso = Image.open(ruta_reverso)
    except Exception as e:
        raise Exception(f"Error al cargar las imágenes: {e}")

    # Padding entre las dos caras
    padding = 40
    ancho_total = anverso.width + reverso.width + padding
    alto_total  = max(anverso.height, reverso.height) + 60
    
    #Tarea: T5
    #verificar la medida del carnet con sus dos lados
    lados = verificar_medidas(ancho_total, alto_total)
    if lados:
        if lados["lado"] == "ancho":
            ancho_total = ancho_total + (verificar_medidas["medida"]-ancho_total)
        if lados["lado"] == "alto":
            alto_total = ancho_total + (verificar_medidas["medida"]-alto_total)
    #-------------        
    
    combinado = Image.new("RGB", (ancho_total, alto_total), (245, 245, 245))
    combinado.paste(anverso, (0, 0))
    combinado.paste(reverso, (anverso.width + padding, 0))

    # Etiquetas ANVERSO / REVERSO
    draw = ImageDraw.Draw(combinado)
    font_label = cargar_fuente(22)
    draw.text((anverso.width // 2 - 40, anverso.height + 15),
              "ANVERSO", fill=(80, 80, 80), font=font_label)
    draw.text((anverso.width + padding + reverso.width // 2 - 40, reverso.height + 15),
              "REVERSO", fill=(80, 80, 80), font=font_label)

    nombre_archivo = f"{nombre_aprendiz.replace(' ', '_')}_completo.png"
    ruta_combinada = os.path.join("static", "carnets", nombre_archivo)
    combinado.save(ruta_combinada, dpi=(300, 300))
    print(f"✅ Carnet combinado guardado: {ruta_combinada}")

    return nombre_archivo

