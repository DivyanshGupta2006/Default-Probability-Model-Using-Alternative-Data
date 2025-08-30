# In: src/interface/app.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Make sure all your new routers are imported
from src.interface.routers import prediction_router, tracking_router, about_router

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
# ============================

@app.get("/")
def read_root():
    return {"message": "Welcome to the Finshield API. Go to /docs for documentation."}