from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.models.analytics import Analytics
from app.schemas.analytics import AnalyticsCreate, AnalyticsUpdate
from datetime import datetime, date


class CRUDAnalytics:
    def get(self, db: Session, id: int) -> Optional[Analytics]:
        return db.query(Analytics).filter(Analytics.id == id).first()

    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        employee_id: Optional[int] = None,
        violation_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Analytics]:
        query = db.query(Analytics)
        
        if employee_id is not None:
            query = query.filter(Analytics.employee_id == employee_id)
        
        if violation_type:
            query = query.filter(Analytics.violation_type == violation_type)
            
        if start_date:
            query = query.filter(Analytics.violation_date >= start_date)
            
        if end_date:
            query = query.filter(Analytics.violation_date <= end_date)
        
        return query.order_by(desc(Analytics.violation_date), desc(Analytics.created_at)).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: AnalyticsCreate) -> Analytics:
        db_obj = Analytics(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_multi(self, db: Session, *, obj_ins: List[AnalyticsCreate]) -> List[Analytics]:
        """Create multiple analytics records in batch"""
        db_objs = [Analytics(**obj_in.model_dump()) for obj_in in obj_ins]
        db.add_all(db_objs)
        db.commit()
        for db_obj in db_objs:
            db.refresh(db_obj)
        return db_objs

    def update(
        self, db: Session, *, db_obj: Analytics, obj_in: AnalyticsUpdate
    ) -> Analytics:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Analytics:
        obj = db.query(Analytics).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def count(
        self, 
        db: Session,
        employee_id: Optional[int] = None,
        violation_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> int:
        query = db.query(Analytics)
        
        if employee_id is not None:
            query = query.filter(Analytics.employee_id == employee_id)
        
        if violation_type:
            query = query.filter(Analytics.violation_type == violation_type)
            
        if start_date:
            query = query.filter(Analytics.violation_date >= start_date)
            
        if end_date:
            query = query.filter(Analytics.violation_date <= end_date)
            
        return query.count()

    def get_by_employee_and_date(
        self, db: Session, employee_id: int, violation_date: date
    ) -> List[Analytics]:
        return db.query(Analytics).filter(
            and_(
                Analytics.employee_id == employee_id,
                Analytics.violation_date == violation_date
            )
        ).all()

    def exists_for_employee_date_type(
        self, db: Session, employee_id: int, violation_date: date, violation_type: str
    ) -> bool:
        """Check if analytics record already exists for specific employee, date, and type"""
        return db.query(Analytics).filter(
            and_(
                Analytics.employee_id == employee_id,
                Analytics.violation_date == violation_date,
                Analytics.violation_type == violation_type
            )
        ).first() is not None


analytics = CRUDAnalytics()