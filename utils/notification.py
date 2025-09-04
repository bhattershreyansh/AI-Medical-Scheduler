import os
from typing import Optional, List
from datetime import datetime

class MockNotificationService:
    """Mock notification service for testing with fake data"""
    
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self.sent_emails = []
        self.sent_sms = []
        
        # Real credentials (only used if mock_mode = False)
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
    
    def send_email_reminder(self, 
                           patient_email: str, 
                           patient_name: str, 
                           reminder_message: str,
                           subject: str = "Appointment Reminder") -> bool:
        """Send email reminder (mock or real)"""
        
        if self.mock_mode:
            # Mock mode - just log the email
            email_data = {
                'to': patient_email,
                'patient_name': patient_name,
                'subject': subject,
                'message': reminder_message,
                'sent_at': datetime.now().isoformat(),
                'status': 'mock_sent'
            }
            self.sent_emails.append(email_data)
            
            print(f"📧 [MOCK] Email sent to {patient_email}")
            print(f"   Subject: {subject}")
            print(f"   Patient: {patient_name}")
            print(f"   Status: ✅ Mock Email Sent")
            return True
        else:
            # Real mode - actually send email
            return self._send_real_email(patient_email, patient_name, reminder_message, subject)
    
    def send_sms_reminder(self, 
                         patient_phone: str, 
                         reminder_message: str) -> bool:
        """Send SMS reminder (mock or real)"""
        
        if self.mock_mode:
            # Mock mode - just log the SMS
            sms_data = {
                'to': patient_phone,
                'message': reminder_message,
                'sent_at': datetime.now().isoformat(),
                'status': 'mock_sent'
            }
            self.sent_sms.append(sms_data)
            
            print(f"�� [MOCK] SMS sent to {patient_phone}")
            print(f"   Message: {reminder_message[:50]}...")
            print(f"   Status: ✅ Mock SMS Sent")
            return True
        else:
            # Real mode - actually send SMS
            return self._send_real_sms(patient_phone, reminder_message)
    
    def send_intake_forms_email(self, 
                               patient_email: str, 
                               patient_name: str,
                               appointment_date: str,
                               appointment_time: str) -> bool:
        """Send intake forms email (mock or real)"""
        
        subject = "Patient Intake Forms - Complete Before Your Appointment"
        message = f"Intake forms sent to {patient_name} for appointment on {appointment_date} at {appointment_time}"
        
        return self.send_email_reminder(patient_email, patient_name, message, subject)
    
    def send_appointment_confirmation(self, 
                                    patient_email: str, 
                                    patient_name: str,
                                    appointment_data: dict) -> bool:
        """Send appointment confirmation (mock or real)"""
        
        subject = "Appointment Confirmed - Important Details"
        message = f"Appointment confirmed for {patient_name} on {appointment_data.get('date')} at {appointment_data.get('time')}"
        
        return self.send_email_reminder(patient_email, patient_name, message, subject)
    
    def _send_real_email(self, patient_email: str, patient_name: str, reminder_message: str, subject: str) -> bool:
        """Actually send real email (only called when mock_mode = False)"""
        # This would contain the real email sending code
        # For now, just return False to indicate it's not implemented
        print(f"❌ Real email sending not implemented yet")
        return False
    
    def _send_real_sms(self, patient_phone: str, reminder_message: str) -> bool:
        """Actually send real SMS (only called when mock_mode = False)"""
        # This would contain the real SMS sending code
        # For now, just return False to indicate it's not implemented
        print(f"❌ Real SMS sending not implemented yet")
        return False
    
    def get_notification_summary(self) -> str:
        """Get summary of all sent notifications"""
        summary = f"📊 **Notification Summary**\n\n"
        
        summary += f"�� **Emails Sent**: {len(self.sent_emails)}\n"
        for email in self.sent_emails:
            summary += f"   - {email['to']} ({email['subject']}) - {email['status']}\n"
        
        summary += f"\n�� **SMS Sent**: {len(self.sent_sms)}\n"
        for sms in self.sent_sms:
            summary += f"   - {sms['to']} - {sms['status']}\n"
        
        return summary
    
    def clear_mock_data(self):
        """Clear mock notification history"""
        self.sent_emails = []
        self.sent_sms = []

# For production use, you can create a real notification service
class RealNotificationService(MockNotificationService):
    def __init__(self):
        super().__init__(mock_mode=False)

# Test function
def test_mock_notification_service():
    """Test the mock notification service"""
    print("🧪 Testing Mock Notification Service...\n")
    
    service = MockNotificationService(mock_mode=True)
    
    # Test mock email
    print("=== Testing Mock Email ===")
    success = service.send_email_reminder(
        "john.smith@fakeemail.com",
        "John Smith",
        "This is a test reminder message.",
        "Test Reminder"
    )
    print(f"Mock email result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test mock SMS
    print("\n=== Testing Mock SMS ===")
    success = service.send_sms_reminder(
        "(555) 123-4567",
        "Test SMS reminder message"
    )
    print(f"Mock SMS result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test intake forms
    print("\n=== Testing Intake Forms Email ===")
    success = service.send_intake_forms_email(
        "john.smith@fakeemail.com",
        "John Smith",
        "2025-01-15",
        "14:00"
    )
    print(f"Intake forms result: {'✅ Success' if success else '❌ Failed'}")
    
    # Show summary
    print(f"\n{service.get_notification_summary()}")

if __name__ == "__main__":
    test_mock_notification_service()
