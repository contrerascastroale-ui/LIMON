
import cv2
import time

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

def configurar_camara_c920(id_camara=0):
    print(f"Intentando abrir cámara {id_camara} con DSHOW...")
    cap = cv2.VideoCapture(id_camara, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Fallo con DSHOW. Intentando con MSMF (Media Foundation)...")
        cap = cv2.VideoCapture(id_camara, cv2.CAP_MSMF)

    if not cap.isOpened():
        print(f"Error: No se pudo abrir la cámara {id_camara} con ningún backend.")
        print("- Prueba con otro índice (0, 1).")
        print("- Cierra apps que usen la cámara (Teams/Zoom/OBS/navegador).")
        print("- Revisa Privacidad de Cámara en Windows.")
        return

    backend = getattr(cap, "getBackendName", lambda: "desconocido")()
    print(f"--- Configurando Logitech C920 | Backend: {backend} | OpenCV: {getattr(cv2, '__version__', 'desconocida')} ---")

    # 1) AUTOFOCUS -> manual
    if safe_hasattr(cv2, "CAP_PROP_AUTOFOCUS"):
        safe_set(cap, cv2.CAP_PROP_AUTOFOCUS, 0, "AutoFocus (0=manual)")
    else:
        print("Aviso: CAP_PROP_AUTOFOCUS no existe en esta build de OpenCV.")

    # 2) AUTO EXPOSURE -> manual
    # DSHOW: 0.25=manual, 0.75=auto
    # MSMF: en varias builds 1=manual, 0=auto (pero puede variar)
    if safe_hasattr(cv2, "CAP_PROP_AUTO_EXPOSURE"):
        if backend.upper() == "DSHOW":
            safe_set(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 0.25, "Auto Exposure (DSHOW manual=0.25)")
        else:
            ok = safe_set(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 1, "Auto Exposure (MSMF manual intent=1)")
            if not ok:
                safe_set(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 0, "Auto Exposure (MSMF manual alterno=0)")
    else:
        print("Aviso: CAP_PROP_AUTO_EXPOSURE no existe en esta build de OpenCV.")

    # 3) AUTO WHITE BALANCE -> manual (según disponibilidad)
    # Algunas builds usan CAP_PROP_AUTO_WB, otras no lo exponen. CAP_PROP_AUTOWB no existe en varias.
    auto_wb_disabled = False
    if safe_hasattr(cv2, "CAP_PROP_AUTO_WB"):
        # 0 = manual en la mayoría de builds
        auto_wb_disabled = safe_set(cap, cv2.CAP_PROP_AUTO_WB, 0, "Auto White Balance (0=manual)")
    else:
        print("Aviso: CAP_PROP_AUTO_WB no existe en esta build; se procederá con WB por temperatura directamente.")

    time.sleep(0.5)  # dar tiempo al driver

    # 4) Ajustes manuales típicos (ajusta a tu iluminación)
    # Nota: exposición en DSHOW suele ser negativa (-1 a -13 aprox.). En MSMF, a veces positivos.
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
        try:
            safe_set(cap, prop, valor, nombre)
        except Exception as e:
            print(f"{nombre}: propiedad no soportada o error -> {e}")

    # White Balance por temperatura (forzar manual si es posible)
    if safe_hasattr(cv2, "CAP_PROP_WB_TEMPERATURE"):
        # Si no pudimos apagar el auto-WB explícitamente, muchos drivers pasan a manual al setear temperatura:
        safe_set(cap, cv2.CAP_PROP_WB_TEMPERATURE, 4000, "WB Temperatura (K)")
    else:
        # Alternativo (raro en cámaras UVC modernas): canal BLUE_U
        if safe_hasattr(cv2, "CAP_PROP_WHITE_BALANCE_BLUE_U"):
            safe_set(cap, cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, 4000, "WB BlueU (aprox)")
        else:
            print("Aviso: No hay controles de balance de blancos expuestos por este backend/driver.")

    # 5) Vista previa
    print("\nPresiona 'q' para salir...")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer frame (¿otra app está usando la cámara?)")
            break

        cv2.putText(frame, f"C920 Manual ({backend})", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Logitech C920 - Configuración Manual", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    configurar_camara_c920(0)
