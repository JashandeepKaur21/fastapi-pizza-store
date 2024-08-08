from fastapi import APIRouter,HTTPException,status,Response
from pizzaDelivery.routers.login import get_current_user
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..import schemas
from ..import models
from fastapi import APIRouter
from typing import List


router=APIRouter(
    tags=['Pizza']
    
)

@router.delete('/pizza/{id}')
def deletePizza(id,db:Session = Depends(get_db),current_user: schemas.AdminDetails=Depends(get_current_user)):
    db.query(models.Pizza).filter(models.Pizza.id == id).delete(synchronize_session=False)
    db.commit()
    return {'Pizza deleted'}


@router.get('/pizzaList',response_model=List[schemas.PizzaDetails])
def get_listed_pizzas(db:Session = Depends(get_db),current_user: schemas.AdminDetails=Depends(get_current_user)):
    pizza_list=db.query(models.Pizza).all()
    return pizza_list


@router.put('/pizza/{id}')
def updateProduct(id,request: schemas.PizzaDetails,db:Session = Depends(get_db),current_user: schemas.AdminDetails=Depends(get_current_user)):
    product = db.query(models.Pizza).filter(models.Pizza.id == id)
    if not product.first():
        pass
    product.update(request.model_dump())
    db.commit()
    return {'Successfully updated record':product}

@router.post('/addPizza')
def add_pizza(request: schemas.PizzaDetails,db:Session = Depends(get_db),current_user: schemas.AdminDetails=Depends(get_current_user)):
    new_pizza = models.Pizza(name=request.name,description=request.description,price=request.price,qty=request.qty,availability=request.availability)
    db.add(new_pizza)
    db.commit()
    db.refresh(new_pizza)
    return request

