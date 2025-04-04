from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from typing import Optional, List, Dict, Any


class UserBase(BaseModel):
    email: EmailStr = Field(..., title="user email address", example="example@gmail.com")
    username: str = Field(..., title="Username", example="Dental")
    
    
class UserCreate(UserBase): #user create requrest data type
    password: str = Field(..., title="user password", example="someStrongPassword")
    

class User(UserBase): #reesponse data type
    id: int
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True
        

class OTPData(BaseModel):
    user_id:int
    code: Optional[str] = None
    
    class Config:
        from_attributes = True
        
class OneTimePassword(BaseModel):
    code: str





class PanoramicImageCreate(BaseModel):
    id_user: int
    no_rm: str
    name_patient: str

class PanoramicImageUpdate(BaseModel):
    no_rm: Optional[str] = None
    name_patient: Optional[str] = None
    image_url: Optional[str] = None

class PanoramicImageResponse(BaseModel):
    id: int
    id_user: int
    no_rm: str
    name_patient: str
    image_url: str

    class Config:
        from_attributes = True



class CroppedImage(BaseModel):
    cropped_image_url: str
    cropped_squared_image_url: str
    detection_desease_result: Optional[str]  # Bisa bernilai None jika tidak ada hasil deteksi penyakit

# class DetectedPanoramicResponse(BaseModel):
#     id: int
#     id_panoramic_image: int
#     detected_image_url: str
#     result_detection_images: Dict[str, CroppedImage]  # Mengubah detection_result menjadi struktur yang lebih jelas

class DetectedPanoramicResponse(BaseModel):
    id: Optional[int] = None
    id_panoramic_image: Optional[int] = None
    detected_image_url: str
    result_detection_images: Dict[str, CroppedImage]

    class Config:
        from_attributes = True
