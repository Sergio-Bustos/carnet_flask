import qrcode
import os

def generar_qr(cedula):
    enlace = "https://oferta.senasofiaplus.edu.co/sofia-oferta/inicio-sofia-plus.html"
    nombre_archivo = f"{cedula}.png"
    ruta = os.path.join("static", "qr", nombre_archivo)

    # Eliminar QR viejo si existe
    if os.path.exists(ruta):
        os.remove(ruta)

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(enlace)
    qr.make(fit=True)

    imagen = qr.make_image(fill="black", back_color="white")
    imagen.save(ruta)
    return ruta