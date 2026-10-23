from typing import Dict, Any, Optional
from pydantic import BaseModel


class MetadataResponse(BaseModel):
    filename: str
    type: str
    format: Optional[str] = None
    dimensions: Optional[str] = None
    camera: Optional[str] = None
    software: Optional[str] = None
    datetime: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    producer: Optional[str] = None
    page_count: Optional[int] = None
    encrypted: Optional[bool] = None
    gps: Optional[Dict[str, float]] = None
    raw_metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
