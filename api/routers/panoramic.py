import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schema
from ..services import sql_query_panoramic
from typing import List
import shutil

router = APIRouter(prefix="/api/v1/panoramic", tags=["Panoramic Images"])

@router.get("/", response_model=List[schema.PanoramicImageResponse])
def read_panoramic_images(page: int = 1, limit: int = 6, db: Session = Depends(get_db)):
    return sql_query_panoramic.get_panoramic_images(db, page=page, limit=limit)

@router.get("/{image_id}", response_model=schema.PanoramicImageResponse)
def read_panoramic_image(image_id: int, db: Session = Depends(get_db)):
    image = sql_query_panoramic.get_panoramic_image_by_id(db, image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.post("/", response_model=schema.PanoramicImageResponse)
def create_panoramic(id_user: int, no_rm: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return sql_query_panoramic.create_panoramic_image(db, id_user, no_rm, file)

@router.put("/{image_id}", response_model=schema.PanoramicImageResponse)
def update_panoramic(
    image_id: int,
    no_rm: str = Form(None),  # Terima `no_rm` dalam Form Data
    file: UploadFile = File(None),  # Terima gambar opsional
    db: Session = Depends(get_db)
):
    file_path = None

    # Simpan file jika ada gambar yang diunggah
    if file:
        upload_folder = "uploads/"
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # Kirim ke service untuk update
    updated_image = sql_query_panoramic.update_panoramic_image(
        db, image_id, schema.PanoramicImageUpdate(no_rm=no_rm, image_url=file_path)
    )
    
    if updated_image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    return updated_image

@router.delete("/{image_id}")
def delete_panoramic(image_id: int, db: Session = Depends(get_db)):
    deleted_image = sql_query_panoramic.delete_panoramic_image(db, image_id)
    if deleted_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}
