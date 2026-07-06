import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.infrastructure.database.connection import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String, nullable=True)
    subscription_tier = Column(String(50), default="free", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    home_address = Column(Text, nullable=True)
    home_lat = Column(Numeric(10, 8), nullable=True)
    home_lng = Column(Numeric(11, 8), nullable=True)
    budget_tier = Column(String(50), default="mid", nullable=False)
    preferred_class = Column(String(50), default="SL", nullable=False)
    accessibility_senior = Column(Boolean, default=False, nullable=False)
    accessibility_wheelchair = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class TripPlan(Base):
    __tablename__ = "trip_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    origin_name = Column(String(255), nullable=False)
    destination_name = Column(String(255), nullable=False)
    travel_date = Column(Date, nullable=False, index=True)
    total_duration_min = Column(Integer, nullable=True)
    total_cost_min = Column(Integer, nullable=True)
    total_cost_max = Column(Integer, nullable=True)
    itinerary_json = Column(JSONB, nullable=False)
    overall_confidence = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)


class Temple(Base):
    __tablename__ = "temples"

    id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    lat = Column(Numeric(10, 8), nullable=False)
    lng = Column(Numeric(11, 8), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    timings = Column(JSONB, nullable=True)
    darshan_info = Column(JSONB, nullable=True)
    dress_code = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trip_plans.id"), nullable=True, index=True)
    type = Column(String(50), nullable=False)
    scheduled_for = Column(DateTime(timezone=True), nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="PENDING", nullable=False, index=True)
    payload = Column(JSONB, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(255), nullable=True)
    details = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
