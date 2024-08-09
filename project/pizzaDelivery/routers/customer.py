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

@router.get('/menuOfStore',response_model=List[schemas.PizzaDetails])
def get_listed_pizzas(db:Session = Depends(get_db)):
    pizza_list=db.query(models.Pizza).all()
    return pizza_list

# Add pizza to cart
@router.post('/addToCart/{id}', status_code=status.HTTP_201_CREATED)
def add_to_cart(id,request: schemas.Cart, db: Session = Depends(get_db)):
    pizzaDb=db.query(models.Pizza).filter(models.Pizza.id == id)
    pizza = pizzaDb.first()
    if not pizza:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pizza Not Found")
    
    # Check if the pizza is available
    if pizza.qty < request.total:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough pizza available")
    
    if request.total<1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Item Added")
    

    customer = db.query(models.Customer).filter(models.Customer.id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer Not Found")
    cartDb=db.query(models.Cart).filter(models.Cart.customer_id == request.customer_id)
    cart = cartDb.first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart Not Found")
    
    
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
    return {'Items Added Successfully'}  

# Remove pizza from cart
@router.post('/removeFromCart/{id}', status_code=status.HTTP_200_OK)
def remove_from_cart(id, request: schemas.Cart, db: Session = Depends(get_db)):
    pizzaDb = db.query(models.Pizza).filter(models.Pizza.id == id)
    pizza = pizzaDb.first()
    if not pizza:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pizza not found")

    customer = db.query(models.Customer).filter(models.Customer.id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    cartDb = db.query(models.Cart).filter(models.Cart.customer_id == request.customer_id)
    cart = cartDb.first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
     
    if request.total<1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Item Removed")
   

    cartItemDb = db.query(models.CartItems).filter(models.CartItems.cart_id == cart.id, models.CartItems.pizza_id == id)
    cartItem = cartItemDb.first()
    if not cartItem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart")

    if cartItem.qty < request.total:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove more items than are in the cart")

    # Update cart total and pizza quantity
    total_amount = db.query(func.sum(models.CartItems.total)).filter(models.CartItems.cart_id == cart.id).first()[0]
    if not total_amount:
        total_amount = 0
    total_amount -= pizza.price * request.total

    pizzaDb.update({'qty': pizza.qty + request.total})

    if cartItem.qty == request.total:
        db.delete(cartItem)  # Remove the cart item completely if all quantities are removed
    else:
        cartItemDb.update({'qty': cartItem.qty - request.total, 'total': cartItem.total - (pizza.price * request.total)})

    cartDb.update({'total': total_amount})
    db.commit()

    return {'Items removed'}

# Clear the cart
@router.post('/clearCart', status_code=status.HTTP_200_OK)
def clear_cart(request: schemas.Cart, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    cartDb = db.query(models.Cart).filter(models.Cart.customer_id == request.customer_id)
    cart = cartDb.first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    
    cartItems = db.query(models.CartItems).filter(models.CartItems.cart_id == cart.id).all()
    if not cartItems:
        return {'message': 'Cart is already empty'}

    # Restore the quantities of pizzas in stock
    for item in cartItems:
        pizzaDb = db.query(models.Pizza).filter(models.Pizza.id == item.pizza_id)
        pizza = pizzaDb.first()
        if pizza:
            pizzaDb.update({'qty': pizza.qty + item.qty})
    
    # Clear the cart
    db.query(models.CartItems).filter(models.CartItems.cart_id == cart.id).delete()
    cartDb.update({'total': 0})
    db.commit()

    return {'message': 'Cart cleared successfully'}

 