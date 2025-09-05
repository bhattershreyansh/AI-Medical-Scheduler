import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
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
            print(f"   Status:  Mock Email Sent")
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
            print(f"   Status:  Mock SMS Sent")
            return True
        else:
            # Real mode - actually send SMS
            return self._send_real_sms(patient_phone, reminder_message)
    
    def send_intake_forms_email(self, 
                               patient_email: str, 
                               patient_name: str,
                               appointment_date: str,
                               appointment_time: str,
                               form_path: str = "data/New-Patient-Intake-Form.pdf") -> bool:
        """Send intake forms email with PDF attachment (mock or real)"""
        
        subject = "Patient Intake Forms - Complete Before Your Appointment"
        
        if self.mock_mode:
            # Mock mode - just log
            email_data = {
                'to': patient_email,
                'subject': subject,
                'status': ' Mock Email Sent (with PDF attachment)',
                'sent_at': datetime.now().isoformat(),
                'attachment': form_path
            }
            self.sent_emails.append(email_data)
            print(f" [MOCK] Email sent to {patient_email}")
            print(f"   Subject: {subject}")
            print(f"   Patient: {patient_name}")
            print(f"   Attachment: {form_path}")
            print(f"   Status: {email_data['status']}")
            return True
        else:
            # Real mode - send actual email with PDF attachment
            return self._send_real_email_with_attachment(
                patient_email, patient_name, appointment_date, appointment_time, form_path, subject
            )
    
    def send_appointment_confirmation(self, 
                                    patient_email: str, 
                                    patient_name: str,
                                    appointment_data: dict) -> bool:
        """Send appointment confirmation (mock or real)"""
        
        subject = "Appointment Confirmed - Important Details"
        
        if self.mock_mode:
            # Mock mode - just log
            email_data = {
                'to': patient_email,
                'subject': subject,
                'status': ' Mock Email Sent',
                'sent_at': datetime.now().isoformat()
            }
            self.sent_emails.append(email_data)
            print(f" [MOCK] Email sent to {patient_email}")
            print(f"   Subject: {subject}")
            print(f"   Patient: {patient_name}")
            print(f"   Status: {email_data['status']}")
            return True
        else:
            # Real mode - send actual email
            return self._send_real_confirmation_email(
                patient_email, patient_name, appointment_data, subject
            )
    
    def _send_real_email(self, patient_email: str, patient_name: str, reminder_message: str, subject: str) -> bool:
        """Actually send real email (only called when mock_mode = False)"""
        # This would contain the real email sending code
        # For now, just return False to indicate it's not implemented
        print(f" Real email sending not implemented yet")
        return False
    
    def _send_real_email_with_attachment(self, 
                                       patient_email: str, 
                                       patient_name: str,
                                       appointment_date: str,
                                       appointment_time: str,
                                       form_path: str,
                                       subject: str) -> bool:
        """Send real email with PDF attachment"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = patient_email
            msg['Subject'] = subject
            
            # Create email body
            body = f"""
Dear {patient_name},

Please find attached your patient intake forms for your upcoming appointment.

 Appointment Date: {appointment_date}
 Appointment Time: {appointment_time}

Please complete these forms and bring them with you to your appointment.
This will help speed up your check-in process.

If you have any questions, please contact our office.

Best regards,
Medical Practice Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach PDF file
            if os.path.exists(form_path):
                with open(form_path, "rb") as attachment:
                    part = MIMEApplication(attachment.read(), Name="New-Patient-Intake-Form.pdf")
                    part['Content-Disposition'] = f'attachment; filename="New-Patient-Intake-Form.pdf"'
                    msg.attach(part)
                print(f" PDF attachment added: {form_path}")
            else:
                print(f" Warning: Intake form not found at {form_path}")
                return False
            
            # Send email
            return self._send_real_email_smtp(msg, patient_email)
            
        except Exception as e:
            print(f" Error sending email with attachment: {e}")
            return False
    
    def _send_real_email_smtp(self, msg: MIMEMultipart, to_email: str) -> bool:
        """Send email using SMTP"""
        try:
            # Create secure connection
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f" Email with PDF attachment sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f" Failed to send email to {to_email}: {e}")
            return False
    
    def _send_real_sms(self, patient_phone: str, reminder_message: str) -> bool:
        """Actually send real SMS (only called when mock_mode = False)"""
        # This would contain the real SMS sending code
        # For now, just return False to indicate it's not implemented
        print(f" Real SMS sending not implemented yet")
        return False
    
    def _send_real_confirmation_email(self, 
                                patient_email: str, 
                                patient_name: str,
                                appointment_data: dict,
                                subject: str) -> bool:
        """Send real appointment confirmation email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = patient_email
            msg['Subject'] = subject
            
            # Create email body
            body = f"""
Dear {patient_name},

Your appointment has been confirmed with the following details:

 Date: {appointment_data.get('date', 'N/A')}
 Time: {appointment_data.get('time', 'N/A')}
 Doctor: {appointment_data.get('doctor', 'N/A')}
 Location: {appointment_data.get('location', 'N/A')}
 Duration: {appointment_data.get('duration', 'N/A')} minutes

Please arrive 15 minutes early for check-in.

If you need to reschedule or cancel, please contact our office.

Best regards,
Medical Practice Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            return self._send_real_email_smtp(msg, patient_email)
            
        except Exception as e:
            print(f" Error sending confirmation email: {e}")
            return False
    
    def get_notification_summary(self) -> str:
        """Get summary of all sent notifications"""
        summary = f"📊 **Notification Summary**\n\n"
        
        summary += f" **Emails Sent**: {len(self.sent_emails)}\n"
        for email in self.sent_emails:
            summary += f"   - {email['to']} ({email['subject']}) - {email['status']}\n"
        
        summary += f"\n **SMS Sent**: {len(self.sent_sms)}\n"
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
