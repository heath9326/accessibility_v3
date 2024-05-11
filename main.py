from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from assessement.models import InitialText

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def submit_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/")
async def post_root():
    return {"message": "Hello World from post"}

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
