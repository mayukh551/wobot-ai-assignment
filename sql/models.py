from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base
from uuid import uuid4
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=str(uuid4()))
    email = Column(String, unique=True, index=True)
    password = Column(String)

    tasks = relationship("Task", back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=str(uuid4()))
    name = Column(String)
    created_at = Column(String, default=datetime.now().isoformat())
    due_date = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, default="pending")
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="tasks")
