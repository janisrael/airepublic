"""
Base repository class for data access operations
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from model.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, model: type[ModelType], session: Session):
        self.model = model
        self.session = session
    
    def create(self, **kwargs) -> ModelType:
        """Create a new record"""
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get record by ID"""
        return self.session.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination"""
        return self.session.query(self.model).offset(skip).limit(limit).all()
    
    def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """Get record by field value"""
        return self.session.query(self.model).filter(getattr(self.model, field) == value).first()
    
    def get_by_fields(self, **kwargs) -> List[ModelType]:
        """Get records by multiple field values"""
        filters = [getattr(self.model, key) == value for key, value in kwargs.items()]
        return self.session.query(self.model).filter(and_(*filters)).all()
    
    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update record by ID"""
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            self.session.commit()
            self.session.refresh(instance)
        return instance
    
    def delete(self, id: int) -> bool:
        """Delete record by ID"""
        instance = self.get_by_id(id)
        if instance:
            self.session.delete(instance)
            self.session.commit()
            return True
        return False
    
    def count(self) -> int:
        """Count total records"""
        return self.session.query(self.model).count()
    
    def exists(self, id: int) -> bool:
        """Check if record exists by ID"""
        return self.session.query(self.model).filter(self.model.id == id).first() is not None
    
    def search(self, search_term: str, search_fields: List[str]) -> List[ModelType]:
        """Search records by term across multiple fields"""
        filters = []
        for field in search_fields:
            filters.append(getattr(self.model, field).ilike(f"%{search_term}%"))
        return self.session.query(self.model).filter(or_(*filters)).all()
    
    def filter_by(self, **kwargs) -> List[ModelType]:
        """Filter records by field values"""
        return self.session.query(self.model).filter_by(**kwargs).all()
    
    def order_by(self, field: str, desc: bool = False) -> List[ModelType]:
        """Order records by field"""
        order_func = desc if desc else asc
        return self.session.query(self.model).order_by(order_func(getattr(self.model, field))).all()
    
    def paginate(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Paginate records"""
        offset = (page - 1) * per_page
        records = self.session.query(self.model).offset(offset).limit(per_page).all()
        total = self.count()
        
        return {
            'records': records,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'has_next': page * per_page < total,
            'has_prev': page > 1
        }
