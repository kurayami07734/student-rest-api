from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.models import CreateStudentRequestBody, CreateStudentResponseBody
from src.mongo import get_student_collection

load_dotenv()

app = FastAPI(title="Student REST API")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.post("/students", status_code=201)
async def create_student(
    request_body: CreateStudentRequestBody,
) -> CreateStudentResponseBody:
    student_collection = get_student_collection()
    new_student = student_collection.insert_one(request_body.model_dump())
    return {"id": str(new_student.inserted_id)}


@app.get("/students")
async def all_students():
    pass
