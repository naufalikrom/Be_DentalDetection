import shutil
import os
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .. import models, schema

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_panoramic_images(db: Session, id_user: int, page: int = 1, limit: int = 6):
    offset = (page - 1) * limit
    return (
        db.query(models.PanoramicImage)
        .filter(models.PanoramicImage.id_user == id_user) 
        .offset(offset)
        .limit(limit)
        .all()
    )

def get_panoramic_image_by_no_rm(db: Session, no_rm: str):
    return db.query(models.PanoramicImage).filter(models.PanoramicImage.no_rm == no_rm).first()


def create_panoramic_image(db: Session, id_user: int, no_rm: str, file):

    existing_panoramic = db.query(models.PanoramicImage).filter(models.PanoramicImage.no_rm == no_rm).first()
    if existing_panoramic:
        raise HTTPException(status_code=400, detail="no_rm already exists")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_panoramic = models.PanoramicImage(id_user=id_user, no_rm=no_rm, image_url=file_path)
    db.add(db_panoramic)
    db.commit()
    db.refresh(db_panoramic)

    return db_panoramic

def update_panoramic_image(db: Session, no_rm: str, image_url: str):
    db_panoramic = db.query(models.PanoramicImage).filter(models.PanoramicImage.no_rm == no_rm).first()

    if db_panoramic is None:
        return None  # Jika `no_rm` tidak ditemukan, kembalikan None
    
    # Update hanya `image_url`, `no_rm` tetap tidak berubah
    db_panoramic.image_url = image_url

    db.commit()
    db.refresh(db_panoramic)

    return db_panoramic

def delete_panoramic_image(db: Session, no_rm: str):
    db_panoramic = db.query(models.PanoramicImage).filter(models.PanoramicImage.no_rm == no_rm).first()
    if db_panoramic:
        db.delete(db_panoramic)
        db.commit()
    return db_panoramic
