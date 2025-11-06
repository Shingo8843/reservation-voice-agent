"""
Voice-Enabled Salon Reservation API
FastAPI backend for salon booking system with Supabase integration
"""

from datetime import date, time
from enum import Enum
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Salon Reservation API",
    description="Voice-enabled salon booking system",
    version="1.0.0"
)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Constants
TABLE_NAME = "salon_reservations"
DEFAULT_DURATION_MINUTES = 60


# Enums
class ReservationStatus(str, Enum):
    """Reservation status values"""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Pydantic Models
class ReservationCreate(BaseModel):
    """Request model for creating a reservation"""
    customer_name: str = Field(..., description="Customer's name")
    phone_number: str = Field(..., description="Customer's phone number")
    reservation_date: date = Field(..., description="Appointment date (YYYY-MM-DD)")
    reservation_time: time = Field(..., description="Appointment start time (HH:MM or HH:MM:SS format)")
    stylist_name: str = Field(..., description="Assigned stylist name")
    service_menu: str = Field(..., description="Service type (cut, color, treatment, etc.)")
    duration_minutes: int = Field(default=DEFAULT_DURATION_MINUTES, description="Duration in minutes")
    notes: Optional[str] = Field(default=None, description="Optional special requests")

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v
    
    @field_validator("reservation_time", mode="before")
    @classmethod
    def normalize_time(cls, v):
        """Accept HH:MM, H:MM, HH:MM:SS, and H:MM:SS formats (handles single-digit hours)"""
        if isinstance(v, str):
            parts = v.split(":")
            if len(parts) == 2:
                # HH:MM or H:MM format - add seconds
                hour, minute = parts
                # Add leading zero to hour if single digit
                hour = hour.zfill(2)
                return f"{hour}:{minute}:00"
            elif len(parts) == 3:
                # HH:MM:SS or H:MM:SS format - normalize hour
                hour, minute, second = parts
                # Add leading zero to hour if single digit
                hour = hour.zfill(2)
                return f"{hour}:{minute}:{second}"
        return v


class ReservationUpdate(BaseModel):
    """Request model for updating a reservation.
    Only allows modification of: reservation_date, reservation_time, stylist_name, 
    service_menu, duration_minutes, and notes. Customer name cannot be changed.
    """
    reservation_date: Optional[date] = None
    reservation_time: Optional[time] = None
    stylist_name: Optional[str] = None
    service_menu: Optional[str] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Duration must be positive")
        return v
    
    @field_validator("reservation_time", mode="before")
    @classmethod
    def normalize_time(cls, v):
        """Accept HH:MM, H:MM, HH:MM:SS, and H:MM:SS formats (handles single-digit hours)"""
        if isinstance(v, str):
            parts = v.split(":")
            if len(parts) == 2:
                # HH:MM or H:MM format - add seconds
                hour, minute = parts
                # Add leading zero to hour if single digit
                hour = hour.zfill(2)
                return f"{hour}:{minute}:00"
            elif len(parts) == 3:
                # HH:MM:SS or H:MM:SS format - normalize hour
                hour, minute, second = parts
                # Add leading zero to hour if single digit
                hour = hour.zfill(2)
                return f"{hour}:{minute}:{second}"
        return v


class ReservationResponse(BaseModel):
    """Response model for reservation data"""
    reservation_id: UUID
    customer_name: str
    phone_number: str
    reservation_date: date
    reservation_time: time
    stylist_name: str
    service_menu: str
    duration_minutes: int
    status: str
    notes: Optional[str] = None
    created_at: str
    updated_at: str


class ReservationCreateResponse(BaseModel):
    """Response model for successful reservation creation"""
    message: str
    reservation_id: UUID
    reservation: ReservationResponse


class AvailabilityResponse(BaseModel):
    """Response model for availability check"""
    date: date
    stylist_name: str
    booked_slots: List[time]
    available_slots: List[time]


# Helper Functions
def check_availability_conflict(stylist_name: str, reservation_date: date, reservation_time: time, exclude_id: Optional[UUID] = None) -> bool:
    """
    Check if a stylist is already booked for the given date and time.
    Returns True if conflict exists, False otherwise.
    """
    try:
        # Query for scheduled reservations with matching stylist, date, and time
        query = supabase.table(TABLE_NAME).select("*").eq("stylist_name", stylist_name).eq("reservation_date", reservation_date.strftime("%Y-%m-%d")).eq("reservation_time", reservation_time.strftime("%H:%M:%S")).eq("status", ReservationStatus.SCHEDULED.value)
        
        if exclude_id:
            query = query.neq("reservation_id", str(exclude_id))
        
        result = query.execute()
        
        # If any records exist, there's a conflict
        return len(result.data) > 0
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while checking availability: {str(e)}"
        )


def get_all_hours_in_day() -> List[time]:
    """Generate list of all possible booking hours in a day (9 AM to 5 PM)"""
    hours = []
    for hour in range(9, 17):  # 9 AM to 5 PM 
        hours.append(time(hour, 0, 0))
    return hours


# API Endpoints

@app.post("/add", response_model=ReservationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(reservation: ReservationCreate):
    """
    Create a new reservation.
    
    Returns 409 Conflict if the stylist is already booked for that time slot.
    """
    # Check for availability conflict
    if check_availability_conflict(reservation.stylist_name, reservation.reservation_date, reservation.reservation_time):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Stylist '{reservation.stylist_name}' is already booked for {reservation.reservation_date} at {reservation.reservation_time.strftime('%H:%M')}"
        )
    
    try:
        # Insert new reservation
        reservation_data = {
            "customer_name": reservation.customer_name,
            "phone_number": reservation.phone_number,
            "reservation_date": reservation.reservation_date.strftime("%Y-%m-%d"),
            "reservation_time": reservation.reservation_time.strftime("%H:%M:%S"),
            "stylist_name": reservation.stylist_name,
            "service_menu": reservation.service_menu,
            "duration_minutes": reservation.duration_minutes,
            "status": ReservationStatus.SCHEDULED.value,
            "notes": reservation.notes
        }
        
        result = supabase.table(TABLE_NAME).insert(reservation_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create reservation"
            )
        
        reservation_record = result.data[0]
        
        # Convert to response model
        response = ReservationResponse(
            reservation_id=UUID(reservation_record["reservation_id"]),
            customer_name=reservation_record["customer_name"],
            phone_number=reservation_record["phone_number"],
            reservation_date=date.fromisoformat(reservation_record["reservation_date"]),
            reservation_time=time.fromisoformat(reservation_record["reservation_time"]),
            stylist_name=reservation_record["stylist_name"],
            service_menu=reservation_record["service_menu"],
            duration_minutes=reservation_record["duration_minutes"],
            status=reservation_record["status"],
            notes=reservation_record.get("notes"),
            created_at=reservation_record["created_at"],
            updated_at=reservation_record["updated_at"]
        )
        
        return ReservationCreateResponse(
            message=f"Reservation created successfully for {reservation.customer_name}",
            reservation_id=response.reservation_id,
            reservation=response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating reservation: {str(e)}"
        )


@app.get("/lookup/{phone_number}", response_model=List[ReservationResponse])
async def lookup_reservations(phone_number: str):
    """
    Retrieve all scheduled reservations for a given phone number.
    Returns list sorted by date and time.
    Only returns reservations with status 'scheduled'.
    """
    try:
        result = supabase.table(TABLE_NAME).select("*").eq("phone_number", phone_number).eq("status", ReservationStatus.SCHEDULED.value).order("reservation_date").order("reservation_time").execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No scheduled reservations found for phone number: {phone_number}"
            )
        
        reservations = []
        for record in result.data:
            reservations.append(ReservationResponse(
                reservation_id=UUID(record["reservation_id"]),
                customer_name=record["customer_name"],
                phone_number=record["phone_number"],
                reservation_date=date.fromisoformat(record["reservation_date"]),
                reservation_time=time.fromisoformat(record["reservation_time"]),
                stylist_name=record["stylist_name"],
                service_menu=record["service_menu"],
                duration_minutes=record["duration_minutes"],
                status=record["status"],
                notes=record.get("notes"),
                created_at=record["created_at"],
                updated_at=record["updated_at"]
            ))
        
        return reservations
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error looking up reservations: {str(e)}"
        )


@app.put("/modify/{reservation_id}", response_model=ReservationResponse)
async def modify_reservation(reservation_id: UUID, updates: ReservationUpdate):
    """
    Modify an existing reservation.
    Allowed fields: reservation_date, reservation_time, stylist_name, 
    service_menu, duration_minutes, notes.
    Customer name cannot be modified.
    Returns 409 Conflict if the new time conflicts with another booking.
    """
    try:
        # First, check if reservation exists
        existing = supabase.table(TABLE_NAME).select("*").eq("reservation_id", str(reservation_id)).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reservation with ID {reservation_id} not found"
            )
        
        existing_record = existing.data[0]
        
        # Build update dictionary (customer_name is not allowed to be modified)
        update_data = {}
        if updates.reservation_date is not None:
            update_data["reservation_date"] = updates.reservation_date.strftime("%Y-%m-%d")
        if updates.reservation_time is not None:
            update_data["reservation_time"] = updates.reservation_time.strftime("%H:%M:%S")
        if updates.stylist_name is not None:
            update_data["stylist_name"] = updates.stylist_name
        if updates.service_menu is not None:
            update_data["service_menu"] = updates.service_menu
        if updates.duration_minutes is not None:
            update_data["duration_minutes"] = updates.duration_minutes
        if updates.notes is not None:
            update_data["notes"] = updates.notes
        
        # Determine the stylist, date, and time to check
        check_stylist = update_data.get("stylist_name", existing_record["stylist_name"])
        check_date = update_data.get("reservation_date", existing_record["reservation_date"])
        check_time = update_data.get("reservation_time", existing_record["reservation_time"])
        
        # Convert to proper types for conflict check
        if isinstance(check_date, str):
            check_date = date.fromisoformat(check_date)
        if isinstance(check_time, str):
            check_time = time.fromisoformat(check_time)
        
        # Check for availability conflict (excluding current reservation)
        if check_availability_conflict(check_stylist, check_date, check_time, exclude_id=reservation_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Stylist '{check_stylist}' is already booked for {check_date} at {check_time.strftime('%H:%M')}"
            )
        
        # Perform update
        result = supabase.table(TABLE_NAME).update(update_data).eq("reservation_id", str(reservation_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update reservation"
            )
        
        updated_record = result.data[0]
        
        return ReservationResponse(
            reservation_id=UUID(updated_record["reservation_id"]),
            customer_name=updated_record["customer_name"],
            phone_number=updated_record["phone_number"],
            reservation_date=date.fromisoformat(updated_record["reservation_date"]),
            reservation_time=time.fromisoformat(updated_record["reservation_time"]),
            stylist_name=updated_record["stylist_name"],
            service_menu=updated_record["service_menu"],
            duration_minutes=updated_record["duration_minutes"],
            status=updated_record["status"],
            notes=updated_record.get("notes"),
            created_at=updated_record["created_at"],
            updated_at=updated_record["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error modifying reservation: {str(e)}"
        )


@app.delete("/cancel/{reservation_id}", response_model=ReservationResponse)
async def cancel_reservation(reservation_id: UUID):
    """
    Cancel a reservation by setting status to 'cancelled'.
    This frees up the time slot for rebooking.
    """
    try:
        # Check if reservation exists
        existing = supabase.table(TABLE_NAME).select("*").eq("reservation_id", str(reservation_id)).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reservation with ID {reservation_id} not found"
            )
        
        # Update status to cancelled
        result = supabase.table(TABLE_NAME).update({"status": ReservationStatus.CANCELLED.value}).eq("reservation_id", str(reservation_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel reservation"
            )
        
        cancelled_record = result.data[0]
        
        return ReservationResponse(
            reservation_id=UUID(cancelled_record["reservation_id"]),
            customer_name=cancelled_record["customer_name"],
            phone_number=cancelled_record["phone_number"],
            reservation_date=date.fromisoformat(cancelled_record["reservation_date"]),
            reservation_time=time.fromisoformat(cancelled_record["reservation_time"]),
            stylist_name=cancelled_record["stylist_name"],
            service_menu=cancelled_record["service_menu"],
            duration_minutes=cancelled_record["duration_minutes"],
            status=cancelled_record["status"],
            notes=cancelled_record.get("notes"),
            created_at=cancelled_record["created_at"],
            updated_at=cancelled_record["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling reservation: {str(e)}"
        )


@app.get("/availability", response_model=AvailabilityResponse)
async def check_availability(reservation_date: date, stylist: str):
    """
    Check availability for a stylist on a specific date.
    Returns list of booked and available time slots.
    
    Query Parameters:
    - reservation_date: Date in YYYY-MM-DD format
    - stylist: Stylist name
    """
    try:
        # Get all scheduled reservations for the stylist on the given date
        result = supabase.table(TABLE_NAME).select("reservation_time").eq("stylist_name", stylist).eq("reservation_date", reservation_date.strftime("%Y-%m-%d")).eq("status", ReservationStatus.SCHEDULED.value).execute()
        
        booked_times = []
        if result.data:
            booked_times = [time.fromisoformat(record["reservation_time"]) for record in result.data]
        
        # Get all possible hours (9 AM to 5 PM)
        all_hours = get_all_hours_in_day()
        
        # Calculate available slots
        available_times = [t for t in all_hours if t not in booked_times]
        
        return AvailabilityResponse(
            date=reservation_date,
            stylist_name=stylist,
            booked_slots=sorted(booked_times),
            available_slots=sorted(available_times)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking availability: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Salon Reservation API",
        "version": "1.0.0",
        "endpoints": {
            "create": "POST /add",
            "lookup": "GET /lookup/{phone_number}",
            "modify": "PUT /modify/{reservation_id}",
            "cancel": "DELETE /cancel/{reservation_id}",
            "availability": "GET /availability?reservation_date=YYYY-MM-DD&stylist=NAME",
            "docs": "GET /docs"
        }
    }
