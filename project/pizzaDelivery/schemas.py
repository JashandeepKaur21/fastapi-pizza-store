from typing import Optional,List
from pydantic import BaseModel

class AddToCart(BaseModel):
    pizza_id:int
    qty:int
    customer_id:int

class CustomerDetail(BaseModel):
    name: str
    address:str
    emailId:str
    password: str
    mobile :int
    role: str

class AdminDetails(BaseModel):
    emailId:str
    password:str

class DisplayAdmin(BaseModel):
    emailId:str
    class Config:
        orm_mode=True

class DisplayCustomer(BaseModel):
    name: str
    address:str
    emailId:str
    mobile :int
    role: str
    class Config:
        orm_mode=True

class PizzaDetails(BaseModel):
    name:str
    description:str
    price:int
    qty:int
    availability:bool
   # customer_id:int

class CartItem(BaseModel):
    pizza_id:int
    qty:int
    cart_id:int
    price:int
    total:int



class Cart(BaseModel):
    customer_id:int
    total:int
 

class Login(BaseModel):
    username:str
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    username:Optional[str]=None