from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shap

from src.interface.routers import prediction_router, tracking_router, about_router, home_router

app = FastAPI(
    title="Finshield Credit Risk API",
    description="API for predicting and explaining credit default risk."
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="src/interface/static"), name="static")
templates = Jinja2Templates(directory="src/interface/templates")

# === THIS IS THE KEY PART ===
# Ensure the router with your new endpoint is included.
app.include_router(prediction_router.router)
app.include_router(tracking_router.router)
app.include_router(about_router.router)
app.include_router(home_router.router)
# ============================

# Change your root endpoint to this
@app.get("/", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/add", response_class=HTMLResponse)
async def add_user_form(request: Request):
    return templates.TemplateResponse("add_user.html", {"request": request})

# Track User Page (serves the form)
@app.get("/track", response_class=HTMLResponse)
async def track_user_form(request: Request):
    return templates.TemplateResponse("track_user.html", {"request": request})