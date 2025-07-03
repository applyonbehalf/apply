# auth/jwt_handler.py - Fixed version using PyJWT instead of python-jose
from datetime import datetime, timedelta
from typing import Optional
import jwt  # This is PyJWT
from passlib.context import CryptContext
from config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JWTHandler:
    """Handles JWT token creation and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a new access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_secret, 
            algorithm=settings.jwt_algorithm
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """Verify a token and return user_id if valid"""
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret, 
                algorithms=[settings.jwt_algorithm]
            )
            user_id: str = payload.get("sub")
            
            if user_id is None:
                return None
                
            return user_id
            
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid token")
            return None
        except Exception as e:
            print(f"Token verification error: {e}")
            return None
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode a token and return the payload"""
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret, 
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid token")
            return None
        except Exception as e:
            print(f"Token decode error: {e}")
            return None