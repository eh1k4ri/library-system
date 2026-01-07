from fastapi import APIRouter, Response

from app.core.metrics import render_prometheus

router = APIRouter()


@router.get("/metrics")
def get_metrics():
    content, media_type = render_prometheus()
    return Response(content=content, media_type=media_type)
