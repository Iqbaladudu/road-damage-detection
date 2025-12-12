from pathlib import Path

from ultralytics import YOLO

current_dir = Path(__file__).parent
# Load the model from the same directory
model_path = current_dir / "YOLOv8_Small_RDD.pt"
model = YOLO("https://pub-0ccce103f38e4902912534cdb3973783.r2.dev/YOLOv8_Small_RDD.pt")