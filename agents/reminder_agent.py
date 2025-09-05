import sys
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json

# Safe path handling
try:
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir.parent))
except NameError:
    sys.path.append('..')

from models import AppointmentBooking
from utils.notification import MockNotificationService

class ReminderAgent:
    """Assignment-accurate reminder system with 3 automated reminders and actions"""
    
    def __init__(self, mock_mode: bool = True):
        self.reminder_types = {
            1: "regular",      # 1st reminder: regular
            2: "form_check",   # 2nd reminder: check if forms filled
            3: "confirmation"  # 3rd reminder: check visit confirmation
        }
        self.reminder_schedule = {
            1: 24,    # 1st reminder: 24 hours before
            2: 2,     # 2nd reminder: 2 hours before  
            3: 1      # 3rd reminder: 1 hour before
        }
        
        # Add notification service
        self.notification_service = MockNotificationService(mock_mode=mock_mode)
    
    def schedule_reminders(self, appointment: AppointmentBooking) -> Dict[str, Any]:
        """Schedule all 3 reminders for an appointment"""
        
        appointment_time = datetime.combine(
            datetime.strptime(appointment.appointment_slot.date, '%Y-%m-%d').date(),
            datetime.strptime(appointment.appointment_slot.time, '%H:%M').time()
        )
        
        reminders = {}
        
        for reminder_num in range(1, 4):
            reminder_time = appointment_time - timedelta(hours=self.reminder_schedule[reminder_num])
            
            reminders[f"reminder_{reminder_num}"] = {
                "type": self.reminder_types[reminder_num],
                "scheduled_time": reminder_time.isoformat(),
                "sent": False,
                "response_received": False,
                "action_required": self._get_action_for_reminder(reminder_num)
            }
        
        return reminders
    
    def _get_action_for_reminder(self, reminder_num: int) -> str:
        """Get the action required for each reminder type"""
        actions = {
            1: "Confirm your appointment",
            2: "Fill out your patient intake forms",
            3: "Confirm you're still coming or cancel if needed"
        }
        return actions.get(reminder_num, "Unknown action")
    
    def send_reminder(self, reminder_data: Dict, appointment: AppointmentBooking) -> str:
        """Send actual reminder via email and SMS"""
        
        reminder_type = reminder_data["type"]
        action = reminder_data["action_required"]
        
        # Generate message content
        if reminder_type == "regular":
            message = self._send_regular_reminder(appointment, action)
        elif reminder_type == "form_check":
            message = self._send_form_check_reminder(appointment, action)
        elif reminder_type == "confirmation":
            message = self._send_confirmation_reminder(appointment, action)
        else:
            return "Unknown reminder type"
        
        # Actually send the notifications using the service
        patient_email = appointment.patient_info.email
        patient_phone = appointment.patient_info.phone
        
        # Send email
        email_sent = self.notification_service.send_email_reminder(
            patient_email, 
            appointment.patient_info.patient_name,
            message,
            f"Appointment Reminder - {reminder_type.title()}"
        )
        
        # Send SMS
        sms_sent = self.notification_service.send_sms_reminder(
            patient_phone,
            message
        )
        
        # Update reminder status
        reminder_data["sent"] = True
        reminder_data["email_sent"] = email_sent
        reminder_data["sms_sent"] = sms_sent
        reminder_data["sent_at"] = datetime.now().isoformat()
        
        return f"Reminder sent via {'Email' if email_sent else 'Email failed'} and {'SMS' if sms_sent else 'SMS failed'}"
    
    def _send_regular_reminder(self, appointment: AppointmentBooking, action: str) -> str:
        """Send 1st reminder (regular)"""
        
        message = (
            f" **Appointment Reminder**\n\n"
            f"Hi {appointment.patient_info.patient_name}!\n\n"
            f"**Reminder**: Your appointment is tomorrow\n"
            f"**Date**: {appointment.appointment_slot.date}\n"
            f"**Time**: {appointment.appointment_slot.time}\n"
            f"**Doctor**: {appointment.appointment_slot.doctor}\n"
            f"**Location**: {appointment.appointment_slot.location}\n\n"
            f"**Action Required**: {action}\n\n"
            f"Please reply with:\n"
            f" CONFIRM - if you're coming\n"
            f" CANCEL - if you need to reschedule\n"
            f" NEED FORMS - if you need intake forms"
        )
        
        return message
    
    def _send_form_check_reminder(self, appointment: AppointmentBooking, action: str) -> str:
        """Send 2nd reminder (check if forms filled)"""
        
        message = (
            f" **Forms Reminder**\n\n"
            f"Hi {appointment.patient_info.patient_name}!\n\n"
            f"**Reminder**: Your appointment is in 2 hours\n"
            f"**Date**: {appointment.appointment_slot.date}\n"
            f"**Time**: {appointment.appointment_slot.time}\n\n"
            f"**Action Required**: {action}\n\n"
            f"Please reply with:\n"
            f"FORMS COMPLETED - if you've filled intake forms\n"
            f"NEED FORMS - if you need forms sent again\n"
            f"CANCEL - if you need to reschedule"
        )
        
        return message
    
    def _send_confirmation_reminder(self, appointment: AppointmentBooking, action: str) -> str:
        """Send 3rd reminder (final confirmation)"""
        
        message = (
            f"⏰ **Final Confirmation**\n\n"
            f"Hi {appointment.patient_info.patient_name}!\n\n"
            f"**Reminder**: Your appointment is in 1 hour\n"
            f"**Date**: {appointment.appointment_slot.date}\n"
            f"**Time**: {appointment.appointment_slot.time}\n"
            f"**Doctor**: {appointment.appointment_slot.doctor}\n"
            f"**Location**: {appointment.appointment_slot.location}\n\n"
            f"**Action Required**: {action}\n\n"
            f"Please reply with:\n"
            f"CONFIRMED - if you're definitely coming\n"
            f" CANCEL - if you need to cancel\n"
            f"CALL US - if you need to speak to someone"
        )
        
        return message
    
    def process_reminder_response(self, response: str, reminder_data: Dict, appointment: AppointmentBooking) -> Tuple[str, Dict]:
        """Process patient response to reminder"""
        
        response_lower = response.lower().strip()
        reminder_type = reminder_data["type"]
        
        # Update reminder status
        reminder_data["response_received"] = True
        reminder_data["patient_response"] = response
        
        if reminder_type == "regular":
            return self._handle_regular_response(response_lower, appointment)
        elif reminder_type == "form_check":
            return self._handle_form_check_response(response_lower, appointment)
        elif reminder_type == "confirmation":
            return self._handle_confirmation_response(response_lower, appointment)
        else:
            return "Unknown reminder type", {}
    
    def _handle_regular_response(self, response: str, appointment: AppointmentBooking) -> Tuple[str, Dict]:
        """Handle response to 1st reminder"""
        
        if "confirm" in response:
            return (
                "**Appointment Confirmed!**\n\n"
                "Great! We'll see you tomorrow. "
                "You'll receive another reminder in 22 hours.",
                {"status": "confirmed", "next_action": "schedule_form_reminder"}
            )
        elif "cancel" in response:
            return (
                "**Appointment Cancelled**\n\n"
                "We've cancelled your appointment. "
                "Please call us to reschedule.",
                {"status": "cancelled", "next_action": "update_calendar"}
            )
        elif "forms" in response:
            return (
                "**Forms Sent**\n\n"
                "I've sent your patient intake forms to your email. "
                "Please complete them before your appointment.",
                {"status": "forms_sent", "next_action": "send_intake_forms"}
            )
        else:
            return (
                "**Response Not Understood**\n\n"
                "Please reply with CONFIRM, CANCEL, or NEED FORMS.",
                {"status": "unclear", "next_action": "resend_reminder"}
            )
    
    def _handle_form_check_response(self, response: str, appointment: AppointmentBooking) -> Tuple[str, Dict]:
        """Handle response to 2nd reminder"""
        
        if "completed" in response:
            return (
                "**Forms Confirmed!**\n\n"
                "Perfect! Your forms are complete. "
                "You'll receive a final confirmation reminder in 1 hour.",
                {"status": "forms_completed", "next_action": "schedule_final_reminder"}
            )
        elif "forms" in response:
            return (
                "**Forms Re-sent**\n\n"
                "I've sent your intake forms again. "
                "Please complete them as soon as possible.",
                {"status": "forms_resent", "next_action": "send_intake_forms"}
            )
        elif "cancel" in response:
            return (
                " **Appointment Cancelled**\n\n"
                "We've cancelled your appointment. "
                "Please call us to reschedule.",
                {"status": "cancelled", "next_action": "update_calendar"}
            )
        else:
            return (
                " **Response Not Understood**\n\n"
                "Please reply with FORMS COMPLETED, NEED FORMS, or CANCEL.",
                {"status": "unclear", "next_action": "resend_reminder"}
            )
    
    def _handle_confirmation_response(self, response: str, appointment: AppointmentBooking) -> Tuple[str, Dict]:
        """Handle response to 3rd reminder"""
        
        if "confirmed" in response:
            return (
                "**Final Confirmation Received!**\n\n"
                "Excellent! We're looking forward to seeing you in 1 hour. "
                "Please arrive 15 minutes early for check-in.",
                {"status": "confirmed", "next_action": "prepare_for_appointment"}
            )
        elif "cancel" in response:
            return (
                "**Appointment Cancelled**\n\n"
                "We've cancelled your appointment. "
                "Please call us to reschedule.",
                {"status": "cancelled", "next_action": "update_calendar"}
            )
        elif "call" in response:
            return (
                "**Call Requested**\n\n"
                "We'll call you shortly to discuss your appointment. "
                "Please keep your phone nearby.",
                {"status": "call_requested", "next_action": "initiate_call"}
            )
        else:
            return (
                " **Response Not Understood**\n\n"
                "Please reply with CONFIRMED, CANCEL, or CALL US.",
                {"status": "unclear", "next_action": "resend_reminder"}
            )
    
    def get_reminder_summary(self, appointment: AppointmentBooking, reminders: Dict) -> str:
        """Get a summary of all reminders for an appointment"""
        
        summary = f" **Reminder Summary for {appointment.patient_info.patient_name}**\n\n"
        
        for reminder_num in range(1, 4):
            reminder_key = f"reminder_{reminder_num}"
            if reminder_key in reminders:
                reminder = reminders[reminder_key]
                status = " Sent" if reminder["sent"] else "⏰ Pending"
                response = f" Responded" if reminder["response_received"] else "⏳ Waiting"
                
                summary += (
                    f"**Reminder {reminder_num}** ({reminder['type']}):\n"
                    f"Status: {status}\n"
                    f"Response: {response}\n"
                    f"Action: {reminder['action_required']}\n\n"
                )
        
        return summary
    
    def get_notification_summary(self) -> str:
        """Get summary of all notifications sent"""
        return self.notification_service.get_notification_summary()
    
    def clear_notification_history(self):
        """Clear notification history"""
        self.notification_service.clear_mock_data()

# Test function
def test_reminder_agent():
    """Test the reminder agent functionality"""
    print("🧪 Testing Reminder Agent with Mock Notifications...\n")
    
    # Create a mock appointment for testing
    class MockAppointment:
        def __init__(self):
            self.patient_info = type('obj', (object,), {
                'patient_name': 'John Smith',
                'email': 'john.smith@fakeemail.com',
                'phone': '(555) 123-4567'
            })()
            self.appointment_slot = type('obj', (object,), {
                'date': '2025-01-15',
                'time': '14:00',
                'doctor': 'Dr. Naveen',
                'location': 'Gachibowli'
            })()
    
    appointment = MockAppointment()
    agent = ReminderAgent(mock_mode=True)
    
    print("=== Testing Reminder Scheduling ===")
    reminders = agent.schedule_reminders(appointment)
    print(f"Reminders scheduled: {len(reminders)}")
    
    print("\n=== Testing Regular Reminder with Notifications ===")
    reminder_1 = reminders["reminder_1"]
    result = agent.send_reminder(reminder_1, appointment)
    print(f"Reminder Result: {result}")
    
    print("\n=== Testing Response Processing ===")
    response, action = agent.process_reminder_response("CONFIRM", reminder_1, appointment)
    print(f"Response: {response}")
    print(f"Action: {action}")
    
    print("\n=== Testing Form Check Reminder with Notifications ===")
    reminder_2 = reminders["reminder_2"]
    result = agent.send_reminder(reminder_2, appointment)
    print(f"Reminder Result: {result}")
    
    print(f"\n{agent.get_reminder_summary(appointment, reminders)}")
    
    print(f"\n{agent.get_notification_summary()}")

if __name__ == "__main__":
    test_reminder_agent()