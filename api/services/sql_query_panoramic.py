import shutil
import os
from sqlalchemy.orm import Session
from .. import models, schema

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_panoramic_images(db: Session, page: int = 1, limit: int = 6):
    offset = (page - 1) * limit
    return db.query(models.PanoramicImage).offset(offset).limit(limit).all()

def get_panoramic_image_by_id(db: Session, image_id: int):
    return db.query(models.PanoramicImage).filter(models.PanoramicImage.id == image_id).first()

def create_panoramic_image(db: Session, id_user: int, no_rm: str, file):
    # Simpan file gambar
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Simpan data ke database
    db_panoramic = models.PanoramicImage(id_user=id_user, no_rm=no_rm, image_url=file_path)
    db.add(db_panoramic)
    db.commit()
    db.refresh(db_panoramic)
    return db_panoramic

def update_panoramic_image(db: Session, image_id: int, panoramic_update: schema.PanoramicImageUpdate):
    db_panoramic = db.query(models.PanoramicImage).filter(models.PanoramicImage.id == image_id).first()
    
    if db_panoramic:
        update_data = panoramic_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_panoramic, key, value)
        
        db.commit()
        db.refresh(db_panoramic)

    return db_panoramic

def delete_panoramic_image(db: Session, image_id: int):
    db_panoramic = db.query(models.PanoramicImage).filter(models.PanoramicImage.id == image_id).first()
    if db_panoramic:
        db.delete(db_panoramic)
        db.commit()
    return db_panoramic
