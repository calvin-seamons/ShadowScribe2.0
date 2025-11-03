"""SQLAlchemy database models."""
from sqlalchemy import Column, String, Integer, JSON, TIMESTAMP
from datetime import datetime

from api.database.connection import Base


class Character(Base):
    """Character model - stores full character data as JSON."""
    __tablename__ = 'characters'
    
    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    race = Column(String(100))
    character_class = Column(String(100))
    level = Column(Integer)
    data = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'race': self.race,
            'character_class': self.character_class,
            'level': self.level,
            'data': self.data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
