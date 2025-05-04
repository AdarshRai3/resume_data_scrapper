from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse

from app.routers.resume_router import router as resume_router

# Create FastAPI application
app = FastAPI(
    title="Resume Extractor API",
    description="Extract structured data from resume PDFs",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    openapi_url=None,  # Important: Disable default OpenAPI schema
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(resume_router)


# Custom OpenAPI and Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Resume Extractor API",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title="Resume Extractor API",
        version="1.0.0",
        description="Extract structured data from resume PDFs",
        routes=app.routes,
    )
    
    # Explicitly set the OpenAPI version
    openapi_schema["openapi"] = "3.0.0"
    
    return JSONResponse(content=openapi_schema)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Welcome to Resume Extractor API",
        "documentation": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)