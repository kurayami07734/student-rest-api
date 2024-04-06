from dotenv import load_dotenv
from os import getenv
from contextlib import asynccontextmanager
from bson.objectid import ObjectId


from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection

from src.models import Student, StudentOptional

student_collection: Collection = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    global student_collection
    client = MongoClient(getenv("ATLAS_CONNECTION_URL"))
    student_collection = client["Cluster0"].students
    yield
    student_collection = None
    client.close()


app = FastAPI(title="Student REST API", lifespan=lifespan)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.post("/students", status_code=201)
async def create_student(
    request_body: Student,
):
    new_student = student_collection.insert_one(request_body.model_dump())
    return {"id": str(new_student.inserted_id)}


@app.get("/students")
async def all_students(country: str | None = None, age: int = 0):
    all_students = list(student_collection.find())
    if country is not None:
        all_students = [s for s in all_students if s["address"]["country"] == country]
    all_students = [
        {"name": s["name"], "age": s["age"]} for s in all_students if s["age"] >= age
    ]
    return {"data": all_students}


@app.get("/students/{id}")
def student_by_id(id: str):
    student = student_collection.find_one(ObjectId(id))

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    del student["_id"]  # remove id field because is not getting encoded
    return student


@app.patch("/students/{id}", status_code=204)
async def update_student(id: str, request_body: StudentOptional):
    student = student_collection.find_one(ObjectId(id))
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
    student = student_collection.find_one(ObjectId(id))
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    student_collection.delete_one(filter={"_id": ObjectId(id)})
