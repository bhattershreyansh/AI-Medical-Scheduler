from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Literal
from datetime import datetime, date
import re

class PatientInfo(BaseModel):
    """Patient information with comprehensive validation"""
    
    patient_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: str = Field(..., pattern=r'^\d{2}/\d{2}/\d{4}$')
    preferred_doctor: Literal['Dr. Naveen', 'Dr. Naresh', 'Dr. Aish', 'Dr. Shreyansh']
    location: Literal["Gachibowli", "Jubliee Hills", "Banjara Hills"]
    phone: str = Field(..., min_length=10)
    email: EmailStr
    
    @field_validator('patient_name')
    def validate_name(cls, v):
        parts = v.strip().split()
        if len(parts) < 2:
            raise ValueError('Please provide both first and last name')
        return ' '.join(part.title() for part in parts if part)
    
    @field_validator('date_of_birth')
    def validate_dob(cls, v):
        try:
            month, day, year = map(int, v.split('/'))
            birth_date = date(year, month, day)
            
            today = date.today()
            if birth_date > today:
                raise ValueError('Date of birth cannot be in the future')
            
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age > 120 or age < 0:
                raise ValueError('Please verify the date of birth')
                
            return v
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError('Date must be in MM/DD/YYYY format')
            raise e
    
    @field_validator('phone')
    def validate_phone(cls, v):
        digits = re.sub(r'[^\d]', '', v)
        if len(digits) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return v
    
    class Config:
        str_strip_whitespace = True
        validate_assignment = True

class PatientLookupResult(BaseModel):
    """Result of patient database lookup"""
    
    patient_id: Optional[str] = None
    patient_type: Literal["new", "returning"]
    appointment_duration: Literal[30, 60]
    last_visit: Optional[str] = None
    existing_insurance: Optional[dict] = None
    
    @field_validator('appointment_duration')
    def validate_duration_matches_type(cls, v, info):
        # Fix for Pydantic v2 - use info.data instead of values
        patient_type = info.data.get('patient_type')
        if patient_type == 'new' and v != 60:
            raise ValueError('New patients require 60-minute appointments')
        if patient_type == 'returning' and v != 30:
            raise ValueError('Returning patients get 30-minute appointments')
        return v
