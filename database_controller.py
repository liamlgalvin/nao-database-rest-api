import operator
import os
from fastapi import FastAPI, HTTPException, status, Request, Form, File, UploadFile, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from infrastructure.dto.AppDto import AppDto
from domain.schemas import AppForm 
from sqlalchemy.orm import Session
from datetime import date

from domain.app import App

from domain import models

from domain.database import SessionLocal, engine

models.database.Base.metadata.create_all(bind=engine)


app = FastAPI()
templates = Jinja2Templates(directory="infrastructure/templates")
app.mount("/static", StaticFiles(directory="infrastructure/static"), name="static")

BASE_PATH = "/home/liam/workspace/websockets/pfg/database"
APP_FILE_PATH ="/home/liam/workspace/websockets/pfg/database/infrastructure/static/apps/"
LOGO_FILE_PATH ="/home/liam/workspace/websockets/pfg/database/infrastructure/static/appicons/"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_json_string(app_dict):
    # this should be in the database class
    temp_list = []
    static_logo_path = "/static/appicons/"

    for app in sorted(app_dict, key=operator.attrgetter('id')):
        app2 = AppDto(app.id, app.name, app.description, app.image.replace(LOGO_FILE_PATH, static_logo_path), app.location, app.language)
        temp_list.append((app2.__dict__))
    return temp_list


@app.get("/", response_class=HTMLResponse)
def root(
    request: Request,
    db: Session = Depends(get_db)
    ):

    data = db.query(models.App).all()

    return templates.TemplateResponse("index.html", {"request": request, "data" :get_json_string(data)})


@app.get("/create", response_class=HTMLResponse)
def add_app(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@app.post("/create", response_class=HTMLResponse) #status_code=status.HTTP_201_CREATED
async def create(request: Request, 
                form_data: AppForm = Depends(AppForm.as_form), 
                db: Session = Depends(get_db)):
   
    # save app logo
    app_logo_path = await save_file(form_data.logo, LOGO_FILE_PATH)

    # save app file
    app_file_path = await save_file(form_data.app_file, APP_FILE_PATH)

    # todo: move to db
    new_app = App(form_data.name, form_data.description, app_logo_path, app_file_path, form_data.language)
    
    create_app(db, new_app)

    response = RedirectResponse(url='/', 
        status_code=status.HTTP_302_FOUND)
    return response


async def save_file(file: UploadFile, file_path):

    logo_filename = file.filename

    unique_logo_path = uniquify(file_path, logo_filename)

    with open(unique_logo_path, 'wb') as out_file:
        content = await file.read() 
        out_file.write(content) 
    
    return unique_logo_path


@app.delete("/delete/{id}", status_code=status.HTTP_200_OK)
def delete(id: int, db: Session = Depends(get_db)):
    app = get_app(db, id)
    
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
   
    # delete app.logo
    if os.path.exists(app.image):
        os.remove(app.image) 
    # delete app.program
    if os.path.exists(app.location):
        os.remove(app.location) 

    delete_app(db, app)

    return {"ok": True}

def get_app(db: Session, app_id: int):
    app = db.query(models.App).filter(models.App.id == app_id).first()
    db.close()
    return app

def delete_app(db: Session, app):
    db.delete(app)
    db.commit()
    db.close()

def create_app(db: Session, app: App):
    db.add(models.App(**app.__dict__))
    db.commit()
    db.close()

def uniquify(basepath, base_filename):
    filename, extension = base_filename.split(".")
    extension = "."+extension
    counter = 1
    path = basepath + filename + extension

    while os.path.exists(path):
        path = basepath + filename + "(" + str(counter) + ")" + extension
        counter += 1

    return path


@app.get("/get-apps")
def get_all_apps(
    request: Request,
    db: Session = Depends(get_db)
    ):

    data = db.query(models.App).all()

    return data

@app.get("/get-app/{id}")
def get_app_by_id(
    request: Request,
    id: int,
    db: Session = Depends(get_db)
    ):

    data = get_app(db, id)
    print(data)
    return data