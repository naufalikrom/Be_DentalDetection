from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks, Response
from ..database import get_db
from sqlalchemy.orm import Session
from .. import schema, sql_query, utils, models



from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import timedelta


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

@router.post('/signup', status_code=status.HTTP_201_CREATED)
async def register_user(user: schema.UserCreate, background_task: BackgroundTasks ,db: Session = Depends(get_db)):
    
    #check if email already exists
    result=sql_query.check_user_exist(db, email=user.email)
    if result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email: {user.email} already exists")
    
    #hash password
    user.password = utils.hash_password(user.password)
    
    #create a new user
    user = sql_query.insert_new_user(db, user=user)
    
    #send email confirmation
    #user email
    #otp
    otpcode = utils.generate_otp_code()
    otp_data = schema.OTPData(code=otpcode, user_id=user.id) 
    utils.send_email("verify your email", [user.email], background_task, f"your otp code is {otpcode}")

    
    sql_query.create_otp_for_user(db, otp=otp_data)
    
    return{
        "message" : "account successfully created, please verify your email with One Time Passwoord to your email address"
    }

@router.post("/email-verivication", status_code=status.HTTP_200_OK)
async def verify_email(otp:schema.OneTimePassword, response: Response, db: Session = Depends(get_db)): 
    otp_user_qs=db.query(models.UserOneTimePassword).filter(models.UserOneTimePassword.code == otp.code)
    otp_user=otp_user_qs.first()
    
    isValid = utils.verify_otp(otp.code)
    if isValid and otp_user.is_valid:
        user_qs=db.query(models.User).filter(models.User.id == otp_user.user_id)
        user = user_qs.first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invalid user")
        user_qs.update({"is_verified":True}, synchronize_session=False)
        otp_user_qs.update({"is_valid":False}, synchronize_session=False)
        db.commit()
        return{
            "message":"email successfully verified",
            "is_verified":user.is_verified
        }
    else:
        otp_user_qs.update({"is_valid":False}, synchronize_session=False)
        response.status_code=status.HTTP_400_BAD_REQUEST
        return{
            "message":"invalid otp code"
        }


@router.post('/resend_otp', status_code=status.HTTP_200_OK)
async def resend_otp(email: str, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    # Cek apakah user ada
    user = sql_query.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Cek apakah user sudah terverifikasi
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already verified")

    # Hapus OTP lama yang belum diverifikasi
    sql_query.delete_otp_by_user_id(db, user_id=user.id)

    # Generate OTP baru
    new_otp = utils.generate_otp_code()
    new_otp_data = schema.OTPData(code=new_otp, user_id=user.id)
    sql_query.create_otp_for_user(db, otp=new_otp_data)

    # Kirim ulang OTP ke email
    utils.send_email("Resend OTP Code", [user.email], background_task, f"Your new OTP code is {new_otp}")

    return {"message": "New OTP has been sent to your email"}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = sql_query.get_user_by_email(db, form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    if not utils.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = utils.create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
async def forgot_password(email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = sql_query.get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=400, detail="Email not found")

    # Generate OTP
    otp_code = utils.generate_otp_code()
    
    # Hapus OTP lama jika ada
    sql_query.delete_otp_by_user_id(db, user.id)

    # Simpan OTP baru
    otp_data = schema.OTPData(code=otp_code, user_id=user.id)
    sql_query.create_otp_for_user(db, otp=otp_data)

    # Kirim OTP ke email
    utils.send_email("Reset Password OTP", [email], background_tasks, f"Your OTP code is {otp_code}")

    return {"message": "OTP sent to your email. Use it to reset your password."}

@router.post("/reset-password")
async def reset_password(email: str, otp: str, new_password: str, db: Session = Depends(get_db)):
    user = sql_query.get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email")

    otp_entry = db.query(models.UserOneTimePassword).filter(
        models.UserOneTimePassword.user_id == user.id,
        models.UserOneTimePassword.code == otp,
        models.UserOneTimePassword.is_valid == True
    ).first()

    if not otp_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Update password
    hashed_password = utils.hash_password(new_password)
    user.password = hashed_password
    db.commit()

    # Mark OTP as used
    otp_entry.is_valid = False
    db.commit()

    return {"message": "Password successfully reset"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception
        
        user = sql_query.get_user_by_email(db, email)

        if user is None:
            raise credentials_exception
        
        return user

    except JWTError:
        raise credentials_exception
    
@router.get("/protected")
async def protected_route(current_user: models.User = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user.email}"}
