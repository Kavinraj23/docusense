from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from db.session import Base

class Syllabus(Base):
    __tablename__ = "syllabi"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)   
    
    # Foreign key to User (UUID)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Syllabus-specific fields
    course_code = Column(String, nullable=True)
    course_name = Column(String, nullable=True)
    instructor_name = Column(String, nullable=True)
    instructor_email = Column(String, nullable=True)
    semester = Column(String, nullable=True)
    year = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    accent_color = Column(String, nullable=True)  # Store the accent color
    
    # Meeting information
    meeting_days = Column(String, nullable=True)
    meeting_time = Column(String, nullable=True)
    meeting_location = Column(String, nullable=True)
    
    # Important dates
    first_class = Column(String, nullable=True)
    last_class = Column(String, nullable=True)
    midterm_dates = Column(String, nullable=True)  # Stored as JSON array string
    final_exam_date = Column(String, nullable=True)
    
    # Grading
    grading_policy = Column(String, nullable=True)  # Stored as JSON object string
    schedule_summary = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Syllabus(course_code={self.course_code}, course_name={self.course_name})>"