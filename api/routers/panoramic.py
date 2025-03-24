import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schema
from ..services import sql_query_panoramic
from typing import List
import shutil
from fastapi import Request

router = APIRouter(prefix="/api/v1/panoramic", tags=["Panoramic Images"])

@router.get("/", response_model=List[schema.PanoramicImageResponse])
def read_panoramic_images(
    id_user: int, 
    page: int = 1,
    limit: int = 6,
    db: Session = Depends(get_db)
):
    return sql_query_panoramic.get_panoramic_images(db, id_user=id_user, page=page, limit=limit)

# @router.get("/{no_rm}", response_model=schema.PanoramicImageResponse)
# def read_panoramic_image(no_rm: str, db: Session = Depends(get_db)):
#     image = sql_query_panoramic.get_panoramic_image_by_no_rm(db, no_rm)
#     if image is None:
#         raise HTTPException(status_code=404, detail="Image not found")
#     return image

@router.get("/{no_rm}", response_model=schema.PanoramicImageResponse)
def read_panoramic_image(no_rm: str, request: Request, db: Session = Depends(get_db)):
    image = sql_query_panoramic.get_panoramic_image_by_no_rm(db, no_rm)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    # Buat URL lengkap
    base_url = str(request.base_url)  # Ambil base URL dari request
    image_url = f"{base_url}{image.image_url}"  # Gabungkan dengan path gambar

    return {
        "id": image.id,
        "id_user": image.id_user,
        "no_rm": image.no_rm,
        "image_url": image_url
    }


@router.post("/", response_model=schema.PanoramicImageResponse)
def create_panoramic(
    id_user: int = Form(...), 
    no_rm: str = Form(...), 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    return sql_query_panoramic.create_panoramic_image(db, id_user, no_rm, file)

@router.put("/{no_rm}", response_model=schema.PanoramicImageResponse)
def update_panoramic(
    no_rm: str,  # no_rm sebagai patokan
    file: UploadFile = File(...),  # Gambar wajib diunggah
    db: Session = Depends(get_db)
):
    upload_folder = "uploads/"
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Panggil fungsi update berdasarkan no_rm
    updated_image = sql_query_panoramic.update_panoramic_image(db, no_rm, file_path)

    if updated_image is None:
        raise HTTPException(status_code=404, detail="Panoramic image not found")

    return updated_image

@router.delete("/{no_rm}")
def delete_panoramic(no_rm: str, db: Session = Depends(get_db)):
    deleted_image = sql_query_panoramic.delete_panoramic_image(db, no_rm)
    if deleted_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}
