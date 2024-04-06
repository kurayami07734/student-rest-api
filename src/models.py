from typing import Optional, TypedDict
from pydantic import BaseModel


class MongoAddress(TypedDict):
    city: str
    country: str


class MongoStudent(TypedDict):
    _id: str
    name: str
    age: int
    address: MongoAddress


class Address(BaseModel):
    city: str
    country: str


class AddressOptional(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None


class Student(BaseModel):
    name: str
    age: int
    address: Address


class StudentOptional(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[AddressOptional] = None
