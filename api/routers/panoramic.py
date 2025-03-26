import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import schema
from ..services import sql_query_panoramic

router = APIRouter(prefix="/api/v1/panoramic", tags=["Panoramic Images"])


@router.get("/", response_model=List[schema.PanoramicImageResponse])
def read_panoramic_images(
    request: Request, 
    id_user: int, 
    page: int = 1,
    limit: int = 6,
    db: Session = Depends(get_db)
):
    images = sql_query_panoramic.get_panoramic_images(db, id_user=id_user, page=page, limit=limit)

    base_url = request.base_url._url

    return [
        {
            "id": image.id,
            "id_user": image.id_user,
            "no_rm": image.no_rm,
            "name_patient": image.name_patient,
            "image_url": f"{base_url}{image.image_url}".replace("\\", "/")
        }
        for image in images
    ]


@router.get("/{no_rm}", response_model=schema.PanoramicImageResponse)
def read_panoramic_image(no_rm: str, request: Request, db: Session = Depends(get_db)):
    image = sql_query_panoramic.get_panoramic_image_by_no_rm(db, no_rm)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    base_url = str(request.base_url)  
    image_url = f"{base_url}{image.image_url}".replace("\\", "/")

    return {
        "id": image.id,
        "id_user": image.id_user,
        "no_rm": image.no_rm,
        "name_patient": image.name_patient,
        "image_url": image_url
    }


@router.post("/", response_model=schema.PanoramicImageResponse)
def create_panoramic(
    id_user: int = Form(...), 
    no_rm: str = Form(...), 
    name_patient: str = Form(...),
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    return sql_query_panoramic.create_panoramic_image(db, id_user, no_rm, name_patient, file)


@router.put("/{no_rm}", response_model=schema.PanoramicImageResponse)
def update_panoramic(
    no_rm: str,
    name_patient: str = Form(...),
    file: UploadFile = File(None),  
    db: Session = Depends(get_db)
):
    db_panoramic = sql_query_panoramic.get_panoramic_image_by_no_rm(db, no_rm)
    
    if not db_panoramic:
        raise HTTPException(status_code=404, detail="Panoramic image not found")
    
    image_url = db_panoramic.image_url  # Gunakan URL lama jika file tidak diunggah

    if file:  
        upload_folder = "uploads/"
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image_url = file_path  # Gunakan file baru jika diunggah
    
    updated_image = sql_query_panoramic.update_panoramic_image(db, no_rm, name_patient, image_url)
    return updated_image


@router.delete("/{no_rm}")
def delete_panoramic(no_rm: str, db: Session = Depends(get_db)):
    deleted_image = sql_query_panoramic.delete_panoramic_image(db, no_rm)
    if deleted_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}
