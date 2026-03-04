import os
import cv2
import time
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

def stream_yolo(show_fps=True, imgsz=640):
    """
    Inicia un stream de video usando la cámara 0 con la optimización de DirectShow
    y unifica la resolución de la cámara con la de la IA (imgsz).
    """
    print("[INFO] Cargando modelo...")
    model = YOLO("yolo26n.pt")

    print("[INFO] Iniciando cámara (DirectShow)...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Definir resolución de cámara igual a imgsz
    # Nota: imgsz suele ser un valor único (ej. 640), se asume 4:3 o la cámara ajustará al más cercano
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, imgsz)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, imgsz)

    if not cap.isOpened():
        print("[ERROR] No se pudo acceder a la cámara.")
        return

    # Leer resolución real (la cámara podría no soportar la solicitada y asignar la más cercana)
    real_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    real_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[INFO] Resolución activa: {real_width}x{real_height}")

    # Obtener el path original de guardado (predict, predict2...)
    save_dir = get_save_dir()
    video_path = os.path.join(save_dir, "0.avi") # YOLO guarda la cámara 0 como 0.avi por defecto

    print("\n--- CONFIGURACIÓN ---")
    print("1. Se abrirá la ventana de video de inmediato.")
    print(f"2. El video se guardará en '{video_path}'.")
    print("3. Para salir: Pulsa 'q' EN LA VENTANA DE VIDEO o Ctrl+C en la terminal.\n")

    # Configuración del VideoWriter usando la resolución real
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0

    # Usar XVID para .avi (original) o mp4v para .mp4
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(video_path, fourcc, fps, (real_width, real_height))

    frames_written = 0
    total_frames_processed = 0
    start_time = None
    prev_frame_time = 0
    max_fps = 0
    min_fps = float('inf')

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Cálculo de FPS de la vista previa
            current_time = time.time()
            render_fps = 0
            if prev_frame_time != 0:
                render_fps = 1 / (current_time - prev_frame_time)
                
                # Solo tomamos máximos y mínimos después de 5 segundos de grabación
                # para evitar el sesgo del inicio (inicialización de cámara/modelo)
                if start_time is not None and (current_time - start_time) > 5:
                    if render_fps > max_fps: max_fps = render_fps
                    if render_fps < min_fps: min_fps = render_fps
            prev_frame_time = current_time
            
            total_frames_processed += 1
            
            # Predict con el parámetro imgsz solicitado
            results = model.predict(frame, verbose=False, imgsz=imgsz)
            annotated_frame = results[0].plot()
            
            # Dibujar los FPS sobre la imagen solo si se solicita
            if show_fps:
                cv2.putText(annotated_frame, f"FPS: {render_fps:.1f}", (20, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Inicializamos el contador de tiempo DESPUÉS de analizar el primer frame
            # para que el warmup de YOLO no afecte la sincronización inicial.
            if start_time is None:
                start_time = time.time()
                
            cv2.imshow("YOLO Preview", annotated_frame)
            
            # Sincronización de velocidad de video
            # Rellenamos los frames consumidos por el tiempo de procesamiento de YOLO
            # para que el video resultante se reproduzca a velocidad normal.
            elapsed = time.time() - start_time
            expected_frames = int(elapsed * fps)
            frames_to_write = expected_frames - frames_written
            
            # Siempre escribimos el frame actual por lo menos 1 vez
            if frames_to_write < 1:
                frames_to_write = 1
                
            for _ in range(frames_to_write):
                out.write(annotated_frame)
                frames_written += 1
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n[INFO] Detención por terminal detectada.")
    finally:
        print(f"[INFO] Video guardado en: {video_path}")
        
        # Calcular el promedio de FPS final
        if start_time is not None:
            total_elapsed = time.time() - start_time
            if total_elapsed > 0:
                avg_fps = total_frames_processed / total_elapsed
                print(f"[INFO] Promedio de procesamiento: {avg_fps:.2f} FPS")
                print(f"[INFO] FPS Máximo: {max_fps:.2f}")
                if min_fps != float('inf'):
                    print(f"[INFO] FPS Mínimo: {min_fps:.2f}")
                
        cap.release()
        out.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        # imgsz define tanto la resolución de la cámara como la de la IA
        # Valores recomendados: 320, 640, 1280
        stream_yolo(show_fps=True, imgsz=640)
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un problema: {e}")
