from .patients_models import PatientInfo, PatientLookupResult
from .appointment_models import AppointmentSlot, AppointmentBooking
from .insurance_models import InsuranceInfo

# Resolve forward references
AppointmentBooking.model_rebuild()

__all__ = [
    "PatientInfo",
    "PatientLookupResult", 
    "AppointmentSlot",
    "AppointmentBooking",
    "InsuranceInfo"
]
