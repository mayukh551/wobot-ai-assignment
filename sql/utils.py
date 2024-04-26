from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:

    '''
    Hasher class is used to hash the password and verify the password
    and the methods are static so that we can use them without creating an instance of the class
    '''

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)