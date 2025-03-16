import sqlalchemy as sql
from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

class User(Base):
    __tablename__ = "users"
    id = sql.Column(sql.Integer, autoincrement=True, primary_key=True, index=True)
    email = sql.Column(sql.String(255), unique=True, index=True)
    password = sql.Column(sql.String, nullable=False)
    is_active = sql.Column(sql.Boolean(), default=True)
    is_verified = sql.Column(sql.Boolean(), default=False)
    date_joined = sql.Column(sql.TIMESTAMP(timezone=True), server_default=text('now()'))
    
    
class UserOneTimePassword(Base):
    __tablename__ = "user_one_time_passwords"
    id = sql.Column(sql.Integer, autoincrement=True, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id', ondelete='CASCADE'))
    code = sql.Column(sql.String(6), unique=True, nullable=False)
    is_valid = sql.Column(sql.Boolean(), default=True)
