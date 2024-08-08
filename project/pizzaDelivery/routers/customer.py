from typing import List
from fastapi import APIRouter,HTTPException,status
from passlib.context import CryptContext
from sqlalchemy import func
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..import schemas
from ..import models

router=APIRouter(
    tags=['Customer']
)
pwd_context = CryptContext(schemes=["bcrypt"],deprecated ="auto")

#Adding users details
@router.post('/createUser', status_code=status.HTTP_201_CREATED,response_model=schemas.DisplayCustomer)
def post_user_details(request:schemas.CustomerDetail,db:Session = Depends(get_db)):
    hashedPassword=pwd_context.hash(request.password)

    user= models.Customer(name=request.name,address=request.address,emailId=request.emailId, password=hashedPassword,mobile=request.mobile,role=request.role)
    db.add(user)
    db.commit()
    db.refresh(user)

    user_fetch=db.query(models.Customer).filter(models.Customer.emailId == request.emailId).first()
    cart=models.Cart(total=0,customer_id=user_fetch.id)
    db.add(cart)
    db.commit()
    db.refresh(cart)

    return user_fetch

#Updating users details
@router.put('/updateUserDetails/{emailId}', status_code=status.HTTP_201_CREATED,response_model=schemas.DisplayCustomer)
def update_user_details(emailId,request:schemas.CustomerDetail,db:Session = Depends(get_db)):
    user = db.query(models.Customer).filter(models.Customer.emailId == emailId)
    if not user.first():
        pass
    user.update(request.model_dump())
    db.commit()
    return {'user details updated'}

@router.get('/menuOfStore',response_model=List[schemas.PizzaDetails])
def get_listed_pizzas(db:Session = Depends(get_db)):
    pizza_list=db.query(models.Pizza).all()
    return pizza_list

#Adding pizza to cart
@router.post('/addToCart/{id}', status_code=status.HTTP_201_CREATED)
def add_to_cart(id,request: schemas.Cart, db: Session = Depends(get_db)):
    pizzaDb=db.query(models.Pizza).filter(models.Pizza.id == id)
    pizza = pizzaDb.first()
    if not pizza:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pizza not found")
    
    # Check if the pizza is available
    if pizza.qty < request.total:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough pizza available")
    
    customer = db.query(models.Customer).filter(models.Customer.id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    cartDb=db.query(models.Cart).filter(models.Cart.customer_id == request.customer_id)
    cart = cartDb.first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    
    
    total_amount = db.query(func.sum(models.CartItems.total)).filter(models.CartItems.cart_id == cart.id).first()[0]
    if not total_amount:
        total_amount=0
    total_amount += pizza.price * request.total

    cartItem=models.CartItems(total=pizza.price * request.total,qty=request.total,pizza_id=id,price=pizza.price,cart_id=cart.id)
    db.add(cartItem)

    cartDb.update({'total':total_amount})
    pizzaDb.update({'qty':pizza.qty-request.total})
    db.commit()
    db.refresh(cartItem)


    return {'Items added'}  

    