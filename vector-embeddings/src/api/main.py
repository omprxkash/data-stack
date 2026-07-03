from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import embed, search, cluster, retrieve, health

app = FastAPI(
    title="vector-embeddings",
    description="Semantic search, hybrid retrieval, and clustering over your own documents.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(embed.router, tags=["Embeddings"])
app.include_router(search.router, tags=["Search"])
app.include_router(cluster.router, tags=["Clustering"])
app.include_router(retrieve.router, tags=["Retrieval"])
app.include_router(health.router, tags=["Health"])


