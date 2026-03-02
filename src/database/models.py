from __future__ import annotations

import uuid

from sqlalchemy import CHAR, Column, Date, DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    __allow_unmapped__ = True


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    isin = Column(String(12), unique=True, nullable=False)
    sedol = Column(String(7), nullable=True)
    short_description = Column(String(255), nullable=True)
    issuer = Column(String(255), nullable=False)
    issue_date = Column(Date, nullable=False)
    currency = Column(CHAR(3), nullable=False, server_default="GBP")
    maturity_date = Column(Date, nullable=False)
    product_type = Column(String(100), nullable=True)
    guarantor = Column(String(255), nullable=True)
    dealer = Column(String(255), nullable=True)
    nominal_amount = Column(Numeric(18, 2), nullable=True)
    specified_denomination = Column(Numeric(18, 2), nullable=True)
    calculation_amount = Column(Numeric(18, 2), nullable=True)
    strike_date = Column(Date, nullable=True)
    trade_date = Column(Date, nullable=False)
    coupon_barrier_level = Column(Numeric(5, 2), nullable=True)
    knock_in_barrier_level = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    events = relationship("ProductEvent", back_populates="product", cascade="all, delete-orphan")
    underlyings = relationship("ProductUnderlying", back_populates="product", cascade="all, delete-orphan")


class ProductEvent(Base):
    __tablename__ = "product_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_isin = Column(String(12), ForeignKey("products.isin"), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_level_pct = Column(Numeric(6, 2), nullable=True)
    event_strike_pct = Column(Numeric(6, 2), nullable=True)
    event_date = Column(Date, nullable=False)
    event_amount = Column(Numeric(10, 4), nullable=True)
    event_payment_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    
    product = relationship("Product", back_populates="events")


class ProductUnderlying(Base):
    __tablename__ = "product_underlyings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_isin = Column(String(12), ForeignKey("products.isin"), nullable=False)
    bbg_code = Column(String(50), nullable=False)
    weight = Column(Numeric(5, 4), nullable=True)
    initial_price = Column(Numeric(18, 4), nullable=True)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    product = relationship("Product", back_populates="underlyings")
