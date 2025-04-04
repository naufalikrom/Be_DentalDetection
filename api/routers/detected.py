from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import sql_query_detected
from ..schema import DetectedPanoramicResponse
from ..models import DetectedPanoramic, PanoramicImage
from typing import List

router = APIRouter(prefix="/api/v1/detected", tags=["Detected Panoramic"])

@router.put("/{no_rm}", response_model=DetectedPanoramicResponse)
def detect_teeth(no_rm: str, db: Session = Depends(get_db)):
    """Deteksi gigi dari gambar panoramic. Jika sudah ada, update data lama."""
    try:
        # Cek apakah data sudah ada
        detected = db.query(DetectedPanoramic).join(PanoramicImage).filter(PanoramicImage.no_rm == no_rm).first()

        if detected:
            db.delete(detected)
            db.commit()
        
        # Jalankan deteksi baru
        new_detected = sql_query_detected.detect_and_store(db, no_rm)

        return DetectedPanoramicResponse(
            id=new_detected.id,
            id_panoramic_image=new_detected.id_panoramic_image,
            detected_image_url=new_detected.detected_image_url,
            result_detection_images=new_detected.result_detection_images
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/{no_rm}", response_model=List[DetectedPanoramicResponse])
def get_detected_images(no_rm: str, db: Session = Depends(get_db)):
    detected = db.query(DetectedPanoramic).join(PanoramicImage).filter(PanoramicImage.no_rm == no_rm).all()
    
    if not detected:
        raise HTTPException(status_code=404, detail="Detected images not found")

    return [
        DetectedPanoramicResponse(
            id=d.id,
            id_panoramic_image=d.id_panoramic_image,
            detected_image_url=d.detected_image_url,
            result_detection_images=d.result_detection_images
        ) for d in detected
    ]


