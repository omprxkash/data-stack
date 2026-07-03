"""
Standalone Plotly visualisation for UMAP output — useful in notebooks or as a quick CLI check.
"""
import json


def scatter_umap(points: list[dict], title: str = "UMAP cluster view") -> None:
    """Render an interactive 2D scatter plot. Requires plotly installed."""
    try:
        import plotly.express as px
        import pandas as pd
    except ImportError:
        raise ImportError("Install plotly and pandas to use scatter_umap()")

    df = pd.DataFrame(points)
    if "cluster" not in df.columns:
        df["cluster"] = "0"
    df["cluster"] = df["cluster"].astype(str)
    df["label"] = df["text"].str[:80] + "…"

    fig = px.scatter(
        df, x="x", y="y", color="cluster",
        hover_data=["id", "label"],
        title=title, width=900, height=600,
    )
    fig.update_traces(marker=dict(size=8, opacity=0.8))
    fig.show()


def export_json(points: list[dict], path: str) -> None:
    """Save UMAP points to a JSON file for use outside Python."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(points, f, indent=2)
