import sys
import os
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
from pathlib import Path

# Safe path handling
try:
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir.parent))
except NameError:
    sys.path.append('..')

from models import AppointmentSlot, PatientLookupResult

class SchedulingAgent:
    """Assignment-accurate scheduling agent for appointment slot management"""
    
    def __init__(self, schedule_excel_path: str = "data/doctors_schedule.xlsx"):
        self.schedule_excel_path = schedule_excel_path
        self.schedule_df = None
        self.load_doctor_schedule()
    
    def load_doctor_schedule(self):
        """Load doctor availability schedule from Excel"""
        try:
            # Try multiple paths to find the schedule file
            possible_paths = [
                self.schedule_excel_path,
                "../data/doctors_schedule.xlsx",
                "../../data/doctors_schedule.xlsx",
                os.path.join(os.path.dirname(__file__), "..", "data", "doctors_schedule.xlsx")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.schedule_df = pd.read_excel(path)
                    print(f"Loaded doctor schedule from {path}")
                    break
            else:
                print("Doctor schedule not found.")
                self.schedule_df = pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error loading doctor schedule: {e}")
            self.schedule_df = pd.DataFrame()
    
    def find_available_slots(self, 
                            patient_data: Dict[str, Any], 
                            lookup_result: PatientLookupResult) -> Tuple[str, List[AppointmentSlot]]:
        """
        Find available appointment slots based on patient preferences and type
        
        Args:
            patient_data: Patient preferences (doctor, location)
            lookup_result: Patient lookup result (new vs returning)
            
        Returns:
            - response_message: What to tell the user
            - available_slots: List of available AppointmentSlot objects
        """
        if self.schedule_df is None or self.schedule_df.empty:
            return "Doctor schedule is not available. Please try again later.", []
        
        preferred_doctor = patient_data.get('preferred_doctor')
        preferred_location = patient_data.get('location')
        required_duration = lookup_result.appointment_duration
        
        if not preferred_doctor or not preferred_location:
            return "Missing doctor or location preference.", []
        
        # Filter available slots
        available_slots = self._filter_available_slots(
            preferred_doctor, preferred_location, required_duration
        )
        
        if not available_slots:
            return self._get_no_slots_message(preferred_doctor, preferred_location), []
        
        # Convert to AppointmentSlot objects
        appointment_slots = self._create_appointment_slots(available_slots)
        
        response_message = self._format_available_slots_message(
            available_slots, preferred_doctor, preferred_location, required_duration
        )
        
        return response_message, appointment_slots
    
    def _filter_available_slots(self, doctor: str, location: str, duration: int) -> List[Dict]:
        """Filter available slots based on preferences"""
        try:
            if duration == 60:  # New patient needs 2 consecutive slots
                # Find slots where current slot + next slot are both available
                available_slots = self._find_consecutive_slots(doctor, location)
            else:  # Returning patient needs 1 slot
                filtered_df = self.schedule_df[
                    (self.schedule_df['doctor'] == doctor) &
                    (self.schedule_df['location'] == location) &
                    (self.schedule_df['available'] == True) &
                    (self.schedule_df['duration_available'] >= duration)
                ].copy()
                available_slots = filtered_df.to_dict('records')
            
            # Sort by date and time
            if available_slots:
                df = pd.DataFrame(available_slots)
                df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
                df = df.sort_values('datetime')
                available_slots = df.head(7).to_dict('records')
            
            return available_slots
            
        except Exception as e:
            print(f"Error filtering available slots: {e}")
            return []

    def _find_consecutive_slots(self, doctor: str, location: str) -> List[Dict]:
        """Find consecutive 30-minute slots for new patients (60 minutes total)"""
        consecutive_slots = []
        
        try:
            # Get all available slots for this doctor/location
            doctor_slots = self.schedule_df[
                (self.schedule_df['doctor'] == doctor) &
                (self.schedule_df['location'] == location) &
                (self.schedule_df['available'] == True) &
                (self.schedule_df['duration_available'] >= 30)
            ].copy()
            
            if doctor_slots.empty:
                return consecutive_slots
            
            # Sort by date and time
            doctor_slots['datetime'] = pd.to_datetime(doctor_slots['date'] + ' ' + doctor_slots['time'])
            doctor_slots = doctor_slots.sort_values('datetime')
            
            # Check for consecutive slots
            for i in range(len(doctor_slots) - 1):
                current_slot = doctor_slots.iloc[i]
                next_slot = doctor_slots.iloc[i + 1]
                
                # Check if slots are consecutive (30 minutes apart)
                current_time = pd.to_datetime(current_slot['date'] + ' ' + current_slot['time'])
                next_time = pd.to_datetime(next_slot['date'] + ' ' + next_slot['time'])
                
                if (next_time - current_time).total_seconds() == 1800:  # 30 minutes = 1800 seconds
                    # Found consecutive slots - add the first one
                    consecutive_slots.append(current_slot.to_dict())
            
            return consecutive_slots
            
        except Exception as e:
            print(f"Error finding consecutive slots: {e}")
            return []
    
    def _create_appointment_slots(self, available_slots: List[Dict]) -> List[AppointmentSlot]:
        """Convert filtered data to AppointmentSlot objects"""
        appointment_slots = []
        
        for slot in available_slots:
            try:
                appointment_slot = AppointmentSlot(
                    doctor=slot['doctor'],
                    location=slot['location'],
                    date=slot['date'],
                    time=slot['time'],
                    duration_available=slot['duration_available']
                )
                appointment_slots.append(appointment_slot)
            except Exception as e:
                print(f"Error creating appointment slot: {e}")
                continue
        
        return appointment_slots
    
    def _format_available_slots_message(self, 
                                      available_slots: List[Dict], 
                                      doctor: str, 
                                      location: str, 
                                      duration: int) -> str:
        """Format the message showing available slots"""
        
        if not available_slots:
            return "No available slots found."
        
        message = (
            f"**Available Appointment Slots**\n\n"
            f"**Doctor**: {doctor}\n"
            f"**Location**: {location}\n"
            f"**Duration**: {duration} minutes\n\n"
            f"Here are your available options:\n\n"
        )
        
        for i, slot in enumerate(available_slots, 1):
            # Format the date and time nicely
            date_obj = datetime.strptime(slot['date'], '%Y-%m-%d')
            formatted_date = date_obj.strftime('%A, %B %d, %Y')
            formatted_time = slot['time']
            
            message += (
                f"{i}. **{formatted_date}** at **{formatted_time}**\n"
            )
        
        message += (
            f"\nPlease choose a slot number (1-{len(available_slots)}) "
            f"or let me know if you'd like different options."
        )
        
        return message
    
    def _get_no_slots_message(self, doctor: str, location: str) -> str:
        """Message when no slots are available"""
        return (
            f" **No Available Slots**\n\n"
            f"Sorry, there are no available appointments with {doctor} at {location}.\n\n"
            f"Would you like me to:\n"
            f"1. Check availability with other doctors?\n"
            f"2. Check availability at other locations?\n"
            f"3. Check availability on different dates?"
        )
    
    def update_doctor_schedule(self, selected_slot: AppointmentSlot, patient_type: str):
        """Mark the booked slot(s) as unavailable in the Excel file"""
        try:
            if patient_type == "new":
                # New patient needs 60 minutes = 2 consecutive 30-minute slots
                # Find both the selected slot AND the next 30-minute slot
                
                # Get the selected slot time
                selected_time = selected_slot.time
                
                # Calculate next 30-minute slot
                from datetime import datetime, timedelta
                time_obj = datetime.strptime(selected_time, '%H:%M').time()
                next_time_obj = (datetime.combine(datetime.today(), time_obj) + timedelta(minutes=30)).time()
                next_time = next_time_obj.strftime('%H:%M')
                
                # Update BOTH slots
                mask1 = (
                    (self.schedule_df['doctor'] == selected_slot.doctor) &
                    (self.schedule_df['location'] == selected_slot.location) &
                    (self.schedule_df['date'] == selected_slot.date) &
                    (self.schedule_df['time'] == selected_slot.time)
                )
                
                mask2 = (
                    (self.schedule_df['doctor'] == selected_slot.doctor) &
                    (self.schedule_df['location'] == selected_slot.location) &
                    (self.schedule_df['date'] == selected_slot.date) &
                    (self.schedule_df['time'] == next_time)
                )
                
                # Mark both slots as unavailable
                self.schedule_df.loc[mask1, 'available'] = False
                self.schedule_df.loc[mask1, 'duration_available'] = 0
                self.schedule_df.loc[mask1, 'status'] = "Fully Booked (New Patient)"
                
                self.schedule_df.loc[mask2, 'available'] = False
                self.schedule_df.loc[mask2, 'duration_available'] = 0
                self.schedule_df.loc[mask2, 'status'] = "Fully Booked (New Patient)"
                
            else:
                # Returning patient needs 30 minutes = 1 slot
                mask = (
                    (self.schedule_df['doctor'] == selected_slot.doctor) &
                    (self.schedule_df['location'] == selected_slot.location) &
                    (self.schedule_df['date'] == selected_slot.date) &
                    (self.schedule_df['time'] == selected_slot.time)
                )
                
                # Mark slot as unavailable
                self.schedule_df.loc[mask, 'available'] = False
                self.schedule_df.loc[mask, 'duration_available'] = 0
                self.schedule_df.loc[mask, 'status'] = "Fully Booked (Returning Patient)"
            
            # Save the updated schedule
            self.schedule_df.to_excel(self.schedule_excel_path, index=False)
            print(f"✅ Updated doctor schedule: {patient_type} patient booked {selected_slot.time}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating doctor schedule: {e}")
            return False
    
    def book_appointment_slot(self, 
                             slot_index: int, 
                             available_slots: List[AppointmentSlot],
                             patient_type: str = "new") -> Tuple[str, Optional[AppointmentSlot]]:
        """
        Book a specific appointment slot
        
        Args:
            slot_index: User's choice (1-based index)
            available_slots: List of available slots
            
        Returns:
            - response_message: Confirmation or error message
            - selected_slot: The booked AppointmentSlot object
        """
        try:
            # Convert 1-based index to 0-based
            actual_index = slot_index - 1
            
            if actual_index < 0 or actual_index >= len(available_slots):
                return f"❌ Please choose a valid slot number (1-{len(available_slots)}).", None
            
            selected_slot = available_slots[actual_index]
            
            # 🆕 ADD THIS: Handle multi-slot bookings for new patients
            if patient_type == "new":
                # New patients need 2 consecutive 30-minute slots
                success = self._book_consecutive_slots(selected_slot, patient_type)
            else:
                # Returning patients only need 1 slot
                success = self.update_doctor_schedule(selected_slot, patient_type)
            
            if not success:
                return f"❌ Failed to book appointment slot.", None
            
            # Format confirmation message
            date_obj = datetime.strptime(selected_slot.date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%A, %B %d, %Y')
            
            confirmation_message = (
                f"✅ **Appointment Slot Booked!**\n\n"
                f"**Date**: {formatted_date}\n"
                f"**Time**: {selected_slot.time}\n"
                f"**Doctor**: {selected_slot.doctor}\n"
                f"**Location**: {selected_slot.location}\n"
                f"**Duration**: {30 if patient_type == 'returning' else 60} minutes\n"
                f"**Patient Type**: {patient_type.title()}\n\n"
                f"Great! Now let me collect your insurance information..."
            )
            
            return confirmation_message, selected_slot
            
        except Exception as e:
            return f"❌ Error booking appointment slot: {e}", None

    def _book_consecutive_slots(self, selected_slot: AppointmentSlot, patient_type: str) -> bool:
        """Book consecutive slots for new patients (60 minutes)"""
        try:
            # Find the next consecutive slot (30 minutes later)
            current_time = datetime.strptime(selected_slot.time, '%H:%M')
            next_time = (current_time + timedelta(minutes=30)).strftime('%H:%M')
            
            # Check if next slot exists and is available
            next_slot_mask = (
                (self.schedule_df['doctor'] == selected_slot.doctor) &
                (self.schedule_df['location'] == selected_slot.location) &
                (self.schedule_df['date'] == selected_slot.date) &
                (self.schedule_df['time'] == next_time) &
                (self.schedule_df['available'] == True)
            )
            
            if not next_slot_mask.any():
                print(f"❌ Next slot {next_time} not available for consecutive booking")
                return False
            
            # Book both slots
            success1 = self.update_doctor_schedule(selected_slot, "consecutive_first")
            success2 = self.update_doctor_schedule(
                AppointmentSlot(
                    doctor=selected_slot.doctor,
                    location=selected_slot.location,
                    date=selected_slot.date,
                    time=next_time,
                    duration_available=30
                ), 
                "consecutive_second"
            )
            
            return success1 and success2
            
        except Exception as e:
            print(f"❌ Error booking consecutive slots: {e}")
            return False
    
    def get_schedule_summary(self) -> str:
        """Get a summary of the loaded schedule"""
        if self.schedule_df is None or self.schedule_df.empty:
            return " No schedule data loaded"
        
        total_slots = len(self.schedule_df)
        available_slots = len(self.schedule_df[self.schedule_df['available'] == True])
        
        return (
            f" **Schedule Summary**\n"
            f"Total Slots: {total_slots}\n"
            f"Available Slots: {available_slots}\n"
            f"Unavailable Slots: {total_slots - available_slots}"
        )

# Test function
def test_scheduling_agent():
    """Test the scheduling agent functionality"""
    print("Testing Scheduling Agent...\n")
    
    agent = SchedulingAgent()
    
    # Test data
    patient_data = {
        'patient_name': 'John Smith',
        'preferred_doctor': 'Dr. Naveen',
        'location': 'Gachibowli'
    }
    
    # Mock lookup result
    class MockLookupResult:
        def __init__(self):
            self.patient_type = "returning"
            self.appointment_duration = 30
    
    lookup_result = MockLookupResult()
    
    print("=== Testing Available Slots ===")
    response, slots = agent.find_available_slots(patient_data, lookup_result)
    print(f"Response: {response}")
    print(f"Available Slots: {len(slots)}")
    
    if slots:
        print("\n=== Testing Slot Booking ===")
        # Fix: Pass patient_type correctly
        booking_response, selected_slot = agent.book_appointment_slot(1, slots, lookup_result.patient_type)
        print(f"Booking Response: {booking_response}")
        if selected_slot:
            print(f"Selected Slot: {selected_slot}")
    
    print(f"\n{agent.get_schedule_summary()}")

if __name__ == "__main__":
    test_scheduling_agent()