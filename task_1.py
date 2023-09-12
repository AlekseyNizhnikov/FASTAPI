import databases
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKeyConstraint
from pathlib import Path
from typing import List

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

DATABASE_URL = "sqlite:///my_database.db"
database = databases.Database(DATABASE_URL)
metadata = MetaData()

users = Table("users", metadata,
              Column("id", Integer, primary_key=True),
              Column("name", String(32)),
              Column("email", String(128)),
              Column("password", String(32)))

products = Table("products", metadata,
                 Column("id", Integer, primary_key=True),
                 Column("product_name", String(128)),
                 Column("price", Integer))

orders = Table("orders", metadata,
               Column("id", Integer, primary_key=True),
               Column("user_id", Integer),
               Column("product_id", Integer),
               Column("status", String(32)),
               ForeignKeyConstraint(["user_id"], ['users.id']),
               ForeignKeyConstraint(["product_id"], ['products.id']))

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

app = FastAPI()


class UserIn(BaseModel):
    name: str = Field(max_length=32)
    email: str = Field(max_length=128)
    password: str = Field(max_length=64)


class ProductIn(BaseModel):
    product_name: str = Field(max_length=32)
    price: int


class OrderIn(BaseModel):
    user_id: int
    product_id: int
    status: str = Field(max_length=32)


class Users(BaseModel):
    id: int
    name: str = Field(max_length=32)
    email: str = Field(max_length=50)
    password: str = Field(max_length=64)


class Products(BaseModel):
    id: int
    product_name: str = Field(max_length=128)
    price: int


class Orders(BaseModel):
    id: int
    user_id: int
    product_id: int
    status: str = Field(max_length=32)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/users/", response_model=List[Users])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get("/products/", response_model=List[Products])
async def read_products():
    query = products.select()
    return await database.fetch_all(query)


@app.get("/orders/", response_model=List[Orders])
async def read_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.get("/users/{id}/", response_model=Users)
async def get_user_id(id: int):
    query = users.select().where(users.c.id == id)
    return await database.fetch_one(query)


@app.get("/products/{id}/", response_model=Products)
async def get_product_id(id: int):
    query = products.select().where(products.c.id == id)
    return await database.fetch_one(query)


@app.get("/orders/{id}/", response_model=Orders)
async def get_order_id(id: int):
    query = orders.select().where(orders.c.id == id)
    return await database.fetch_one(query)


@app.post("/user/add", response_model=Users)
async def create_user(user: UserIn):
    query = users.insert().values(**user.dict())
    last_record_id = await  database.execute(query)
    return {**user.dict(), "id": last_record_id}


@app.post("/product/add", response_model=Products)
async def create_product(product: ProductIn):
    query = products.insert().values(**product.dict())
    last_record_id = await  database.execute(query)
    return {**product.dict(), "id": last_record_id}


@app.post("/orders/add", response_model=Orders)
async def create_product(order: OrderIn):
    query = orders.insert().values(**order.dict())
    last_record_id = await  database.execute(query)
    return {**order.dict(), "id": last_record_id}


@app.put("/user/update/{id}", response_model=Users)
async def update_user(user: UserIn, id: int):
    query = users.update().where(users.c.id == id).values(**user.dict())
    await database.execute(query)
    return {**user.dict(), "id": id}


@app.put("/product/update/{id}", response_model=Users)
async def update_product(product: ProductIn, id: int):
    query = products.update().where(products.c.id == id).values(**product.dict())
    await database.execute(query)
    return {**product.dict(), "id": id}


@app.put("/order/update/{id}", response_model=Orders)
async def update_order(order: OrderIn, id: int):
    query = orders.update().where(orders.c.id == id).values(**order.dict())
    await database.execute(query)
    return {**order.dict(), "id": id}


@app.delete("/user/del/{id}")
async def delete_user(id: int):
    query = users.delete().where(users.c.id == id)
    await database.execute(query)
    return {"message": f"User {id} delete"}


@app.delete("/product/del/{id}")
async def delete_product(id: int):
    query = products.delete().where(products.c.id == id)
    await database.execute(query)
    return {"message": f"Product {id} delete"}


@app.delete("/order/del/{id}")
async def delete_order(id: int):
    query = orders.delete().where(orders.c.id == id)
    await database.execute(query)
    return {"message": f"Order {id} delete"}


if __name__ == "__main__":
    uvicorn.run(f"{Path(__file__).stem}:app", port=8001)
