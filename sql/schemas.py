from pydantic import BaseModel, EmailStr
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# Task Schema
class TaskBase(BaseModel):
    name: str
    description: str | None = None
    due_date: str | None = None
    status: Status = Status.PENDING


class TaskUpdate(TaskBase):
    name: str | None = None
    description: str | None = None
    due_date: str | None = None
    status: Status | None = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: str
    owner_id: str

    class Config:
        from_attributes = True


# User schemas

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: str
    tasks: list[Task] = []

    class Config:
        from_attributes = True
