from ultralytics import YOLO
import cv2

def stream_yolo():
    """
    Inicia un stream de video usando la cámara 0, muestra detecciones y guarda el video.
    """
    # Cargar el modelo
    model = YOLO("yolo26n.pt")

    print("--- CONFIGURACIÓN ---")
    print("1. Se abrirá una ventana de video (show=True).")
    print("2. El video se guardará en la carpeta 'runs/detect/'.")
    print("3. Para salir: Pulsa 'q' EN LA VENTANA DE VIDEO o Ctrl+C en la terminal.\n")

    # Ejecutar la predicción
    # show=True: Requerido para ver la ventana y usar la tecla 'q'
    # save=True: Guarda el video resultante
    # stream=True: Procesa el flujo frame a frame
    results = model.predict(source="0", show=True, stream=True, save=True)

    try:
        for result in results:
            # Solo iteramos para mantener vivo el proceso
            pass
    except KeyboardInterrupt:
        print("\n[INFO] Detención por terminal detectada.")
    finally:
        print("[INFO] Cerrando y guardando archivo...")
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        stream_yolo()
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un problema: {e}")
