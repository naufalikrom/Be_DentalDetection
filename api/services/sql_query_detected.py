import shutil
import os
from sqlalchemy.orm import Session
from .. import models, schema

DETECTED_UPLOAD_DIR = "detected_uploads"
os.makedirs(DETECTED_UPLOAD_DIR, exist_ok=True)

def create_detected_panoramic(db: Session, id_panoramic_image: int, detection_result: dict, detected_file, crop_file):
    # Simpan file hasil deteksi
    detected_file_path = f"{DETECTED_UPLOAD_DIR}/{detected_file.filename}"
    crop_file_path = f"{DETECTED_UPLOAD_DIR}/{crop_file.filename}"

    with open(detected_file_path, "wb") as buffer:
        shutil.copyfileobj(detected_file.file, buffer)

    with open(crop_file_path, "wb") as buffer:
        shutil.copyfileobj(crop_file.file, buffer)

    # Simpan ke database
    db_detected = models.DetectedPanoramic(
        id_panoramic_image=id_panoramic_image,
        detected_image_url=detected_file_path,
        detected_crop_image_url=crop_file_path,
        detection_result=detection_result
    )

    db.add(db_detected)
    db.commit()
    db.refresh(db_detected)
    return db_detected

def get_detected_panoramic(db: Session, detected_id: int):
    return db.query(models.DetectedPanoramic).filter(models.DetectedPanoramic.id == detected_id).first()

def get_detected_panoramics_by_panoramic_id(db: Session, panoramic_id: int):
    return db.query(models.DetectedPanoramic).filter(models.DetectedPanoramic.id_panoramic_image == panoramic_id).all()

def delete_detected_panoramic(db: Session, detected_id: int):
    db_detected = db.query(models.DetectedPanoramic).filter(models.DetectedPanoramic.id == detected_id).first()
    
    if db_detected:
        db.delete(db_detected)
        db.commit()
    
    return db_detected