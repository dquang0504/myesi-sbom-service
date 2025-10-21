from celery import Celery
import httpx
import asyncio
import json
from app.models.db import AsyncSessionLocal
from app.services.sbom_crud import get_sbom

celery = Celery(
    "sbom_tasks", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)

OSV_URL = "https://api.osv.dev/v1/querybatch"


@celery.task(name="enqueue_osv_scan")
def enqueue_osv_scan(sbom_id: str):
    asyncio.run(scan_vulnerabilities(sbom_id))


async def scan_vulnerabilities(sbom_id: str):
    async with AsyncSessionLocal() as session:
        sbom = await get_sbom(session, sbom_id)
        if not sbom:
            return

        components = sbom.sbom.get("components", [])
        queries = [
            {"package": {"name": c["name"], "version": c.get("version", "")}}
            for c in components
        ]

        async with httpx.AsyncClient() as client:
            resp = await client.post(OSV_URL, json={"queries": queries}, timeout=60.0)

        if resp.status_code == 200:
            vuln_result = resp.json()
            print(
                f"[OSV] Vulnerability scan result for {sbom_id}: {json.dumps(vuln_result)[:200]}"
            )
