from PIL import Image
import numpy as np
import os
import cv2


# ═══════════════════════════════════════════════════════════
# DETECCION DE FONDO BLANCO
# Si el 70%+ de los pixeles del borde son blancos (R,G,B >= 200)
# la foto se guarda TAL CUAL sin ningún procesamiento.
# Solo se recorta al tamaño 3x4. Nada más.
# ═══════════════════════════════════════════════════════════
UMBRAL_BLANCO           = 200   # canal mínimo para ser "blanco"
PORCENTAJE_BORDE_BLANCO = 0.70  # 70% del borde debe ser blanco


def fondo_es_blanco(imagen_rgb):
    arr = np.array(imagen_rgb)
    h, w = arr.shape[:2]
    grosor = max(15, int(min(h, w) * 0.06))

    bordes = np.concatenate([
        arr[0:grosor, :].reshape(-1, 3),
        arr[h-grosor:h, :].reshape(-1, 3),
        arr[:, 0:grosor].reshape(-1, 3),
        arr[:, w-grosor:w].reshape(-1, 3),
    ], axis=0)

    es_blanco = (
        (bordes[:, 0] >= UMBRAL_BLANCO) &
        (bordes[:, 1] >= UMBRAL_BLANCO) &
        (bordes[:, 2] >= UMBRAL_BLANCO)
    )

    proporcion = es_blanco.sum() / len(bordes)
    print(f"    Fondo: {proporcion*100:.1f}% blanco en bordes")
    return proporcion >= PORCENTAJE_BORDE_BLANCO


def procesar_foto_carnet(ruta_imagen, ruta_salida, ancho_carnet=220, alto_carnet=270):
    """
    Si el fondo es blanco  → copia exacta del archivo original. CERO procesamiento.
    Si el fondo no es blanco → eliminar fondo con IA, limpiar, recortar.
    """
    try:
        import shutil

        print(f"[1] Abriendo: {ruta_imagen}")
        imagen = Image.open(ruta_imagen).convert('RGB')

        print("[2] Verificando fondo...")
        if fondo_es_blanco(imagen):
            # ══ FONDO BLANCO: copia binaria exacta del archivo, sin tocar nada ══
            print("    [FONDO BLANCO] Copiando archivo original sin ninguna modificacion")
            shutil.copy2(ruta_imagen, ruta_salida)
            print(f"[OK] Guardado: {ruta_salida}")
            return True

        # ══ FONDO NO BLANCO: procesar con IA ══
        print("[3] Fondo no blanco — eliminando con IA...")
        resultado = eliminar_solo_fondo(imagen)

        print("[4] Limpiando residuos en bordes...")
        resultado = limpiar_residuos_fondo(resultado)

        print("[5] Ajustando tamano 3x4...")
        final = redimensionar_para_carnet(resultado, ancho_carnet, alto_carnet)
        final.save(ruta_salida, 'PNG', quality=100)
        print(f"[OK] Guardado: {ruta_salida}")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def eliminar_solo_fondo(imagen):
    """Elimina fondo usando IA especializada en personas"""
    try:
        from rembg import remove, new_session
        import io

        print("    Cargando modelo u2net_human_seg...")
        session = new_session("u2net_human_seg")

        buffer = io.BytesIO()
        imagen.save(buffer, format='PNG')
        buffer.seek(0)

        output_bytes = remove(
            buffer.read(),
            session=session,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10,
            bgcolor=(255, 255, 255, 255)
        )

        resultado = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
        fondo = Image.new("RGBA", resultado.size, (255, 255, 255, 255))
        fondo.paste(resultado, (0, 0), resultado)

        print("    Fondo eliminado — persona intacta")
        return fondo.convert("RGB")

    except ImportError:
        print("    rembg no instalado, usando OpenCV")
        return eliminar_fondo_simple(imagen)
    except Exception as e:
        print(f"    Error rembg: {e}, usando OpenCV")
        return eliminar_fondo_simple(imagen)


def limpiar_residuos_fondo(imagen):
    """Limpia manchas que rembg deja en los bordes exteriores"""
    try:
        img_np  = np.array(imagen.convert("RGB"))
        h, w    = img_np.shape[:2]
        img_hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

        margen_x = int(w * 0.18)
        margen_y = int(h * 0.12)

        mask_borde = np.zeros((h, w), np.uint8)
        mask_borde[:margen_y, :]   = 255
        mask_borde[h-margen_y:, :] = 255
        mask_borde[:, :margen_x]   = 255
        mask_borde[:, w-margen_x:] = 255

        mask_blanco = cv2.inRange(img_hsv,
                                  np.array([0,   0, 210]),
                                  np.array([180, 25, 255]))

        mask_oscuro = (img_np.mean(axis=2) < 60).astype(np.uint8) * 255
        ko = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_oscuro = cv2.dilate(mask_oscuro, ko, iterations=1)

        mask_no_blanco  = cv2.bitwise_not(mask_blanco)
        mask_no_oscuro  = cv2.bitwise_not(mask_oscuro)
        mask_candidatos = cv2.bitwise_and(mask_no_blanco, mask_no_oscuro)
        mask_residuo    = cv2.bitwise_and(mask_candidatos, mask_borde)

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            mask_residuo, connectivity=8)

        mask_final = np.zeros((h, w), np.uint8)
        umbral_max = int(w * h * 0.005)

        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] <= umbral_max:
                mask_final[labels == i] = 255

        if mask_final.sum() == 0:
            print("    Sin residuos detectados")
            return imagen

        mask_s = cv2.GaussianBlur(mask_final.astype(np.float32), (3, 3), 0)
        res    = img_np.copy().astype(np.float32)
        alpha  = mask_s / 255.0
        for c in range(3):
            res[:, :, c] = img_np[:, :, c] * (1 - alpha) + 255.0 * alpha

        n = (mask_final > 0).sum()
        print(f"    Residuos eliminados: {n} pixeles")
        return Image.fromarray(res.astype(np.uint8))

    except Exception as e:
        print(f"    limpiar_residuos error ({e}) — se omite")
        return imagen


def eliminar_fondo_simple(imagen):
    """Metodo alternativo sin rembg — usa OpenCV"""
    try:
        img_array = np.array(imagen)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        h, w = img_bgr.shape[:2]

        b = 40
        muestras = []
        muestras.extend(img_bgr[0:b, :].reshape(-1, 3))
        muestras.extend(img_bgr[h-b:h, :].reshape(-1, 3))
        muestras.extend(img_bgr[:, 0:b].reshape(-1, 3))
        muestras.extend(img_bgr[:, w-b:w].reshape(-1, 3))

        color = np.median(muestras, axis=0).astype(int)
        tol   = 50
        lower = np.clip(color - tol, 0, 255).astype(np.uint8)
        upper = np.clip(color + tol, 0, 255).astype(np.uint8)
        mask_fondo   = cv2.inRange(img_bgr, lower, upper)
        mask_persona = cv2.bitwise_not(mask_fondo)

        kernel = np.ones((5, 5), np.uint8)
        mask_persona = cv2.morphologyEx(mask_persona, cv2.MORPH_CLOSE, kernel)
        mask_persona = cv2.GaussianBlur(mask_persona, (5, 5), 0)

        resultado = np.ones_like(img_bgr) * 255
        mask_3d   = cv2.cvtColor(mask_persona, cv2.COLOR_GRAY2BGR) / 255.0
        resultado = (img_bgr * mask_3d + resultado * (1 - mask_3d)).astype(np.uint8)

        return Image.fromarray(cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB))

    except Exception as e:
        print(f"    Error OpenCV: {e} — imagen original")
        return imagen


def redimensionar_para_carnet(imagen, ancho, alto):
    """Recorta y redimensiona a proporcion 3x4 exacta"""
    w, h = imagen.size
    ratio_objetivo = ancho / alto
    ratio_actual   = w / h

    if ratio_actual > ratio_objetivo:
        nuevo_w = int(h * ratio_objetivo)
        left    = (w - nuevo_w) // 2
        imagen  = imagen.crop((left, 0, left + nuevo_w, h))
    else:
        nuevo_h = int(w / ratio_objetivo)
        imagen  = imagen.crop((0, 0, w, nuevo_h))

    return imagen.resize((ancho, alto), Image.Resampling.LANCZOS)


def validar_imagen(ruta):
    try:
        with Image.open(ruta) as img:
            img.verify()
        img = Image.open(ruta)
        if img.size[0] < 200 or img.size[1] < 200:
            return False, "Imagen muy pequena (minimo 200x200px)"
        if os.path.getsize(ruta) > 10485760:
            return False, "Imagen muy grande (maximo 10MB)"
        return True, "OK"
    except:
        return False, "Archivo de imagen invalido"


def verificar_si_foto_existe(cedula, carpeta="static/fotos"):
    for nombre in [
        f"foto_{cedula}.png",
        f"foto_{cedula}.jpg",
        f"{cedula}.png",
        f"{cedula}.jpg"
    ]:
        ruta = os.path.join(carpeta, nombre)
        if os.path.exists(ruta):
            return True, ruta
    return False, None


def procesar_foto_aprendiz(archivo_foto, cedula, carpeta_fotos="static/fotos"):
    try:
        print("\n" + "="*70)
        print(f"PROCESANDO FOTO — Cedula: {cedula}")
        print("="*70)

        existe, ruta_vieja = verificar_si_foto_existe(cedula, carpeta_fotos)
        if existe and ruta_vieja:
            os.remove(ruta_vieja)
            print(f"[OK] Foto anterior eliminada: {ruta_vieja}")

        os.makedirs(carpeta_fotos, exist_ok=True)

        ext = os.path.splitext(archivo_foto.filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            return False, None, "Formato invalido. Use JPG o PNG"

        temp       = f"temp_{cedula}{ext}"
        final      = f"foto_{cedula}.png"
        ruta_temp  = os.path.join(carpeta_fotos, temp)
        ruta_final = os.path.join(carpeta_fotos, final)

        archivo_foto.save(ruta_temp)

        valida, msg = validar_imagen(ruta_temp)
        if not valida:
            os.remove(ruta_temp)
            return False, None, msg

        exito = procesar_foto_carnet(ruta_temp, ruta_final, 220, 270)

        if os.path.exists(ruta_temp):
            os.remove(ruta_temp)

        if exito:
            print(f"[OK] Foto final guardada: {ruta_final}")
            print("="*70 + "\n")
            return True, final, "Foto procesada correctamente con IA"
        else:
            return False, None, "Error al procesar la imagen"

    except Exception as e:
        print(f"[ERROR GENERAL] {e}")
        if 'ruta_temp' in locals() and os.path.exists(ruta_temp):
            os.remove(ruta_temp)
        return False, None, str(e)


if __name__ == "__main__":
    print("PROCESADOR SENA")
    print("- Fondo BLANCO  -> solo recorta 3x4, NO toca la foto")
    print("- Fondo otro color -> elimina con IA + limpia residuos")