from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.db.session import Base

class Syllabus(Base):
    __tablename__ = "syllabi"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)   
    
    # Syllabus-specific fields
    course_code = Column(String, nullable=True)
    course_name = Column(String, nullable=True)
    instructor_name = Column(String, nullable=True)
    instructor_email = Column(String, nullable=True)
    semester = Column(String, nullable=True)
    year = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
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