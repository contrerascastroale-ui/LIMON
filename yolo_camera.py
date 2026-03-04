import os
import cv2
from ultralytics import YOLO

def stream_yolo():
    """
    Inicia un stream de video usando la cámara 0, muestra detecciones y guarda el video.
    Optimizado con cv2.CAP_DSHOW para que la cámara abra instantáneamente en Windows.
    """
    print("[INFO] Cargando modelo...")
    # Cargar el modelo YOLO
    model = YOLO("yolo26n.pt")

    print("[INFO] Iniciando cámara (DirectShow)...")
    # CAP_DSHOW es crucial en Windows para evitar demoras de inicialización
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("[ERROR] No se pudo acceder a la cámara.")
        return

    # Preparar el directorio de guardado
    save_dir = os.path.join("runs", "detect")
    os.makedirs(save_dir, exist_ok=True)
    video_path = os.path.join(save_dir, "yolo_cam_record.mp4")

    print("\n--- CONFIGURACIÓN ---")
    print("1. Se abrirá la ventana de video de inmediato.")
    print(f"2. El video se guardará en '{video_path}'.")
    print("3. Para salir: Pulsa 'q' EN LA VENTANA DE VIDEO o Ctrl+C en la terminal.\n")

    # Obtener atributos de la cámara para guardar el video correctamente
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Predicción frame a frame (verbose=False evita saturar la terminal)
            results = model.predict(frame, verbose=False)
            
            # Extraer la imagen anotada
            annotated_frame = results[0].plot()
            
            # Mostrar la vista previa y guardar el frame
            cv2.imshow("YOLO Preview", annotated_frame)
            out.write(annotated_frame)
            
            # Pulsar 'q' para salir, check cada 1 ms
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n[INFO] Detención por terminal detectada.")
    finally:
        print("[INFO] Cerrando y guardando video...")
        cap.release()
        out.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        stream_yolo()
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un problema: {e}")
