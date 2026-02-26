from ultralytics import YOLO

# Cargar el modelo YOLOv26 nano
model = YOLO('yolo26n.pt')

# Realizar la predicción sobre la imagen proporcionada
# 'save=True' guarda el resultado en la carpeta runs/detect/predict
# 'show=True' muestra la imagen con las detecciones (si hay un entorno gráfico disponible)
results = model.predict(source='https://ultralytics.com/images/bus.jpg', save=True, show=True)

print("Predicción completada. Los resultados se han guardado en la carpeta 'runs/detect/'.")
