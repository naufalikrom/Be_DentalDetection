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


# class PanoramicImageBase(BaseModel):
#     id_user: int
#     no_rm: str
#     image_url: str

# class PanoramicImageCreate(PanoramicImageBase):
#     pass

# class PanoramicImageUpdate(BaseModel):
#     no_rm: Optional[str] = None
#     image_url: Optional[str] = None

# class PanoramicImageResponse(PanoramicImageBase):
#     id: int
#     created_at: datetime

#     class Config:
#         from_attributes = True




class PanoramicImageCreate(BaseModel):
    id_user: int
    no_rm: str

class PanoramicImageUpdate(BaseModel):
    no_rm: Optional[str] = None
    image_url: Optional[str] = None

class PanoramicImageResponse(BaseModel):
    id: int
    id_user: int
    no_rm: str
    image_url: str

    class Config:
        from_attributes = True



# Schema untuk menambah DetectedPanoramic
class DetectedPanoramicCreate(BaseModel):
    id_panoramic_image: int
    detection_result: Dict[str, Any]  # Hasil deteksi dalam bentuk JSON

# Schema untuk response DetectedPanoramic
class DetectedPanoramicResponse(BaseModel):
    id: int
    id_panoramic_image: int
    detected_image_url: str
    detected_crop_image_url: str
    detection_result: Dict[str, Any]

    class Config:
        from_attributes = True