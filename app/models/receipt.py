from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), unique=True, nullable=False)
    receipt_number = Column(String(50), unique=True, nullable=False)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())

    sale = relationship("Sale", back_populates="receipt")