from passlib.context import CryptContext

passlib = CryptContext(schemes=["bcrypt"], deprecated="auto")
