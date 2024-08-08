from datetime import timedelta,datetime
from fastapi import APIRouter, Depends,HTTPException,status
from ..import schemas,database,models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..database import get_db
from jose import jwt,JWTError
from ..schemas import TokenData
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
SECRET_KEY= "e93bc1c6dde4cf5af9a82490dadf0d07"
ALGORITHM= "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=20


router=APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"],deprecated ="auto")
oauth2_scheme= OAuth2PasswordBearer(tokenUrl="adminLogin")
oauth2_scheme_customer= OAuth2PasswordBearer(tokenUrl="customerLogin")



def generate_token(data:dict):
    to_encode=data.copy()
    expire= datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt= jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt



@router.post('/adminLogin')
def adminLogin(request:OAuth2PasswordRequestForm= Depends(),db:Session = Depends(get_db)):
    admin=db.query(models.Admin).filter(models.Admin.emailId == request.username).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Invalid user/ Username not found')
    if not pwd_context.verify(request.password,admin.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Invalid Password')
    access_token = generate_token(
        data={"sub":admin.emailId}
    )
    return {"access_token":access_token,"token_type":"bearer"}

@router.post('/customerLogin')
def customerLogin(request:OAuth2PasswordRequestForm= Depends(),db:Session = Depends(get_db)):
    customer=db.query(models.Customer).filter(models.Customer.emailId == request.username).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Invalid user/ Username not found')
    if not pwd_context.verify(request.password,customer.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Invalid Password')
    access_token= generate_token(
        data={"sub":customer.emailId}
    )
    return {"access_token":access_token,"token_type":"bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail= "Invalid auth credentials",
        headers= {'WWW-Authenticate':"Bearer"},
    )
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data= TokenData(username=username)
    except JWTError:
        raise credentials_exception

def get_current_customer(token: str = Depends(oauth2_scheme_customer)):
    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail= "Invalid auth credentials",
        headers= {'WWW-Authenticate':"Bearer"},
    )
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data= TokenData(username=username)
    except JWTError:
        raise credentials_exception
