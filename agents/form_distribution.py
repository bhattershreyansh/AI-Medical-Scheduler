import sys
import os
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime

# Safe path handling
try:
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir.parent))
except NameError:
    sys.path.append('..')

from utils.notification import MockNotificationService

class FormDistributionAgent:
    """Assignment-accurate form distribution agent for sending patient intake forms"""
    
    def __init__(self, mock_mode: bool = True):
        self.notification_service = MockNotificationService(mock_mode=mock_mode)
        self.forms_sent = []
        # Assignment only provides one form
        self.form_template = 'New-Patient-Intake-Form.pdf'
    
    def send_intake_forms(self, 
                          patient_email: str, 
                          patient_name: str,
                          appointment_data: Dict[str, Any],
                          patient_type: str = "new") -> Tuple[str, bool]:
        """
        Send patient intake form via email (assignment requirement)
        
        Args:
            patient_email: Patient's email address
            patient_name: Patient's full name
            appointment_data: Appointment details
            patient_type: "new" or "returning" patient
            
        Returns:
            - response_message: What to tell the user
            - success: Whether form was sent successfully
        """
        
        try:
            # Assignment only provides New-Patient-Intake-Form.pdf
            # So we send this form to all patients
            form_to_send = self.form_template
            
            # Send the form via email
            email_sent = self.notification_service.send_intake_forms_email(
                patient_email,
                patient_name,
                appointment_data.get('date', 'N/A'),
                appointment_data.get('time', 'N/A')
            )
            
            if email_sent:
                # Log the form sent
                form_record = {
                    'patient_email': patient_email,
                    'patient_name': patient_name,
                    'patient_type': patient_type,
                    'form_sent': form_to_send,
                    'appointment_date': appointment_data.get('date'),
                    'appointment_time': appointment_data.get('time'),
                    'sent_at': datetime.now().isoformat(),
                    'status': 'sent'
                }
                self.forms_sent.append(form_record)
                
                response_message = self._get_form_sent_message(
                    patient_name, form_to_send, appointment_data, patient_type
                )
                return response_message, True
            else:
                return "Failed to send intake form. Please try again.", False
                
        except Exception as e:
            print(f"Error sending intake form: {e}")
            return f"Error sending form: {str(e)}", False
    
    def resend_intake_form(self, 
                           patient_email: str, 
                           patient_name: str,
                           appointment_data: Dict[str, Any]) -> Tuple[str, bool]:
        """Resend intake form to patient"""
        
        return self.send_intake_forms(patient_email, patient_name, appointment_data, "returning")
    
    def _get_form_sent_message(self, 
                               patient_name: str, 
                               form_sent: str, 
                               appointment_data: Dict[str, Any],
                               patient_type: str) -> str:
        """Generate message confirming form was sent"""
        
        appointment_date = appointment_data.get('date', 'N/A')
        appointment_time = appointment_data.get('time', 'N/A')
        
        # Simplified message for better user experience
        message = (
            f"**Intake Forms Sent!**\n\n"
            f"Hi {patient_name}! Your {'new patient' if patient_type == 'new' else 'patient'} intake forms "
            f"have been sent to your email.\n\n"
            f"**Please complete them before your appointment on {appointment_date} at {appointment_time}.**\n\n"
            f"This will help speed up your check-in process!"
        )
        
        return message
    
    def check_form_status(self, patient_email: str) -> Dict[str, Any]:
        """Check the status of form sent to a patient"""
        
        for form_record in self.forms_sent:
            if form_record['patient_email'] == patient_email:
                return {
                    'status': 'found',
                    'form_sent': form_record['form_sent'],
                    'sent_at': form_record['sent_at'],
                    'patient_type': form_record['patient_type']
                }
        
        return {'status': 'not_found'}
    
    def get_forms_summary(self) -> str:
        """Get a summary of all forms sent"""
        
        if not self.forms_sent:
            return "**Forms Summary**: No forms have been sent yet."
        
        summary = f"**Form Distribution Summary**\n\n"
        summary += f"**Total Forms Sent**: {len(self.forms_sent)}\n\n"
        
        # Group by patient type
        new_patients = [f for f in self.forms_sent if f['patient_type'] == 'new']
        returning_patients = [f for f in self.forms_sent if f['patient_type'] == 'returning']
        
        summary += f"**New Patients**: {len(new_patients)}\n"
        summary += f"**Returning Patients**: {len(returning_patients)}\n\n"
        
        summary += "**Form Type**: New-Patient-Intake-Form.pdf (sent to all patients)\n\n"
        
        summary += "**Recent Forms Sent**:\n"
        for form_record in self.forms_sent[-5:]:  # Show last 5
            summary += (
                f"• {form_record['patient_name']} ({form_record['patient_type']}) - "
                f"{form_record['sent_at'][:10]}\n"
            )
        
        return summary
    
    def send_reminder_for_form(self, 
                               patient_email: str, 
                               patient_name: str,
                               appointment_data: Dict[str, Any]) -> Tuple[str, bool]:
        """Send a reminder to complete intake form"""
        
        reminder_message = (
            f"📋 **Intake Form Reminder**\n\n"
            f"Hi {patient_name},\n\n"
            f"This is a friendly reminder to complete your New Patient Intake Form before your appointment.\n\n"
            f"**Appointment**: {appointment_data.get('date')} at {appointment_data.get('time')}\n\n"
            f"**Form to Complete**:\n"
            f"• New-Patient-Intake-Form.pdf\n\n"
            f"**Why Complete Form Early?**\n"
            f"Faster check-in process\n"
            f"More time with your doctor\n"
            f"Reduced wait times\n\n"
            f"**Need Form Again?**\n"
            f"Reply with 'NEED FORM' and we'll resend it immediately.\n\n"
            f"Thank you!"
        )
        
        # Send reminder email
        email_sent = self.notification_service.send_email_reminder(
            patient_email,
            patient_name,
            reminder_message,
            "Intake Form Reminder - Complete Before Your Appointment"
        )
        
        return (
            f"Form reminder sent to {patient_email}",
            email_sent
        )
    
    def get_form_template(self) -> str:
        """Get the available form template (assignment provides only one)"""
        return self.form_template
    
    def clear_forms_history(self):
        """Clear forms sent history"""
        self.forms_sent = []

# Test function
def test_form_distribution_agent():
    """Test the form distribution agent functionality"""
    print("Testing Form Distribution Agent (Assignment-Accurate)...\n")
    
    agent = FormDistributionAgent(mock_mode=True)
    
    # Test data
    patient_email = "john.smith@fakeemail.com"
    patient_name = "John Smith"
    appointment_data = {
        'date': '2025-01-15',
        'time': '14:00',
        'doctor': 'Dr. Naveen',
        'location': 'Gachibowli'
    }
    
    print("=== Testing New Patient Form ===")
    response, success = agent.send_intake_forms(
        patient_email, patient_name, appointment_data, "new"
    )
    print(f"Form Sent Result: {'Success' if success else 'Failed'}")
    print(f"Response: {response}")
    
    print("\n=== Testing Returning Patient Form ===")
    response, success = agent.send_intake_forms(
        "jane.doe@fakeemail.com", "Jane Doe", appointment_data, "returning"
    )
    print(f"Form Sent Result: {'Success' if success else 'Failed'}")
    print(f"Response: {response}")
    
    print("\n=== Testing Form Status Check ===")
    status = agent.check_form_status(patient_email)
    print(f"Form Status: {status}")
    
    print("\n=== Testing Form Reminder ===")
    reminder_response, reminder_sent = agent.send_reminder_for_form(
        patient_email, patient_name, appointment_data
    )
    print(f"Reminder Result: {reminder_response}")
    print(f"Reminder Sent: {'Yes' if reminder_sent else 'No'}")
    
    print(f"\n{agent.get_forms_summary()}")

if __name__ == "__main__":
    test_form_distribution_agent()