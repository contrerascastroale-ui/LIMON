import os
import cv2
from ultralytics import YOLO

def get_save_dir(base_dir="runs/detect", prefix="predict"):
    """
    Simula el comportamiento de YOLO para crear carpetas incrementales (predict, predict2, etc.)
    """
    if not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)
    
    i = 1
    while True:
        folder_name = prefix if i == 1 else f"{prefix}{i}"
        save_path = os.path.join(base_dir, folder_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            return save_path
        i += 1

def stream_yolo():
    """
    Inicia un stream de video usando la cámara 0 con la optimización de DirectShow
    y respeta el sistema de guardado original de YOLO.
    """
    print("[INFO] Cargando modelo...")
    model = YOLO("yolo26n.pt")

    print("[INFO] Iniciando cámara (DirectShow)...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("[ERROR] No se pudo acceder a la cámara.")
        return

    # Obtener el path original de guardado (predict, predict2...)
    save_dir = get_save_dir()
    video_path = os.path.join(save_dir, "0.avi") # YOLO guarda la cámara 0 como 0.avi por defecto

    print("\n--- CONFIGURACIÓN ---")
    print("1. Se abrirá la ventana de video de inmediato.")
    print(f"2. El video se guardará en '{video_path}'.")
    print("3. Para salir: Pulsa 'q' EN LA VENTANA DE VIDEO o Ctrl+C en la terminal.\n")

    # Configuración del VideoWriter
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0

    # Usar XVID para .avi (original) o mp4v para .mp4
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            results = model.predict(frame, verbose=False)
            annotated_frame = results[0].plot()
            
            cv2.imshow("YOLO Preview", annotated_frame)
            out.write(annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n[INFO] Detención por terminal detectada.")
    finally:
        print(f"[INFO] Video guardado en: {video_path}")
        cap.release()
        out.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        stream_yolo()
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un problema: {e}")
