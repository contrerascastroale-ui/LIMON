import cv2
import sys
import os
import time
def count_frames(video_path):
    if not os.path.exists(video_path):
        print(f"Error: El archivo '{video_path}' no existe.")
        return

    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: No se pudo abrir el video '{video_path}'.")
        return

    # Método 1: Usar la propiedad de metadatos (Rápido, pero a veces inexacto)
    total_metadata = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Método 2: Conteo manual (Lento, pero preciso)
    count = 0
    print(f"Contando frames de: {video_path}...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
    
    cap.release()

    print("-" * 30)
    print(f"Resultados para: {os.path.basename(video_path)}")
    print(f"Frames (Metadatos): {total_metadata}")
    print(f"Frames (Conteo manual): {count}")
    print("-" * 30)
    
    if total_metadata != count:
        print("Aviso: Hay una discrepancia entre los metadatos y el conteo real.")

if __name__ == "__main__":
    folder = "grabaciones"
    
    if not os.path.exists(folder):
        print(f"Error: La carpeta '{folder}' no existe.")
        sys.exit(1)

    # Obtener lista de videos
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.avi', '.mp4', '.mkv'))]
    
    if not files:
        print(f"No se encontraron videos en la carpeta '{folder}'.")
        sys.exit(1)

    # Ordenar archivos por fecha de creación (más reciente primero)
    files.sort(key=lambda x: os.path.getctime(os.path.join(folder, x)), reverse=True)

    print("\n--- SELECCIÓN DE VIDEO ---")
    for i, file in enumerate(files):
        creation_time = time.ctime(os.path.getctime(os.path.join(folder, file)))
        print(f"[{i}] {file} ({creation_time})")
    
    try:
        seleccion = input(f"\nSelecciona el número del video (0-{len(files)-1}) o 'q' para salir: ")
        
        if seleccion.lower() == 'q':
            sys.exit(0)
            
        indice = int(seleccion)
        if 0 <= indice < len(files):
            video_file = os.path.join(folder, files[indice])
            count_frames(video_file)
        else:
            print("Índice fuera de rango.")
    except ValueError:
        print("Entrada no válida. Por favor, introduce un número.")
