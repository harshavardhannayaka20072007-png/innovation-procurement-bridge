from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
import pymysql
import bcrypt
import jwt
from datetime import datetime, timedelta
from config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_db():
    connection = pymysql.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        port=settings.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        yield connection
    finally:
        connection.close()

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: RegisterSchema, db=Depends(get_db)):
    if user_data.role not in ['government', 'startup', 'evaluator']:
        raise HTTPException(status_code=400, detail="Invalid user role")

    with db.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE email = %s", (user_data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pw = hash_password(user_data.password)
        sql = "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (user_data.name, user_data.email, hashed_pw, user_data.role))
        db.commit()

    return {"message": "User registered successfully"}

@router.post("/login")
def login(credentials: LoginSchema, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s", (credentials.email,))
        user = cursor.fetchone()

        if not user or not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token_payload = {
            "sub": str(user["id"]),
            "role": user["role"],
            "name": user["name"]
        }
        token = create_access_token(token_payload)

        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user["role"],
            "name": user["name"],
            "user_id": user["id"]
        }