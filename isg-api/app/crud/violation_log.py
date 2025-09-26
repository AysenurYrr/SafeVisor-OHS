from typing import List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from app.models.violation_log import ViolationLog
from app.schemas.violation_log import ViolationLogCreate, ViolationLogUpdate
from datetime import datetime, date


class CRUDViolationLog:
    def get(self, db: Session, id: int) -> Optional[ViolationLog]:
        return db.query(ViolationLog).filter(ViolationLog.id == id).first()

    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        employee_id: Optional[int] = None,
        camera_id: Optional[int] = None,
        reported: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ViolationLog]:
        query = db.query(ViolationLog)
        
        if employee_id is not None:
            query = query.filter(ViolationLog.employee_id == employee_id)
        
        if camera_id is not None:
            query = query.filter(ViolationLog.camera_id == camera_id)
            
        if reported is not None:
            query = query.filter(ViolationLog.reported == reported)
            
        if start_date:
            query = query.filter(ViolationLog.timestamp >= start_date)
            
        if end_date:
            query = query.filter(ViolationLog.timestamp <= end_date)
        
        return query.order_by(desc(ViolationLog.timestamp)).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ViolationLogCreate) -> ViolationLog:
        db_obj = ViolationLog(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ViolationLog, obj_in: ViolationLogUpdate
    ) -> ViolationLog:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ViolationLog:
        obj = db.query(ViolationLog).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_unreported_for_date(self, db: Session, target_date: date) -> List[ViolationLog]:
        """Get all unreported violation logs for a specific date"""
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        return db.query(ViolationLog).filter(
            and_(
                ViolationLog.reported == False,
                ViolationLog.timestamp >= start_datetime,
                ViolationLog.timestamp <= end_datetime
            )
        ).all()

    def mark_as_reported(self, db: Session, violation_log_ids: List[int]) -> int:
        """Mark violation logs as reported"""
        count = db.query(ViolationLog).filter(
            ViolationLog.id.in_(violation_log_ids)
        ).update(
            {ViolationLog.reported: True},
            synchronize_session=False
        )
        db.commit()
        return count

    def count(
        self, 
        db: Session,
        employee_id: Optional[int] = None,
        camera_id: Optional[int] = None,
        reported: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        query = db.query(ViolationLog)
        
        if employee_id is not None:
            query = query.filter(ViolationLog.employee_id == employee_id)
        
        if camera_id is not None:
            query = query.filter(ViolationLog.camera_id == camera_id)
            
        if reported is not None:
            query = query.filter(ViolationLog.reported == reported)
            
        if start_date:
            query = query.filter(ViolationLog.timestamp >= start_date)
            
        if end_date:
            query = query.filter(ViolationLog.timestamp <= end_date)
            
        return query.count()


violation_log = CRUDViolationLog()