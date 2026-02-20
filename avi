import cv2
import time
import os
from datetime import datetime

def safe_hasattr(module, name):
    try:
        getattr(module, name)
        return True
    except Exception:
        return False

def safe_set(cap, prop, value, nombre=""):
    try:
        ok = cap.set(prop, value)
        val = cap.get(prop) if ok else "N/A"
        print(f"{nombre or prop}: set={value} -> {'OK' if ok else 'FALLÓ'} (actual={val})")
        return ok
    except Exception as e:
        print(f"{nombre or prop}: EXCEPCIÓN al setear -> {e}")
        return False

def crear_escritor_video_avi(path_salida, ancho, alto, fps_deseado=30):
    """
    Crea un VideoWriter en formato AVI.
    Intento 1: MJPG (muy compatible, archivos grandes).
    Intento 2: XVID (más comprimido).
    """
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    ruta_avi = os.path.splitext(path_salida)[0] + ".avi"
    writer = cv2.VideoWriter(ruta_avi, fourcc, fps_deseado, (ancho, alto))
    if writer.isOpened():
        print(f"Grabando en: {ruta_avi} (AVI/MJPG) @ {fps_deseado} FPS, {ancho}x{alto}")
        return writer, ruta_avi

    # Fallback a XVID
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    writer = cv2.VideoWriter(ruta_avi, fourcc, fps_deseado, (ancho, alto))
    if writer.isOpened():
        print(f"Grabando en: {ruta_avi} (AVI/XVID) @ {fps_deseado} FPS, {ancho}x{alto}")
        return writer, ruta_avi

    return None, None

def configurar_camara_c920(id_camara=0, grabar_auto=False, carpeta_salida="grabaciones"):
    print(f"Intentando abrir cámara {id_camara} con DSHOW...")
    cap = cv2.VideoCapture(id_camara, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Fallo con DSHOW. Intentando con MSMF (Media Foundation)...")
        cap = cv2.VideoCapture(id_camara, cv2.CAP_MSMF)

    if not cap.isOpened():
        print(f"Error: No se pudo abrir la cámara {id_camara} con ningún backend.")
        return

    backend = getattr(cap, "getBackendName", lambda: "desconocido")()
    print(f"--- Configurando Logitech C920 | Backend: {backend} | OpenCV: {getattr(cv2, '__version__', 'desconocida')} ---")

    # Ajustes manuales esenciales
    if safe_hasattr(cv2, "CAP_PROP_AUTOFOCUS"):
        safe_set(cap, cv2.CAP_PROP_AUTOFOCUS, 0, "AutoFocus (0=manual)")
    if safe_hasattr(cv2, "CAP_PROP_AUTO_EXPOSURE"):
        if backend.upper() == "DSHOW":
            safe_set(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 0.25, "Auto Exposure (DSHOW manual=0.25)")
        else:
            ok = safe_set(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 1, "Auto Exposure (MSMF manual intent=1)")
            if not ok:
                safe_set(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 0, "Auto Exposure (MSMF manual alterno=0)")

    if safe_hasattr(cv2, "CAP_PROP_AUTO_WB"):
        safe_set(cap, cv2.CAP_PROP_AUTO_WB, 0, "Auto White Balance (0=manual)")

    time.sleep(0.5)

    expo_val = -5 if backend.upper() == "DSHOW" else 5
    ajustes = [
        ("Brillo",      getattr(cv2, "CAP_PROP_BRIGHTNESS", 10), 128),
        ("Contraste",   getattr(cv2, "CAP_PROP_CONTRAST", 11), 128),
        ("Saturación",  getattr(cv2, "CAP_PROP_SATURATION", 12), 128),
        ("Nitidez",     getattr(cv2, "CAP_PROP_SHARPNESS", 20), 128),
        ("Ganancia",    getattr(cv2, "CAP_PROP_GAIN", 14), 0),
        ("Exposición",  getattr(cv2, "CAP_PROP_EXPOSURE", 15), expo_val),
        ("Enfoque",     getattr(cv2, "CAP_PROP_FOCUS", 28), 0),
    ]
    for nombre, prop, valor in ajustes:
        safe_set(cap, prop, valor, nombre)

    if safe_hasattr(cv2, "CAP_PROP_WB_TEMPERATURE"):
        safe_set(cap, cv2.CAP_PROP_WB_TEMPERATURE, 4000, "WB Temperatura (K)")

    # ====== Captura / Grabación ======
    # Resolución típica C920
    deseado_ancho = 1800
    deseado_alto  = 800
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, deseado_ancho)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, deseado_alto)
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or deseado_ancho
    alto  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or deseado_alto
    print(f"Resolución efectiva: {ancho}x{alto}")

    # FPS efectivos
    fps_cam = cap.get(cv2.CAP_PROP_FPS)
    if not fps_cam or fps_cam <= 0:
        fps_cam = 30
    fps = int(round(fps_cam))
    print(f"FPS efectivos: {fps}")

    os.makedirs(carpeta_salida, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_base = f"C920_{timestamp}"
    ruta_base = os.path.join(carpeta_salida, nombre_base)

    writer = None
    ruta_video = None
    grabando = False

    if grabar_auto:
        writer, ruta_video = crear_escritor_video_avi(ruta_base, ancho, alto, fps)
        if writer is None:
            print("No se pudo crear el escritor AVI. Revisa códecs o permisos.")
        else:
            grabando = True

    print("\nControles:")
    print("  q  -> salir")
    print("  r  -> iniciar/pausar grabación")
    print("  n  -> iniciar nueva grabación (cierra la actual)")
    print("  s  -> detener y guardar (si está grabando)")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer frame (¿otra app está usando la cámara?)")
            break

        cv2.putText(frame, f"C920 Manual ({backend})", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if grabando and writer:
            cv2.circle(frame, (ancho - 30, 30), 10, (0, 0, 255), -1)
            cv2.putText(frame, "REC", (ancho - 80, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
            writer.write(frame)

        cv2.imshow("Logitech C920 - Configuracion + Grabacion (AVI)", frame)
        k = cv2.waitKey(1) & 0xFF

        if k == ord('q'):
            break

        elif k == ord('r'):
            if not grabando:
                if writer is None:
                    writer, ruta_video = crear_escritor_video_avi(ruta_base, ancho, alto, fps)
                if writer is not None:
                    grabando = True
                    print("Grabación INICIADA.")
            else:
                grabando = False
                print("Grabación en PAUSA (archivo sigue abierto).")

        elif k == ord('s'):
            if writer is not None:
                writer.release()
                print(f"Grabación GUARDADA en: {ruta_video}")
                writer = None
                ruta_video = None
                grabando = False

        elif k == ord('n'):
            if writer is not None:
                writer.release()
                print(f"Grabación GUARDADA en: {ruta_video}")
                writer = None
                ruta_video = None
                grabando = False
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_base = f"C920_{timestamp}"
            ruta_base = os.path.join(carpeta_salida, nombre_base)
            writer, ruta_video = crear_escritor_video_avi(ruta_base, ancho, alto, fps)
            if writer is not None:
                grabando = True
                print("Nueva grabación INICIADA.")

    if writer is not None:
        writer.release()
        print(f"Grabación GUARDADA en: {ruta_video}")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    configurar_camara_c920(id_camara=0, grabar_auto=False, carpeta_salida="grabaciones")
