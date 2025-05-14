from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from code_runner_backend.routes import run_code
from code_runner_backend.logs import logger_instance
import os

app = FastAPI(
    title="Code Runner API",
    description="An API service for running code",
    version="1.0.0"
)

# Get the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create static files and templates directories
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Set up templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(run_code.router)

logger_instance.info("✅ App initialized.")
