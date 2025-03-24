import sqlalchemy as sql
from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from datetime import datetime, timedelta, timezone

class User(Base):
    __tablename__ = "users"
    id = sql.Column(sql.Integer, autoincrement=True, primary_key=True, index=True)
    email = sql.Column(sql.String(255), unique=True, index=True)
    password = sql.Column(sql.String, nullable=False)
    username = sql.Column(sql.String, nullable=False)
    is_active = sql.Column(sql.Boolean(), default=True)
    is_verified = sql.Column(sql.Boolean(), default=False)
    date_joined = sql.Column(sql.TIMESTAMP(timezone=True), server_default=text('now()'))
    
    # Relationship
    panoramic_images = relationship("PanoramicImage", back_populates="user", cascade="all, delete-orphan")
    
class UserOneTimePassword(Base):
    __tablename__ = "user_one_time_passwords"
    id = sql.Column(sql.Integer, autoincrement=True, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id', ondelete='CASCADE'))
    code = sql.Column(sql.String(6), unique=True, nullable=False)
    is_valid = sql.Column(sql.Boolean(), default=True)
    created_at = sql.Column(sql.DateTime, default=datetime.now, nullable=False)
    

    
class PanoramicImage(Base):
    __tablename__ = "panoramic_images"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True, index=True)
    id_user = sql.Column(sql.Integer, sql.ForeignKey("users.id", ondelete="CASCADE"))
    no_rm = sql.Column(sql.String, unique=True, nullable=False)
    image_url = sql.Column(sql.String, nullable=False)  # Path file gambar
    created_at = sql.Column(sql.DateTime, default=datetime.now, nullable=False)

    user = relationship("User", back_populates="panoramic_images")
    detected_panoramics = relationship("DetectedPanoramic", back_populates="panoramic_image", cascade="all, delete-orphan")


class DetectedPanoramic(Base):
    __tablename__ = "detected_panoramics"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True, index=True)
    id_panoramic_image = sql.Column(sql.Integer, sql.ForeignKey("panoramic_images.id", ondelete="CASCADE"))
    detected_image_url = sql.Column(sql.String, nullable=False)  # Path gambar hasil deteksi
    detected_crop_image_url = sql.Column(sql.String, nullable=False)  # Path gambar hasil crop
    detection_result = sql.Column(sql.JSON, nullable=False)  # Data JSON hasil deteksi
    created_at = sql.Column(sql.DateTime, default=datetime.now, nullable=False)

    # Relasi dengan PanoramicImage
    panoramic_image = relationship("PanoramicImage", back_populates="detected_panoramics")
