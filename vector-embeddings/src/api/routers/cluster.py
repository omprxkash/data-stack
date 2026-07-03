from fastapi import APIRouter, Query
from ...storage.chroma_store import ChromaVectorStore
from ...clustering.umap_reducer import UMAPReducer
from ...clustering.kmeans_cluster import KMeansCluster

router = APIRouter()


@router.get("/cluster/umap")
def umap_cluster(
    collection: str = Query("default"),
    n_clusters: int = Query(5),
):
    store = ChromaVectorStore(collection_name=collection)
    reducer = UMAPReducer()
    points = reducer.reduce(store, collection=collection)

    if points:
        clusterer = KMeansCluster(n_clusters=n_clusters)
        cluster_labels = clusterer.cluster(store, collection=collection)
        label_map = {c["id"]: c["cluster"] for c in cluster_labels}
        for p in points:
            p["cluster"] = label_map.get(p["id"], 0)

    return {"points": points, "collection": collection}
