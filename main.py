import datetime, uuid
from fastapi import FastAPI
from typing import List
import databases, sqlalchemy
from pydantic import BaseModel, Field


app = FastAPI(
    
)


## Подключение базы данных и создание таблицы на PostgreSQL
DATABASE_URL = "postgresql://postgres:12345678@localhost:5432/test"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

stydents = sqlalchemy.Table(
    "py_stydent",
    metadata,
    sqlalchemy.Column("id"        , sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name" , sqlalchemy.String),
    sqlalchemy.Column("gender"    , sqlalchemy.CHAR  ),
    sqlalchemy.Column("Date_of_birth" , sqlalchemy.String)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


## Создание моделей и заполнение их данными для примера
class StydentList(BaseModel):
    id            : str
    first_name    : str
    last_name     : str
    gender        : str
    Date_of_birth : str
class StydentEntry(BaseModel):
    first_name    : str = Field(..., example="Egor")
    last_name     : str = Field(..., example="Kadurin")
    gender        : str = Field(..., example="M")
    Date_of_birth : str = Field(..., example="29.07.2003")
class StydentUpdate(BaseModel):
    id            : str = Field(..., example="Enter your id")
    first_name    : str = Field(..., example="Черемисин")
    last_name     : str = Field(..., example="Андрей")
    gender        : str = Field(..., example="M")
    Date_of_birth : str = Field(..., example="29.07.1990")
class StydentDelete(BaseModel):
    id: str = Field(..., example="Введите сюда id")



#Функиця для нахождения всех студентов
@app.get("/stydents", response_model=List[StydentList], tags=["Поиск"])
async def find_all_stydent():
    query = stydents.select()
    return await database.fetch_all(query)

#Функиця для Создания студента
@app.post("/stydents", response_model=StydentList, tags=["Система управления"])
async def register_stydent(stydent: StydentEntry):
    gID   = str(uuid.uuid1())
    query = stydents.insert().values(
        id = gID,
        first_name = stydent.first_name,
        last_name  = stydent.last_name,
        gender     = stydent.gender,
        Date_of_birth = stydent.Date_of_birth,
    ) 

    await database.execute(query)
    return {
        "id": gID,
        **stydent.dict(),
    }

#Функиця для нахождения студента по id
@app.get("/stydents/{stydentId}", response_model=StydentList, tags=["Поиск"])
async def find_sydent_by_id(stydentId: str):
    query = stydents.select().where(stydents.c.id == stydentId)
    return await database.fetch_one(query)

#Функиця для изменения информации о студенте
@app.put("/stydents", response_model=StydentList, tags=["Система управления"])
async def update_user(stydent: StydentUpdate):
    gID   = str(uuid.uuid1())
    query = stydents.update().\
        where(stydents.c.id == stydent.id).\
        values(
            id = gID,
            first_name = stydent.first_name,
            last_name  = stydent.last_name,
            gender     = stydent.gender,
            Date_of_birth = stydent.Date_of_birth,
        )
    await database.execute(query)

    return await find_sydent_by_id(stydent.id)

#Функиця для удаления стуждента
@app.delete("/stydents/{stydentsId}", tags=["Система управления"])
async def delete_stydent(stydent: StydentDelete):
    query = stydents.delete().where(stydents.c.id == stydent.id)
    await database.execute(query)

    return {
        "status" : True,
        "message": "Этот студент успешно удален"
    }
