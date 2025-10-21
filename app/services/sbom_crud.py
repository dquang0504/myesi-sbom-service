from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sbom_models import SBOM
from typing import Optional
from uuid import UUID


async def create_sbom(
    session: AsyncSession,
    project_name: str,
    sbom_json: dict,
    source: str = "upload",
    object_url: Optional[str] = None,
) -> SBOM:
    new = SBOM(
        project_name=project_name, sbom=sbom_json, source=source, object_url=object_url
    )
    session.add(new)
    await session.commit()
    await session.refresh(new)
    return new


async def get_sbom(session: AsyncSession, sbom_id: UUID) -> Optional[SBOM]:
    q = select(SBOM).where(SBOM.id == sbom_id)
    r = await session.execute(q)
    return r.scalar_one_or_none()


async def list_sboms(
    session: AsyncSession,
    project_name: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    q = select(SBOM).order_by(SBOM.created_at.desc()).limit(limit).offset(offset)
    if project_name:
        q = q.where(SBOM.project_name == project_name)
    r = await session.execute(q)
    return r.scalars().all()


async def find_by_component(
    session: AsyncSession, component_name: str, limit: int = 100
):
    # assumes sbom JSON structure includes list of components under sbom["components"][*]["name"]
    q = (
        select(SBOM)
        .where(SBOM.sbom["components"].contains([{"name": component_name}]))
        .limit(limit)
    )
    r = await session.execute(q)
    return r.scalars().all()
