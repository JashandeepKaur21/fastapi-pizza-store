from fastapi import FastAPI
from .import models
from .database import engine
from .routers import admin, customer,cart,login,pizza

app= FastAPI(
    title="Pizza Delivery API",
    description= "Get all the details about the pizza delivery store",
  
)

app.include_router(admin.router)
app.include_router(customer.router)
app.include_router(login.router)
app.include_router(pizza.router)

models.Base.metadata.create_all(engine)


@app.get('/')
def index():
    return 'Welcome to pizza store'




