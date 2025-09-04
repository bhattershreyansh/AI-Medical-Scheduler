from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime, date, time
import re
from .patients_models import PatientInfo, PatientLookupResult
from .insurance_models import InsuranceInfo

class AppointmentSlot(BaseModel):
    """Available appointment slot"""
    
    doctor: str
    location: str  
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    time: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    duration_available: int = Field(..., ge=30, le=60)
    
    @field_validator('date')
    def validate_future_date(cls, v):
        return v

class AppointmentBooking(BaseModel):
    """Complete appointment booking record"""
    
    appointment_id: str
    patient_info: 'PatientInfo'
    appointment_slot: AppointmentSlot
    insurance_info: 'InsuranceInfo'
    
    status: Literal["confirmed", "pending", "cancelled"] = "confirmed"
    created_at: datetime = Field(default_factory=datetime.now)
    form_sent: bool = False
    reminders_sent: int = Field(default=0, ge=0, le=3)
    
    @field_validator('appointment_id')
    def validate_appointment_id_format(cls, v):
        pattern = r'^APT_\d{8}_\d{3}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid appointment ID format')
        return v
