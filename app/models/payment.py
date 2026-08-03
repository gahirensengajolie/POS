import enum
from sqlalchemy import Column, Integer, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PaymentMethod(str, enum.Enum):
    cash = "Cash"
    card = "Card"
    mobile = "Mobile"
    split = "Split"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    payment_method = Column(Enum(PaymentMethod, name="payment_method"), nullable=False)
    amount_paid = Column(Numeric(10, 2), nullable=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())

    sale = relationship("Sale", back_populates="payments")