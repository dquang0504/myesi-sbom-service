from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from .db import Base
import uuid


class SBOM(Base):
    __tablename__ = "sboms"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String(255), index=True, nullable=False)
    source = Column(String(50), nullable=False, default="upload")  # upload | ci | api
    sbom = Column(JSONB, nullable=False)  # full canonical SBOM JSON stored here
    summary = Column(
        JSONB, nullable=True
    )  # optional materialized summary (components list, counts)
    object_url = Column(
        String(1024), nullable=True
    )  # presigned URL or object key in S3/MinIO
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_sboms_project_created", "project_name", "created_at"),)
