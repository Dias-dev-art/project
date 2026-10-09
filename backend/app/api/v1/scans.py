from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.scan import Scan
from app.schemas.scan import ScanOut

router = APIRouter(prefix="/scans")


@router.get("", response_model=list[ScanOut])
async def list_scans(db: AsyncSession = Depends(get_db)):
    stmt = select(Scan).options(selectinload(Scan.findings)).order_by(Scan.id.desc()).limit(50)
    return (await db.execute(stmt)).scalars().all()


@router.get("/{scan_id}", response_model=ScanOut)
async def get_scan(scan_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Scan).options(selectinload(Scan.findings)).where(Scan.id == scan_id)
    scan = (await db.execute(stmt)).scalar_one_or_none()
    if scan is None:
        raise HTTPException(status_code=404, detail="scan not found")
    return scan
