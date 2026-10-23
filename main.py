from fastapi import FastAPI, Request, UploadFile, File, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.exif_extractor import extract_image_metadata
from core.pdf_extractor import extract_pdf_metadata
from core.sanitizer import sanitize_image, sanitize_pdf
from schemas.metadata_response import MetadataResponse

app = FastAPI(
    title="MetaInspector - Extractor de Metadatos",
    docs_url=None,  # Ocultar OpenAPI/Swagger en producción
    redoc_url=None
)

# CORS Restringido [Checklist 43]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/aviso-legal", response_class=HTMLResponse)
async def legal_page(request: Request):
    return templates.TemplateResponse(request=request, name="legal.html")


@app.get("/privacidad", response_class=HTMLResponse)
async def privacy_page(request: Request):
    return templates.TemplateResponse(request=request, name="privacy.html")


# Endpoint API Inspección [Checklist 26, 31, 32]
@app.post("/api/v1/inspect", response_model=MetadataResponse)
async def inspect_file(file: UploadFile = File(...)):
    contents = await file.read()
    
    # Validar tamaño máximo [Checklist 26]
    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail=f"El archivo supera el límite máximo permitido de {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    filename = file.filename.lower()
    
    if filename.endswith((".jpg", ".jpeg", ".png", ".webp", ".tiff")):
        data = extract_image_metadata(contents, file.filename)
    elif filename.endswith(".pdf"):
        data = extract_pdf_metadata(contents, file.filename)
    else:
        raise HTTPException(status_code=400, detail="Formato no soportado. Usá JPG, PNG, WEBP, TIFF o PDF.")

    return data


# Endpoint API Sanitización/Download [Checklist 26]
@app.post("/api/v1/sanitize")
async def sanitize_file_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename.lower()

    if filename.endswith((".jpg", ".jpeg", ".png", ".webp", ".tiff")):
        clean_bytes = sanitize_image(contents)
        media_type = file.content_type or "image/jpeg"
    elif filename.endswith(".pdf"):
        clean_bytes = sanitize_pdf(contents)
        media_type = "application/pdf"
    else:
        raise HTTPException(status_code=400, detail="Formato no soportado para sanitización.")

    clean_filename = f"clean_{file.filename}"
    return Response(
        content=clean_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'}
    )


# Directivas robots.txt [Checklist 07]
@app.get("/robots.txt", response_class=HTMLResponse)
async def get_robots():
    content = "User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: https://md.lcastro.com.ar/sitemap.xml"
    return HTMLResponse(content=content, media_type="text/plain")


# Error Handlers Personalizados [Checklist 14, 41]
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=404, content={"error": "Recurso no encontrado"})
    return templates.TemplateResponse(request=request, name="404.html", status_code=404)


@app.exception_handler(500)
async def custom_500_handler(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=500, content={"error": "Error interno del servidor"})
    return templates.TemplateResponse(request=request, name="500.html", status_code=500)
