from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, time, datetime
from uuid import UUID

class Reservation(BaseModel):
    customer_name: str
    phone_number: str
    reservation_date: date
    reservation_time: time
    stylist_name: str
    service_menu: str
    duration_minutes: Optional[int] = 60
    status: Optional[str] = "scheduled"
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ReservationResponse(BaseModel):
    reservation_id: UUID
    customer_name: str
    phone_number: str
    reservation_date: date
    reservation_time: time
    stylist_name: str
    service_menu: str
    duration_minutes: Optional[int] = 60
    status: Optional[str] = "scheduled"
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
