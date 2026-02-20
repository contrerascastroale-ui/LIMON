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

def crear_escritor_video(path_salida, ancho, alto, fps_deseado=30, prefer_mp4=True):
    """
    Intenta crear un VideoWriter con el mejor códec disponible.
    prefer_mp4=True intenta H.264/MP4 primero (si hay codec instalado).
    Fallback a MJPG/AVI si H.264 no está disponible.
    """
    if prefer_mp4:
        # Intento 1: MP4 con H.264 (requiere que Windows tenga un encoder disponible)
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # 'H264' o 'avc1' (depende del sistema)
        ruta_mp4 = os.path.splitext(path_salida)[0] + ".mp4"
        writer = cv2.VideoWriter(ruta_mp4, fourcc, fps_deseado, (ancho, alto))
        if writer.isOpened():
            print(f"Grabando en: {ruta_mp4} (H.264/avc1) @ {fps_deseado} FPS, {ancho}x{alto}")
            return writer, ruta_mp4

        # Intento 2: MP4 con 'mp4v' (MPEG-4 parte 2)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(ruta_mp4, fourcc, fps_deseado, (ancho, alto))
        if writer.isOpened():
            print(f"Grabando en: {ruta_mp4} (mp4v) @ {fps_deseado} FPS, {ancho}x{alto}")
            return writer, ruta_mp4

    # Fallback: AVI con MJPG (alto bitrate, pero muy compatible)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    ruta_avi = os.path.splitext(path_salida)[0] + ".avi"
    writer = cv2.VideoWriter(ruta_avi, fourcc, fps_deseado, (ancho, alto))
    if writer.isOpened():
        print(f"Grabando en: {ruta_avi} (MJPG) @ {fps_deseado} FPS, {ancho}x{alto}")
        return writer, ruta_avi

    # Último intento: XVID (AVI)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    writer = cv2.VideoWriter(ruta_avi, fourcc, fps_deseado, (ancho, alto))
    if writer.isOpened():
        print(f"Grabando en: {ruta_avi} (XVID) @ {fps_deseado} FPS, {ancho}x{alto}")
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

    # Ajustes manuales esenciales (similar a tu script anterior)
    if safe_hasattr(cv2, "CAP_PROP_AUTOFOCUS"):
        safe_set(cap, cv2.CAP_PROP_AUTOFOCUS, 0, "AutoFocus (0=manual)")
    if safe_hasattr(cv2, "CAP_PROP_AUTO_EXPOSURE"):
        if backend.upper() == "DSHOW":
            safe_set(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 0.25, "Auto Exposure (DSHOW manual=0.25)")
        else:
            ok = safe_set(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 1, "Auto Exposure (MSMF manual intent=1)")
            if not ok:
                safe_set(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 0, "Auto Exposure (MSMF manual alterno=0)")

    # WB: si existe CAP_PROP_AUTO_WB, apágalo. Si no, setea temperatura directamente.
    if safe_hasattr(cv2, "CAP_PROP_AUTO_WB"):
        safe_set(cap, cv2.CAP_PROP_AUTO_WB, 0, "Auto White Balance (0=manual)")

    time.sleep(0.5)

    # Exposición típica por backend
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

    # ====== Parámetros de captura / grabación ======
    # Resolución deseada (ajústala a tu C920: 1280x720 o 1920x1080)
    deseado_ancho = 1800
    deseado_alto  = 800
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, deseado_ancho)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, deseado_alto)
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or deseado_ancho
    alto  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or deseado_alto
    print(f"Resolución efectiva: {ancho}x{alto}")

    # FPS: intenta leer de la cámara; si no, usa 30
    fps_cam = cap.get(cv2.CAP_PROP_FPS)
    if not fps_cam or fps_cam <= 0:
        fps_cam = 30
    fps = int(round(fps_cam))
    print(f"FPS efectivos: {fps}")

    # Carpeta de salida
    os.makedirs(carpeta_salida, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_base = f"C920_{timestamp}"
    ruta_base = os.path.join(carpeta_salida, nombre_base)

    writer = None
    ruta_video = None
    grabando = False

    if grabar_auto:
        writer, ruta_video = crear_escritor_video(ruta_base, ancho, alto, fps, prefer_mp4=True)
        if writer is None:
            print("No se pudo crear el escritor de video. Verifica códecs instalados.")
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

        # (Opcional) convertir a BGR ya viene así; si usaras cvtColor, hazlo antes de escribir

        # Overlay estado
        cv2.putText(frame, f"C920 Manual ({backend})", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if grabando:
            # Indicador REC
            cv2.circle(frame, (ancho - 30, 30), 10, (0, 0, 255), -1)
            cv2.putText(frame, "REC", (ancho - 80, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
            if writer:
                writer.write(frame)

        cv2.imshow("Logitech C920 - Configuracion + Grabacion", frame)
        k = cv2.waitKey(1) & 0xFF

        if k == ord('q'):
            break

        elif k == ord('r'):
            # toggle grabación
            if not grabando:
                if writer is None:
                    writer, ruta_video = crear_escritor_video(ruta_base, ancho, alto, fps, prefer_mp4=True)
                if writer is not None:
                    grabando = True
                    print("Grabación INICIADA.")
            else:
                grabando = False
                print("Grabación en PAUSA (archivo sigue abierto).")

        elif k == ord('s'):
            # detener y cerrar archivo actual
            if writer is not None:
                writer.release()
                print(f"Grabación GUARDADA en: {ruta_video}")
                writer = None
                ruta_video = None
                grabando = False

        elif k == ord('n'):
            # cierra actual (si existe) y abre uno nuevo
            if writer is not None:
                writer.release()
                print(f"Grabación GUARDADA en: {ruta_video}")
                writer = None
                ruta_video = None
                grabando = False
            # nuevo nombre
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_base = f"C920_{timestamp}"
            ruta_base = os.path.join(carpeta_salida, nombre_base)
            writer, ruta_video = crear_escritor_video(ruta_base, ancho, alto, fps, prefer_mp4=True)
            if writer is not None:
                grabando = True
                print("Nueva grabación INICIADA.")

    # Cleanup
    if writer is not None:
        writer.release()
        print(f"Grabación GUARDADA en: {ruta_video}")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Cambia a True si quieres que empiece grabando automáticamente
    configurar_camara_c920(id_camara=0, grabar_auto=False, carpeta_salida="grabaciones")
