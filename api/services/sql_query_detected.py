import os
import torch
import numpy as np
from PIL import Image
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ultralytics import YOLO
from ultralytics.utils.plotting import save_one_box
from pathlib import Path
from .. import models
from transformers import ViTForImageClassification, ViTFeatureExtractor, ViTImageProcessor

# Path dasar proyek
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Path model YOLO
yolo_model_path = BASE_DIR / "models" / "best_yolo.pt"
model = YOLO(str(yolo_model_path))

# Ambil daftar nama class dari model
CLASS_NAMES = model.names  # Misal: {0: "11", 1: "12", ..., 31: "48"}

# Folder penyimpanan gambar di dalam `uploads/`
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

CROPPED_DIR = UPLOADS_DIR / "cropped_detected"  # Crop standar
CROPPED_DIR.mkdir(parents=True, exist_ok=True)

CROPPED_SQUARED_DIR = UPLOADS_DIR / "cropped_squared_detected"  # Crop square
CROPPED_SQUARED_DIR.mkdir(parents=True, exist_ok=True)

DETECTED_DIR = UPLOADS_DIR / "detected_uploads"
DETECTED_DIR.mkdir(parents=True, exist_ok=True)

# ViT models
vit_model_path = BASE_DIR / "models" / "best_vit_largev2.0.pth"
# feature_extractor = ViTFeatureExtractor.from_pretrained("google/vit-large-patch16-224")
feature_extractor = ViTImageProcessor.from_pretrained("google/vit-large-patch16-224-in21k")
vit_model = ViTForImageClassification.from_pretrained("google/vit-large-patch16-224-in21k", num_labels=5)

# Load state dict jika model sudah di-train ulang
vit_model.load_state_dict(torch.load(vit_model_path, map_location=torch.device('cpu')))
vit_model.eval()

def detect_disease(image_path):
    """Gunakan ViT untuk mendeteksi penyakit dari gambar."""
    image = Image.open(image_path).convert("RGB")
    inputs = feature_extractor(images=image, return_tensors="pt")
    outputs = vit_model(**inputs)
    logits = outputs.logits
    predicted_class = logits.argmax(-1).item()

    # Mapping hasil prediksi ke nama penyakit
    class_labels = ['Impaksi', 'Karies', 'LesiPeriapikal', 'Normal', 'Resorbsi']
    return class_labels[predicted_class]

def detect_and_store(db: Session, no_rm: str):
    """Deteksi gigi menggunakan YOLOv8, crop hasil deteksi secara square, dan simpan ke database."""
    
    # Ambil gambar panoramic dari database
    panoramic = db.query(models.PanoramicImage).filter(models.PanoramicImage.no_rm == no_rm).first()
    if not panoramic:
        raise HTTPException(status_code=404, detail="Panoramic image not found")
    
    image_path = panoramic.image_url
    results = model(image_path)
    detections = results[0].boxes.data.cpu().numpy()

    # Struktur penyimpanan hasil crop
    cropped_dir = CROPPED_DIR / no_rm
    cropped_dir.mkdir(parents=True, exist_ok=True)

    cropped_squared_dir = CROPPED_SQUARED_DIR / no_rm
    cropped_squared_dir.mkdir(parents=True, exist_ok=True)

    # Konversi gambar ke format yang bisa diproses
    image = Image.open(image_path).convert("RGB")
    imc = np.array(image)  # Untuk `save_one_box`

    # Simpan gambar deteksi dengan bounding box
    detected_image_path = DETECTED_DIR / f"detected_{no_rm}.jpg"
    results[0].save(filename=detected_image_path)

    # Dictionary untuk menyimpan hasil deteksi
    detected_teeth = {}
    
    # Loop setiap hasil deteksi
    for det in detections:
        xyxy = torch.tensor(det[:4])  # Koordinat bounding box
        class_index = int(det[5])  # Class ID dari YOLO

        # Pastikan class_index ada dalam CLASS_NAMES sebelum melanjutkan
        if class_index not in CLASS_NAMES:
            print(f"⚠️ Class index {class_index} tidak ditemukan dalam CLASS_NAMES, dilewati.")
            continue

        # Ambil nomor gigi yang benar dari CLASS_NAMES
        tooth_number = CLASS_NAMES[class_index].replace(" ", "_")

        # Path penyimpanan gambar hasil crop standar
        cropped_filename = f"{tooth_number}.jpg"
        cropped_path = cropped_dir / cropped_filename

        # Path penyimpanan gambar hasil crop square
        cropped_squared_path = cropped_squared_dir / cropped_filename

        # Crop standar
        save_one_box(xyxy, imc, file=cropped_path, BGR=True)

        # Crop square
        save_one_box(xyxy, imc, file=cropped_squared_path, square=True, BGR=True)
        
        # Klasifikasi penyakit
        disease_result = detect_disease(cropped_squared_path)

        # Simpan dalam dictionary hasil deteksi
        detected_teeth[tooth_number] = {
            "cropped_image_url": f"/uploads/cropped_detected/{no_rm}/{cropped_filename}",
            "cropped_squared_image_url": f"/uploads/cropped_squared_detected/{no_rm}/{cropped_filename}",
            "detection_desease_result": disease_result
        }

        print(f"✅ Cropped: {cropped_path}")
        print(f"✅ Cropped (square): {cropped_squared_path}")

    # Simpan hasil ke database
    db_detected = models.DetectedPanoramic(
        id_panoramic_image=panoramic.id,
        detected_image_url=f"/uploads/detected_uploads/detected_{no_rm}.jpg",  # URL untuk diakses frontend
        result_detection_images=detected_teeth  # JSON hasil cropping
    )
    db.add(db_detected)
    db.commit()
    db.refresh(db_detected)
    
    return db_detected
