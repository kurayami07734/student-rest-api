from typing import Optional
from pydantic import BaseModel


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
