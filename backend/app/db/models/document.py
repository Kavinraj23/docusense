from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.db.session import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)

    # Gemini metadata fields
    title = Column(String, nullable=True)
    author = Column(String, nullable=True)
    document_type = Column(String, nullable=True)
    date = Column(String, nullable=True)  # keep as string for now
    summary = Column(Text, nullable=True)
    tags = Column(String, nullable=True)  # store comma-separated list

    def __repr__(self):
        return f"<Document(filename={self.filename}, title={self.title})>"