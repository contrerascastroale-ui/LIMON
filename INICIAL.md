 import cv2
import time

def configurar_camara_c920(id_camara=0): # Cambiado a 2 basándonos en tu prueba anterior
    # Intentamos primero con DSHOW (mejor para manual)
    print(f"Intentando abrir cámara {id_camara} con DSHOW...")
    cap = cv2.VideoCapture(id_camara + cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Fallo con DSHOW. Intentando con MSMF (Media Foundation)...")
        cap = cv2.VideoCapture(id_camara + cv2.CAP_MSMF)

    if not cap.isOpened():
        print(f"Error: No se pudo abrir la cámara {id_camara} con ningún backend.")
        return

    print("--- Configurando Logitech C920 en Modo Manual ---")

    # 1. Desactivar funciones automáticas primero
    # ------------------------------------------
    
    # Desactivar Auto Foco (0 = Manual, 1 = Auto)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    
    # Desactivar Auto Exposición
    # En Windows/DSHOW: 0.25 suele ser Manual, 0.75 es Auto. 
    # Alternativamente, a veces se usa 1 para manual y 3 para auto.
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25) 
    
    # Desactivar Balance de Blancos Automático (0 = Manual)
    cap.set(cv2.CAP_PROP_AUTOWB, 0)

    # Esperar un momento para que los cambios se apliquen
    time.sleep(1)

    # 2. Definir valores manuales específicos
    # ------------------------------------------
    # Nota: Los rangos dependen del driver, pero estos son valores típicos para C920
    
    settings = {
        "Brillo (Brightness)": (cv2.CAP_PROP_BRIGHTNESS, 128),
        "Contraste (Contrast)": (cv2.CAP_PROP_CONTRAST, 128),
        "Saturación (Saturation)": (cv2.CAP_PROP_SATURATION, 128),
        "Nitidez (Sharpness)": (cv2.CAP_PROP_SHARPNESS, 128),
        "Ganancia (Gain)": (cv2.CAP_PROP_GAIN, 0),
        "Exposición (Exposure)": (cv2.CAP_PROP_EXPOSURE, -5), # Valores negativos son comunes en DSHOW
        "Enfoque (Focus)": (cv2.CAP_PROP_FOCUS, 0),          # 0 es infinito, valores altos son macro
        "Balance de Blancos (WB)": (cv2.CAP_PROP_WB_TEMPERATURE, 4000)
    }

    for name, (prop, value) in settings.items():
        success = cap.set(prop, value)
        print(f"{name}: Establecido en {value} -> {'Éxito' if success else 'Fallo'}")

    # 3. Mostrar la cámara para verificar
    # ------------------------------------------
    print("\nPresiona 'q' para salir...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.putText(frame, "C920 MODO MANUAL ACTIVO", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Logitech C920 - Configuración Manual", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
