from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.employee_log import EmployeeLogResponse
from app.crud import employee_log as crud_employee_log

router = APIRouter()

@router.get('/', response_model=List[EmployeeLogResponse])
def list_employee_logs(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    employee_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_active_user)
) -> List[EmployeeLogResponse]:
    logs = crud_employee_log.get_employee_logs(
        db=db,
        skip=skip,
        limit=limit,
        employee_id=employee_id,
        action=action
    )
    # Enrich names
    enriched = []
    for log in logs:
        log_full = crud_employee_log.get_employee_log_with_names(db, log.id)
        if log_full:
            enriched.append(log_full)
    return enriched
