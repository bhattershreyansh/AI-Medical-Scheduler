from typing import TypedDict, List, Optional
from models import PatientInfo, PatientLookupResult, AppointmentSlot, AppointmentBooking, InsuranceInfo

class BookingState(TypedDict):
    # Process Control
    current_step: str
    user_input: Optional[str]
    agent_response: Optional[str]
    conversation_history: List[str]
    errors: List[str]
    
    # Validated Pydantic Models
    patient_info: Optional[PatientInfo]
    lookup_result: Optional[PatientLookupResult]
    available_slots: Optional[List[AppointmentSlot]]
    selected_slot: Optional[AppointmentSlot]
    insurance_info: Optional[InsuranceInfo]
    final_booking: Optional[AppointmentBooking]
    
    # Temporary data during collection
    temp_name: Optional[str]
    temp_dob: Optional[str]
    temp_doctor: Optional[str]
    temp_location: Optional[str]
    temp_phone: Optional[str]
    
    # Status Flags
    calendar_updated: bool
    excel_exported: bool
    form_sent: bool

def create_initial_state() -> BookingState:
    """Create initial booking state"""
    return BookingState(
        current_step="greeting",
        user_input=None,
        agent_response=None,
        conversation_history=[],
        errors=[],
        patient_info=None,
        lookup_result=None,
        available_slots=None,
        selected_slot=None,
        insurance_info=None,
        final_booking=None,
        temp_name=None,
        temp_dob=None,
        temp_doctor=None,
        temp_location=None,
        temp_phone=None,
        calendar_updated=False,
        excel_exported=False,
        form_sent=False
    )
