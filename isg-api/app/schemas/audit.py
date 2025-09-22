from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class AuditLogRead(BaseModel):
    id: int
    user_id: int
    action: str
    target: Optional[str] = None
    timestamp: datetime
    event_metadata: Optional[Any] = None

    class Config:
        from_attributes = True
