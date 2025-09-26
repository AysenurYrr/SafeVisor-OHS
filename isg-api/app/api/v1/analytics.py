from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud import analytics, violation_log, employee
from app.schemas.analytics import (
    AnalyticsResponse, 
    AnalyticsListResponse, 
    AnalyticsGenerateRequest,
    AnalyticsReportsFilter
)
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.employee import Employee
from datetime import date, datetime
import json
from typing import Any, Dict
import numpy as np

router = APIRouter()


def _match_employee_by_embeddings(face_embeddings: List[float], db: Session, threshold: float = 0.6) -> Optional[int]:
    """
    Match employee by face embeddings using cosine similarity
    Returns employee_id if match found, None otherwise
    """
    if not face_embeddings:
        return None
    
    # Get all employees with face embeddings
    employees_with_embeddings = db.query(Employee).filter(
        Employee.face_embeddings.isnot(None)
    ).all()
    
    if not employees_with_embeddings:
        return None
    
    input_embedding = np.array(face_embeddings)
    best_match_id = None
    best_similarity = threshold
    
    for emp in employees_with_embeddings:
        try:
            # Parse stored embeddings
            if isinstance(emp.face_embeddings, str):
                stored_embeddings = json.loads(emp.face_embeddings)
            else:
                stored_embeddings = emp.face_embeddings
            
            if not stored_embeddings:
                continue
                
            stored_embedding = np.array(stored_embeddings)
            
            # Calculate cosine similarity
            similarity = np.dot(input_embedding, stored_embedding) / (
                np.linalg.norm(input_embedding) * np.linalg.norm(stored_embedding)
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = emp.id
                
        except (json.JSONDecodeError, ValueError, TypeError):
            # Skip invalid embeddings
            continue
    
    return best_match_id


@router.post("/generate-daily")
async def generate_daily_analytics(
    request: AnalyticsGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process all unreported violation logs for current day (or specified date),
    match employees by embeddings, insert into analytics, mark violation logs as reported.
    """
    target_date = request.date or date.today()
    
    # Get unreported violation logs for the target date
    unreported_logs = violation_log.violation_log.get_unreported_for_date(db, target_date)
    
    if not unreported_logs:
        return {
            "message": f"No unreported violation logs found for {target_date}",
            "processed_count": 0,
            "created_analytics": 0
        }
    
    created_analytics = []
    processed_log_ids = []
    
    for log in unreported_logs:
        employee_id = log.employee_id
        
        # If employee_id is not set, try to match using face embeddings
        if not employee_id and log.bounding_boxes:
            try:
                # Extract face embeddings from bounding boxes if available
                bounding_box_data = log.bounding_boxes
                if isinstance(bounding_box_data, str):
                    bounding_box_data = json.loads(bounding_box_data)
                
                # Look for face embeddings in the bounding box data
                face_embeddings = bounding_box_data.get("face_embeddings")
                if face_embeddings:
                    employee_id = _match_employee_by_embeddings(face_embeddings, db)
                    
                    # Update the violation log with matched employee
                    if employee_id:
                        log.employee_id = employee_id
                        db.add(log)
                        
            except (json.JSONDecodeError, KeyError, TypeError):
                # Skip if we can't parse embeddings
                pass
        
        # Skip if we still don't have an employee
        if not employee_id:
            continue
        
        # Process each violation type
        violation_types = log.violation_types
        if isinstance(violation_types, str):
            violation_types = json.loads(violation_types)
        
        for violation_type in violation_types:
            # Check if analytics record already exists
            if not analytics.analytics.exists_for_employee_date_type(
                db, employee_id, target_date, violation_type
            ):
                # Get first image path if available
                image_path = None
                if log.image_paths:
                    image_paths = log.image_paths
                    if isinstance(image_paths, str):
                        image_paths = json.loads(image_paths)
                    if image_paths and len(image_paths) > 0:
                        image_path = image_paths[0]
                
                # Create analytics record
                analytics_create = analytics.AnalyticsCreate(
                    employee_id=employee_id,
                    violation_type=violation_type,
                    violation_date=target_date,
                    violation_image_path=image_path
                )
                
                created_record = analytics.analytics.create(db, obj_in=analytics_create)
                created_analytics.append(created_record)
        
        processed_log_ids.append(log.id)
    
    # Mark processed logs as reported
    if processed_log_ids:
        violation_log.violation_log.mark_as_reported(db, processed_log_ids)
        db.commit()
    
    return {
        "message": f"Successfully processed violation logs for {target_date}",
        "processed_count": len(processed_log_ids),
        "created_analytics": len(created_analytics),
        "target_date": target_date
    }


@router.get("/reports", response_model=AnalyticsListResponse)
async def get_analytics_reports(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    violation_type: Optional[str] = Query(None, description="Filter by violation type"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List analytics reports with filters (date, employee, violation type).
    """
    skip = (page - 1) * per_page
    
    # Get analytics records
    analytics_records = analytics.analytics.get_multi(
        db,
        skip=skip,
        limit=per_page,
        employee_id=employee_id,
        violation_type=violation_type,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get total count
    total = analytics.analytics.count(
        db,
        employee_id=employee_id,
        violation_type=violation_type,
        start_date=start_date,
        end_date=end_date
    )
    
    return AnalyticsListResponse(
        analytics=analytics_records,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/summary")
async def get_analytics_summary(
    start_date: Optional[date] = Query(None, description="Start date for summary"),
    end_date: Optional[date] = Query(None, description="End date for summary"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get analytics summary with violation counts by type and employee.
    """
    # If no dates provided, use last 30 days
    if not start_date:
        from datetime import timedelta
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Get all analytics in date range
    all_analytics = analytics.analytics.get_multi(
        db,
        skip=0,
        limit=10000,  # Large number to get all
        start_date=start_date,
        end_date=end_date
    )
    
    # Group by violation type
    violation_type_counts = {}
    employee_counts = {}
    daily_counts = {}
    
    for record in all_analytics:
        # Count by violation type
        vtype = record.violation_type
        violation_type_counts[vtype] = violation_type_counts.get(vtype, 0) + 1
        
        # Count by employee
        emp_id = record.employee_id
        employee_counts[emp_id] = employee_counts.get(emp_id, 0) + 1
        
        # Count by date
        vdate = record.violation_date.isoformat()
        daily_counts[vdate] = daily_counts.get(vdate, 0) + 1
    
    return {
        "summary_period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "total_violations": len(all_analytics),
        "violations_by_type": violation_type_counts,
        "violations_by_employee": employee_counts,
        "daily_violation_counts": daily_counts,
        "unique_employees": len(employee_counts),
        "unique_violation_types": len(violation_type_counts)
    }