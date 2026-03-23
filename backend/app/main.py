from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, notebooks, sources, chat, exports

app = FastAPI(
    title="H-NoteBook API",
    description="AI-Powered Web Notebook Application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(notebooks.router, prefix="/api/v1")
app.include_router(sources.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(exports.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "H-NoteBook API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
