import torch
import sys

print(f"Python version: {sys.version}")
print(f"PyTorch version: {torch.__version__}")

if torch.cuda.is_available():
    print(f"✅ CUDA is available!")
    print(f"   Device count: {torch.cuda.device_count()}")
    print(f"   Current device: {torch.cuda.current_device()}")
    print(f"   Device name: {torch.cuda.get_device_name(0)}")
else:
    print(f"❌ CUDA is NOT available.")
