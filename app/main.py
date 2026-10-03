import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.config import seed_default_configs, get_config, get_raw_initial_api_key
from app.logger import setup_logger
from app.auth import verify_session

# Import all API routers
from app.routers import auth, index, search, config, incremental, reclassify


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        seed_default_configs(db)
        cfg = get_config(db)
        setup_logger(level=cfg.log_level)
    finally:
        db.close()
    yield
    # Shutdown tasks (if any)


app = FastAPI(
    title="DeptWise Indexer & Search",
    description="Local semantic document searcher with department classification and incremental XML support.",
    version="1.0.0",
    lifespan=lifespan
)

# Session middleware
SESSION_SECRET = os.getenv("SESSION_SECRET", "deptwise-secret-key-998877665544332211")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# Mount static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
STATIC_DIR = os.path.join(PROJECT_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Register API routers
app.include_router(auth.router)
app.include_router(index.router)
app.include_router(search.router)
app.include_router(config.router)
app.include_router(incremental.router)
app.include_router(reclassify.router)


# --- UI HTML PAGE ROUTES ---
def render_page(template_name: str, request: Request, active_page: str, context: dict = None):
    if not verify_session(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    ctx = {"request": request, "active_page": active_page}
    if context:
        ctx.update(context)
    return templates.TemplateResponse(request=request, name=template_name, context=ctx)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    if verify_session(request):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request, "error": error},
    )


@app.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return render_page("dashboard.html", request, "dashboard")


@app.get("/folders", response_class=HTMLResponse)
async def folders_page(request: Request):
    return render_page("folders.html", request, "folders")


@app.get("/file-types", response_class=HTMLResponse)
async def file_types_page(request: Request):
    return render_page("file_types.html", request, "file_types")


@app.get("/exclusions", response_class=HTMLResponse)
async def exclusions_page(request: Request):
    return render_page("exclusions.html", request, "exclusions")


@app.get("/departments", response_class=HTMLResponse)
async def departments_page(request: Request):
    return render_page("departments.html", request, "departments")


@app.get("/doc-types", response_class=HTMLResponse)
async def doctypes_page(request: Request):
    return render_page("doctypes.html", request, "doctypes")


@app.get("/synonyms", response_class=HTMLResponse)
async def synonyms_page(request: Request):
    return render_page("synonyms.html", request, "synonyms")


@app.get("/incremental", response_class=HTMLResponse)
async def incremental_page(request: Request):
    return render_page("incremental.html", request, "incremental")


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    cfg = get_config(db)
    init_key = get_raw_initial_api_key()
    return render_page("settings.html", request, "settings", {"initial_api_key": init_key})


@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    return render_page("logs.html", request, "logs")
