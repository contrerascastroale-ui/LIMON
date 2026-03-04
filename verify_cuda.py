import torch
from ultralytics import YOLO

def verify_gpu_environment():
    print("=== VERIFICACIÓN DE ENTORNO GPU ===")
    
    # 1. Verificar PyTorch y CUDA
    cuda_available = torch.cuda.is_available()
    print(f"[Torch] PyTorch version: {torch.__version__}")
    print(f"[CUDA] CUDA disponible en PyTorch: {'Sí' if cuda_available else 'No'}")
    
    if cuda_available:
        print(f"[CUDA] Versión de CUDA compilada con PyTorch: {torch.version.cuda}")
        print(f"[CUDA] Cantidad de GPUs detectadas: {torch.cuda.device_count()}")
        print(f"[CUDA] Nombre de la GPU 0: {torch.cuda.get_device_name(0)}")
        
        # 2. Verificar cuDNN
        cudnn_available = torch.backends.cudnn.is_available()
        print(f"[cuDNN] cuDNN disponible: {'Sí' if cudnn_available else 'No'}")
        if cudnn_available:
            print(f"[cuDNN] Versión de cuDNN: {torch.backends.cudnn.version()}")
    else:
        print("\n[ADVERTENCIA] PyTorch no está detectando CUDA.")
        print("Para instalar PyTorch con soporte CUDA (ejemplo para Windows/CUDA 11.8 o 12.1):")
        print("pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        print("o")
        print("pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")

if __name__ == '__main__':
    verify_gpu_environment()
