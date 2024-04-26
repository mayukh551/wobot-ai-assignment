from typing import List
from sqlalchemy.orm import Session
from . import models, schemas
import uuid
from .utils import Hasher


# ****************** USER CRUD ******************#

def get_user(db: Session, user_id: str):
    """
    Retrieve a user from the database based on the provided user_id.

    Args:
        db (Session): The database session.
        user_id (str): The ID of the user to retrieve.

    Returns:
        User: The user object if found, otherwise None.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()




def get_user_by_email(db: Session, email: str) -> schemas.User:
    """
    Retrieve a user from the database based on their email.

    Args:
        db (Session): The database session.
        email (str): The email of the user to retrieve.

    Returns:
        schemas.User: The user object retrieved from the database.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    print("Holy smokes", type(user))
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of users from the database.

    Args:
        db (Session): The database session.
        skip (int, optional): Number of records to skip. Defaults to 0.
        limit (int, optional): Maximum number of records to retrieve. Defaults to 100.

    Returns:
        List[User]: A list of User objects.
    """
    return db.query(models.User).offset(skip).limit(limit).all()




def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user in the database.

    Args:
        db (Session): The database session.
        user (UserCreate): The user data to be created.

    Returns:
        User: The created user object.
    """
    fake_hashed_password = Hasher.get_password_hash(user.password)
    db_user = models.User(
        id=str(uuid.uuid4()),
        email=user.email, password=fake_hashed_password)
    print(db_user.id, db_user.email, db_user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user





# ****************** TASK CRUD ******************#



def create_user_task(db: Session, task: schemas.TaskCreate, user_id: str) -> models.Task:
    """
    Create a new task for a user.

    Args:
        db (Session): The database session.
        task (TaskCreate): The task data to be created.
        user_id (str): The ID of the user who owns the task.

    Returns:
        Task: The created task.

    """
    task_id = str(uuid.uuid4())  # generate a unique id for every task
    db_task = models.Task(**task.model_dump(), id=task_id, owner_id=user_id)
    db.add(db_task)
    db_task.status = task.status
    db.commit()
    db.refresh(db_task)
    return db_task



def get_user_tasks(db: Session, user_id: str) -> List[models.Task]: 
    """
    Retrieve all tasks belonging to a specific user.

    Args:
        db (Session): The database session.
        user_id (str): The ID of the user.

    Returns:
        List[models.Task]: A list of tasks belonging to the user.
    """
    return db.query(models.Task).filter(models.Task.owner_id == user_id).all()




def delete_user_task(db: Session, task_id: str) -> models.Task:
    """
    Deletes a user task from the database.

    Args:
        db (Session): The database session.
        task_id (str): The ID of the task to be deleted.

    Returns:
        models.Task: The deleted task.
    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    db.delete(db_task)
    db.commit()
    return db_task




def update_user_task(db: Session, task_id: str, new_task: schemas.TaskUpdate) -> models.Task:
    """
    Update a user task in the database.

    Args:
        db (Session): The database session.
        task_id (str): The ID of the task to be updated.
        new_task (schemas.TaskUpdate): The updated task data.

    Returns:
        models.Task: The updated task object.

    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()

    # Update the task with the new values
    for field, value in new_task.dict().items():
        if value is not None:
            setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task
