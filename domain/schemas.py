
from fastapi import Form, File, UploadFile
from pydantic import BaseModel


# https://stackoverflow.com/a/60670614
class AppForm(BaseModel):
    name: str
    description: str
    logo: UploadFile
    app_file: UploadFile
    language: str

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: str = Form(...),
        logo: UploadFile = File(...),
        app_file: UploadFile = File(...),
        language: str = Form(...)
    ):
        return cls(
            name=name,
            description=description,
            logo=logo,
            app_file=app_file,
            language=language
        )