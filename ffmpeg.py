import cv2
import time
import subprocess
import sys

def safe_hasattr(module, name):
    try:
        getattr(module, name)
        return True
    except Exception:
        return False

def safe_set(cap, prop, value, nombre=""):
    """Intenta setear una propiedad y reporta el resultado de forma segura."""
    try:
        ok = cap.set(prop, value)
        val = cap.get(prop) if ok else "N/A"
        print(f"{nombre or prop}: set={value} -> {'OK' if ok else 'FALLÓ'} (actual={val})")
        return ok
    except Exception as e:
        print(f"{nombre or prop}: EXCEPCIÓN al setear -> {e}")
        return False

def grabar_con_ffmpeg(id_camara=0, nombre_archivo="video_crudo.mp4"):
    print(f"Intentando abrir cámara {id_camara} con DSHOW...")
    # Usamos DSHOW para mejor control de propiedades en Windows
    cap = cv2.VideoCapture(id_camara, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Fallo con DSHOW. Intentando con MSMF...")
        cap = cv2.VideoCapture(id_camara, cv2.CAP_MSMF)

    if not cap.isOpened():
        print(f"Error: No se pudo abrir la cámara {id_camara}.")
        return

    # --- CONFIGURACIÓN DE RESOLUCIÓN ---
    ancho, alto = 640, 480
    fps = 30
    safe_set(cap, cv2.CAP_PROP_FRAME_WIDTH, ancho, "Ancho")
    safe_set(cap, cv2.CAP_PROP_FRAME_HEIGHT, alto, "Alto")
    safe_set(cap, cv2.CAP_PROP_FPS, fps, "FPS")

    backend = getattr(cap, "getBackendName", lambda: "desconocido")()
    print(f"--- Configurando Logitech C920 | Backend: {backend} ---")

    # --- APLICAR CONFIGURACIONES MANUALES (del código original) ---
    
    # 1) AUTOFOCUS -> manual
    if safe_hasattr(cv2, "CAP_PROP_AUTOFOCUS"):
        safe_set(cap, cv2.CAP_PROP_AUTOFOCUS, 0, "AutoFocus (0=manual)")

    # 2) AUTO EXPOSURE -> manual
    if safe_hasattr(cv2, "CAP_PROP_AUTO_EXPOSURE"):
        if backend.upper() == "DSHOW":
            safe_set(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 0.25, "Auto Exposure (DSHOW manual=0.25)")
        else:
            safe_set(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 1, "Auto Exposure (MSMF manual)")

    # 3) AUTO WHITE BALANCE -> manual
    if safe_hasattr(cv2, "CAP_PROP_AUTO_WB"):
        safe_set(cap, cv2.CAP_PROP_AUTO_WB, 0, "Auto White Balance (0=manual)")

    time.sleep(0.5)

    # Ajustes manuales adicionales
    expo_val = -5 if backend.upper() == "DSHOW" else 5
    ajustes = [
        ("Brillo",      cv2.CAP_PROP_BRIGHTNESS, 128),
        ("Contraste",   cv2.CAP_PROP_CONTRAST, 128),
        ("Saturación",  cv2.CAP_PROP_SATURATION, 128),
        ("Nitidez",     cv2.CAP_PROP_SHARPNESS, 128),
        ("Ganancia",    cv2.CAP_PROP_GAIN, 0),
        ("Exposición",  cv2.CAP_PROP_EXPOSURE, expo_val),
        ("Enfoque",     cv2.CAP_PROP_FOCUS, 0),
    ]

    for nombre, prop, valor in ajustes:
        safe_set(cap, prop, valor, nombre)

    if safe_hasattr(cv2, "CAP_PROP_WB_TEMPERATURE"):
        safe_set(cap, cv2.CAP_PROP_WB_TEMPERATURE, 4000, "WB Temperatura (K)")

    # --- PREPARACIÓN DE FFmpeg ---
    # Comando para recibir frames crudos (BGR24) desde el pipe
    command = [
        'ffmpeg',
        '-y',                         # Sobrescribir archivo si existe
        '-f', 'rawvideo',             # Formato de entrada: video crudo
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',          # OpenCV entrega BGR por defecto
        '-s', f'{ancho}x{alto}',      # Resolución
        '-r', str(fps),               # Frames por segundo
        '-i', '-',                    # La entrada vendrá del pipe (stdin)
        '-c:v', 'libx264',            # Encoder H.264
        '-preset', 'ultrafast',       # Preset para mínima latencia/carga CPU
        '-pix_fmt', 'yuv420p',        # Formato de color compatible con la mayoría de reproductores
        nombre_archivo
    ]

    print(f"\nIniciando grabación en: {nombre_archivo}")
    print("Presiona Ctrl+C para detener la grabación.")

    try:
        # Abrimos el proceso de FFmpeg con stdin conectado al pipe
        proc = subprocess.Popen(command, stdin=subprocess.PIPE)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar frame.")
                break

            # Enviamos los bytes "crudos" del frame directamente al stdin de FFmpeg
            proc.stdin.write(frame.tobytes())

    except KeyboardInterrupt:
        print("\nDeteniendo grabación por el usuario...")
    except Exception as e:
        print(f"\nError durante la grabación: {e}")
    finally:
        # Limpieza
        cap.release()
        if 'proc' in locals():
            proc.stdin.close()
            proc.wait()
        print("Grabación finalizada y guardada.")

if __name__ == "__main__":
    # Puedes cambiar el nombre del archivo aquí
    grabar_con_ffmpeg(id_camara=0, nombre_archivo="grabacion_ffmpeg.mp4")
