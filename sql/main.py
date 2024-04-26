from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from sql import crud, models, schemas
from sql.database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from .utils import Hasher

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "SECRET_KEY")
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def jwt_required(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms="HS256")
        email: str = payload.get("email")
        print(email)
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db=SessionLocal(), email=email)

    if user is None:
        raise credentials_exception

    return user


'''
When a model attribute has a default value, it is not required.
Otherwise, it is required. Use `None` to make it just optional.
'''
verifyUser = Depends(jwt_required)


# ****************** AUTH ROUTES ******************#

@app.post("/users/register")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)) -> dict:
    print(user)
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db=db, user=user)
    print(user)
    token = create_access_token(data={"email": user.email, "id": user.id})
    print(token)
    return {"access_token": token}


@app.post("/users/login")
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)) -> dict:
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user is None or not Hasher.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(
        data={"email": db_user.email, "id": db_user.id})
    return {"access_token": token}


# ****************** USER ROUTES ******************#


@ app.get("/users", response_model=list[schemas.User], dependencies=[verifyUser])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@ app.get("/users/{user_id}", response_model=schemas.User, dependencies=[verifyUser])
def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# ****************** TASK ROUTES ******************#

@ app.post("/tasks/{user_id}", response_model=schemas.Task, dependencies=[verifyUser])
def create_task_for_user(
    user_id: str, task: schemas.TaskCreate, db: Session = Depends(get_db)
):
    return crud.create_user_task(db=db, task=task, user_id=user_id)


@ app.get("/tasks/{user_id}", response_model=list[schemas.Task], dependencies=[verifyUser])
def read_tasks(user_id: str, db: Session = Depends(get_db)):
    tasks = crud.get_user_tasks(db, user_id)
    return tasks


@ app.delete("/tasks/{task_id}", dependencies=[verifyUser])
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = crud.delete_user_task(db, task_id)
    return task


@ app.put("/tasks/{task_id}", dependencies=[verifyUser])
def update_task(task_id: str, new_task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = crud.update_user_task(db, task_id, new_task=new_task)
    return task
