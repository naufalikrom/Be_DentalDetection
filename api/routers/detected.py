from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schema
from ..services import sql_query_detected

from typing import List


router = APIRouter(prefix="/api/v1/detected", tags=["Detected Panoramic"])

@router.post("/", response_model=schema.DetectedPanoramicResponse)
def create_detected_panoramic(
    id_panoramic_image: int = Form(...),
    detection_result: str = Form(...),
    detected_file: UploadFile = File(...),
    crop_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    import json
    detection_data = json.loads(detection_result)  # Konversi string JSON ke Python dict
    
    detected_panoramic = sql_query_detected.create_detected_panoramic(
        db, id_panoramic_image, detection_data, detected_file, crop_file
    )
    
    return detected_panoramic

@router.get("/{detected_id}", response_model=schema.DetectedPanoramicResponse)
def get_detected_panoramic(detected_id: int, db: Session = Depends(get_db)):
    detected_panoramic = sql_query_detected.get_detected_panoramic(db, detected_id)
    
    if detected_panoramic is None:
        raise HTTPException(status_code=404, detail="Detected image not found")
    
    return detected_panoramic

@router.get("/by_panoramic/{panoramic_id}", response_model=List[schema.DetectedPanoramicResponse])
def get_detected_panoramics_by_panoramic_id(panoramic_id: int, db: Session = Depends(get_db)):
    return sql_query_detected.get_detected_panoramics_by_panoramic_id(db, panoramic_id)

@router.delete("/{detected_id}")
def delete_detected_panoramic(detected_id: int, db: Session = Depends(get_db)):
    deleted_panoramic = sql_query_detected.delete_detected_panoramic(db, detected_id)
    
    if deleted_panoramic is None:
        raise HTTPException(status_code=404, detail="Detected image not found")
    
    return {"message": "Detected image deleted successfully"}
