from contextlib import asynccontextmanager
from bson.objectid import ObjectId
from datetime import date as dt_date
from os import getenv
from typing import Optional


from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, Response

from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection

import redis


from src.models import Address, Student, MongoStudent, StudentOptional

MAX_API_CALLS_PER_DAY = 100

student_collection: Optional[Collection[MongoStudent]] = None

redis_instance: Optional[redis.Redis] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()

    global student_collection
    global redis_instance

    redis_instance = redis.Redis(
        host="redis",
        port=6379,
        db=0,
        decode_responses=True,
        username=getenv("REDIS_USERNAME"),
    )

    client = MongoClient(getenv("ATLAS_CONNECTION_URL"))
    student_collection = client["Cluster0"].students

    if student_collection is None:
        raise HTTPException(status_code=500, detail="Could not find student collection")

    if redis_instance is None:
        raise HTTPException(status_code=500, detail="Could not connect to redis")

    yield

    student_collection = None
    redis_instance = None
    client.close()
    # redis does not need to be explicitly closed


app = FastAPI(title="Student REST API", lifespan=lifespan)


@app.middleware("http")
async def rate_limiter(req: Request, call_next):
    assert redis_instance is not None, "redis instance should not be none"
    assert req.client is not None, "client must have address"

    today = dt_date.today().strftime("%Y-%m-%d")

    res: Optional[str] = redis_instance.get(req.client.host)  # type: ignore

    response = await call_next(req)

    if res is None:
        redis_instance.set(req.client.host, f"{today}:{1}")
        return response

    date, count = res.split(":")

    count = int(count)

    if date != today:
        redis_instance.set(req.client.host, f"{today}:{1}")
    elif count <= MAX_API_CALLS_PER_DAY:
        redis_instance.set(req.client.host, f"{today}:{count + 1}")
    else:
        return Response(status_code=429, content="Too many requests today")

    return response


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.post("/students", status_code=201)
async def create_student(
    request_body: Student,
):
    assert student_collection is not None, "student collection should be none"

    student = MongoStudent(**request_body.model_dump())
    new_student = student_collection.insert_one(student)
    return {"id": str(new_student.inserted_id)}


@app.get("/students")
async def all_students(country: Optional[str] = None, age: int = 0):
    assert student_collection is not None, "student collection should be none"

    all_students = list(student_collection.find())

    if country is not None:
        all_students = [s for s in all_students if s["address"]["country"] == country]

    all_students = [
        {"name": s["name"], "age": s["age"]} for s in all_students if s["age"] >= age
    ]

    return {"data": all_students}


@app.get("/students/{id}")
def student_by_id(id: str):
    assert student_collection is not None, "student collection should be none"

    student = student_collection.find_one(filter={"_id": ObjectId(id)})

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return Student(
        name=student["name"],
        age=student["age"],
        address=Address(
            city=student["address"]["city"], country=student["address"]["country"]
        ),
    )


@app.patch("/students/{id}", status_code=204)
async def update_student(id: str, request_body: StudentOptional):
    assert student_collection is not None, "student collection should be none"

    student = student_collection.find_one(filter={"_id": ObjectId(id)})

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    fields_to_update = request_body.model_dump(exclude_none=True)

    if "address" in fields_to_update:  # deep merging address field
        fields_to_update["address"] = student["address"] | fields_to_update["address"]

    fields_to_update = student | fields_to_update

    student_collection.update_one(
        filter={"_id": ObjectId(id)}, update={"$set": fields_to_update}
    )


@app.delete("/students/{id}")
async def delete_student(id: str):
    assert student_collection is not None, "student collection should be none"

    student = student_collection.find_one(filter={"_id": ObjectId(id)})

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    student_collection.delete_one(filter={"_id": ObjectId(id)})
