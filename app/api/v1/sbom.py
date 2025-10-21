"""
SBOM module routes.
Forwards requests from API Gateway to SBOM Service.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db import get_db
from app.services import parser, storage, sbom_crud
from app.workers.tasks import enqueue_osv_scan
import uuid

router = APIRouter(prefix="/api/sbom", tags=["sbom"])


@router.post("/upload")
async def upload_sbom(
    project_name: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Receive manifest file (requirements.txt, package-lock.json, v.v.)
    → parse → save to DB & Object Storage → enqueue vuln scan
    """
    content = await file.read()

    try:
        sbom_json = await parser.parse_manifest(file.filename, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse error: {e}")

    object_url = await storage.upload_sbom_json(project_name, sbom_json)
    record = await sbom_crud.create_sbom(
        db,
        project_name=project_name,
        sbom_json=sbom_json,
        source="upload",
        object_url=object_url,
    )

    # enqueue background vulnerability scan
    enqueue_osv_scan.delay(str(record.id))

    return {
        "id": str(record.id),
        "project_name": record.project_name,
        "object_url": record.object_url,
        "message": "SBOM uploaded and queued for vulnerability scan",
    }


@router.get("/list")
async def list_sboms(
    project_name: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    sboms = await sbom_crud.list_sboms(db, project_name, limit)
    return [
        {
            "id": str(s.id),
            "project_name": s.project_name,
            "created_at": s.created_at,
            "object_url": s.object_url,
        }
        for s in sboms
    ]


@router.get("/{sbom_id}")
async def get_sbom(sbom_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    sbom = await sbom_crud.get_sbom(db, sbom_id)
    if not sbom:
        raise HTTPException(status_code=404, detail="SBOM not found")
    return {
        "id": str(sbom.id),
        "project_name": sbom.project_name,
        "created_at": sbom.created_at,
        "object_url": sbom.object_url,
        "sbom": sbom.sbom,
    }
