import cv2
import time
import datetime
import os
import msvcrt  # Específico para Windows, detecta teclas en la consola

def safe_set(cap, prop, value, nombre=""):
    """Intenta setear una propiedad y reporta el resultado."""
    try:
        ok = cap.set(prop, value)
        val = cap.get(prop) if ok else "N/A"
        print(f"{nombre or prop}: set={value} -> {'OK' if ok else 'FALLÓ'} (actual={val})")
        return ok
    except Exception as e:
        print(f"{nombre or prop}: EXCEPCIÓN -> {e}")
        return False

def init_camera(id_camara=0):
    print(f"Abriendo cámara {id_camara} con DSHOW (recomendado para C920)...")
    cap = cv2.VideoCapture(id_camara, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return None

    # 1) Configurar el codec de entrada a MJPG para permitir 1080p @ 30fps
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    
    # 2) Configurar Máxima Resolución
    safe_set(cap, cv2.CAP_PROP_FRAME_WIDTH, 1920, "Ancho")
    safe_set(cap, cv2.CAP_PROP_FRAME_HEIGHT, 1080, "Alto")
    safe_set(cap, cv2.CAP_PROP_FPS, 30, "FPS")

    # 3) Configuraciones Manuales Críticas para mantener 30 FPS
    # El Auto-Exposure suele bajar los FPS en condiciones de poca luz. Forzamos manual.
    safe_set(cap, cv2.CAP_PROP_AUTOFOCUS, 0, "AutoFocus Off")
    safe_set(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 0.25, "Auto Exposure Manual (0.25)") 
    safe_set(cap, cv2.CAP_PROP_EXPOSURE, -5, "Exposición (-5)") # Ajustar según luz, -5 es un buen punto de partida para 30fps
    
    # Desactivar White Balance automático si es posible
    if hasattr(cv2, "CAP_PROP_AUTO_WB"):
        safe_set(cap, cv2.CAP_PROP_AUTO_WB, 0, "Auto WB Off")
    
    safe_set(cap, cv2.CAP_PROP_GAIN, 0, "Ganancia")
    safe_set(cap, cv2.CAP_PROP_FOCUS, 0, "Enfoque Fijo")

    return cap

def main():
    cap = init_camera(0)
    if cap is None:
        return

    recording = False
    out = None
    
    # Crear carpeta para grabaciones si no existe
    output_dir = "grabaciones"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("\n--- CONTROL DE GRABACIÓN (Sin Ventana de Video) ---")
    print("Presiona 'r' para empezar a grabar")
    print("Presiona 's' para detener la grabación")
    print("Presiona 'q' para salir del programa")
    print("---------------------------------------------------\n")

    try:
        while True:
            # Capturar frame para mantener el buffer de la cámara limpio
            ret, frame = cap.read()
            if not ret:
                print("Error leyendo de la cámara")
                break

            # Si estamos grabando, escribir el frame
            if recording and out is not None:
                out.write(frame)

            # Verificar si se presionó una tecla en la consola
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                
                if key == 'r' and not recording:
                    # Iniciar grabación
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(output_dir, f"grabacion_{timestamp}.avi")
                    
                    # Definir el codec y crear el objeto VideoWriter
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    
                    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
                    recording = True
                    print(f"[*] GRABANDO: {filename}")

                elif key == 's' and recording:
                    # Detener grabación
                    recording = False
                    if out is not None:
                        out.release()
                        out = None
                    print("[ ] Grabación FINALIZADA")

                elif key == 'q':
                    # Salir
                    print("[!] Saliendo...")
                    break
            
            # Pequeño sleep para no saturar el CPU si el loop es demasiado rápido
            # pero no tan largo para no perder frames. 
            # Como cap.read() es bloqueante al frame rate de la cámara, suele ser suficiente.

    finally:
        if out is not None:
            out.release()
        cap.release()
        print("Cámara liberada. Programa terminado.")

if __name__ == "__main__":
    main()
