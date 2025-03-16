from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr = Field(..., title="user email address", example="example@gmail.com")
    
    
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