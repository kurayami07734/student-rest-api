from pydantic import BaseModel


class Address(BaseModel):
    city: str
    country: str


class CreateStudentRequestBody(BaseModel):
    name: str
    age: int
    address: Address


class CreateStudentResponseBody(BaseModel):
    id: str
