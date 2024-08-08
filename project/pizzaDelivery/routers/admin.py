from fastapi import APIRouter,HTTPException,status
from typing import List
from passlib.context import CryptContext

from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..database import get_db
from ..import schemas
from ..import models


router= APIRouter(
    tags=['Admin']
)
pwd_context = CryptContext(schemes=["bcrypt"],deprecated ="auto")

#Adding admin details
@router.post('/createAdmin', status_code=status.HTTP_201_CREATED,response_model=schemas.DisplayAdmin)
def post_user_details(request:schemas.AdminDetails,db:Session = Depends(get_db)):
    hashedPassword=pwd_context.hash(request.password)
    admin_user= models.Admin(emailId=request.emailId, password=hashedPassword)
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user
