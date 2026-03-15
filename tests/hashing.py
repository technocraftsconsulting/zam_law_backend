from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print(pwd_context.hash("Password@1234"))
print(pwd_context.verify("Password@1234", pwd_context.hash("Password@1234")))