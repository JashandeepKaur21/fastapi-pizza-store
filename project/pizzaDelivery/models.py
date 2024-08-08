from sqlalchemy import Column, ForeignKey,String,Integer, MetaData, Boolean, DateTime
from .database import Base
from sqlalchemy.orm import relationship
import datetime


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address= Column(String)
    emailId= Column(String)
    password= Column(String)
    mobile = Column(Integer)
    role= Column(String)

class Admin(Base):
    __tablename__ = 'adminDetails'
    id = Column(Integer, primary_key=True, index=True)
    emailId= Column(String)
    password= Column(String)

class Pizza(Base):
    __tablename__ = 'pizzaTypes'
    id = Column(Integer, primary_key=True, index=True)
    name=Column(String)
    description=Column(String)
    price= Column(Integer)
    qty= Column(Integer)
    availability= Column(Boolean)
    customer_id = Column(Integer,ForeignKey('customers.id'))

class Cart(Base):
    __tablename__= 'cart'
    id = Column(Integer, primary_key=True, index=True)
    total= Column(Integer)
    customer_id=Column(Integer,ForeignKey('customers.id'))

class CartItems(Base):
    __tablename__= 'cartItems'
    id = Column(Integer, primary_key=True, index=True)
    cart_id=Column(Integer, ForeignKey('cart.id'))
    pizza_id=Column(Integer,ForeignKey('pizzaTypes.id'))
    qty=Column(Integer)
    price=Column(Integer)
    total=Column(Integer)



    






