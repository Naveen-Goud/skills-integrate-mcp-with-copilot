"""
Database models using SQLAlchemy ORM

Defines the schema for Activities and Participants with proper relationships.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Activity(Base):
    """
    Activity model representing extracurricular activities.
    
    Attributes:
        id: Unique activity identifier
        name: Activity name (unique)
        description: Detailed description of the activity
        schedule: When the activity meets
        max_participants: Maximum number of participants allowed
        participants: Relationship to Participant records
    """
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    schedule = Column(String(255), nullable=False)
    max_participants = Column(Integer, nullable=False)
    
    # Relationship to participants
    participants = relationship("Participant", back_populates="activity", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert Activity to dictionary format for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "schedule": self.schedule,
            "max_participants": self.max_participants,
            "participants": [p.email for p in self.participants]
        }


class Participant(Base):
    """
    Participant model representing students registered for activities.
    
    Attributes:
        id: Unique participant record identifier
        email: Student email address
        activity_id: Foreign key reference to the activity
        activity: Relationship to the Activity record
    """
    __tablename__ = "participants"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    
    # Relationship to activity
    activity = relationship("Activity", back_populates="participants")
    
    # Unique constraint: a student can only register once per activity
    __table_args__ = (
        UniqueConstraint("email", "activity_id", name="uq_email_activity"),
    )
