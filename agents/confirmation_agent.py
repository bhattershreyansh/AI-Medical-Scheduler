import sys
import os
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime
import json

# Safe path handling
try:
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir.parent))
except NameError:
    sys.path.append('..')

from utils.notification import MockNotificationService

class ConfirmationAgent:
    """Assignment-accurate confirmation agent for finalizing appointments and Excel export"""
    
    def __init__(self, mock_mode: bool = True):
        self.notification_service = MockNotificationService(mock_mode=mock_mode)
        self.confirmed_appointments = []
        self.excel_exports = []
    
    def confirm_appointment(self, 
                           appointment_data: Dict[str, Any],
                           patient_info: Dict[str, Any],
                           insurance_info: Dict[str, Any],
                           selected_slot: Dict[str, Any]) -> Tuple[str, bool, Dict[str, Any]]:
        """
        Confirm the complete appointment booking
        
        Args:
            appointment_data: Complete appointment information
            patient_info: Patient details from greeting agent
            insurance_info: Insurance details from insurance agent
            selected_slot: Selected appointment slot from scheduling agent
            
        Returns:
            - response_message: Confirmation message
            - success: Whether confirmation was successful
            - confirmation_record: Complete confirmation data
        """
        
        try:
            # Generate unique appointment ID
            appointment_id = self._generate_appointment_id()
            
            # Use patient ID from lookup result (passed in patient_info)
            patient_id = patient_info.get('patient_id', f"PAT_{len(self.confirmed_appointments) + 1:03d}")
            
            # Create confirmation record with ALL required fields
            confirmation_record = {
                'appointment_id': appointment_id,
                'patient_id': patient_id,  # Fixed: consistent format
                'patient_info': patient_info,
                'insurance_info': insurance_info,
                'appointment_slot': selected_slot,
                'status': 'confirmed',
                'confirmed_at': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat(),  # Added: created timestamp
                'reminders_scheduled': False,
                'forms_sent': False,
                'excel_exported': False,
                'reminders_sent': 0,
                'form_sent': False,
                # Direct access fields for Excel export
                'appointment_date': selected_slot.get('date'),
                'appointment_time': selected_slot.get('time'),
                'patient_name': patient_info.get('patient_name', ''),
                'patient_email': patient_info.get('email', ''),
                'patient_phone': patient_info.get('phone', ''),
                'date_of_birth': patient_info.get('date_of_birth', ''),
                'doctor': selected_slot.get('doctor', ''),
                'location': selected_slot.get('location', ''),
                'duration': selected_slot.get('duration_available', ''),
                'insurance_carrier': insurance_info.get('primary_carrier', ''),
                'member_id': insurance_info.get('member_id', ''),
                'group_number': insurance_info.get('group_number', ''),
            }
            
            # Send confirmation email
            confirmation_email_sent = self._send_confirmation_email(
                patient_info['email'],
                patient_info['patient_name'],
                confirmation_record
            )
            
            # Send confirmation SMS
            confirmation_sms_sent = self._send_confirmation_sms(
                patient_info['phone'],
                confirmation_record
            )
            
            # Update confirmation record
            confirmation_record['email_sent'] = confirmation_email_sent
            confirmation_record['sms_sent'] = confirmation_sms_sent
            
            # Store confirmation
            self.confirmed_appointments.append(confirmation_record)
            
            # Generate confirmation message
            response_message = self._get_confirmation_message(confirmation_record)
            
            return response_message, True, confirmation_record
            
        except Exception as e:
            print(f"❌ Error confirming appointment: {e}")
            return f"❌ Error confirming appointment: {str(e)}", False, {}
    
    def _generate_appointment_id(self) -> str:
        """Generate unique appointment ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = str(len(self.confirmed_appointments) + 1).zfill(3)
        return f"APT_{timestamp}_{random_suffix}"
    
    def _send_confirmation_email(self, 
                                patient_email: str, 
                                patient_name: str,
                                confirmation_record: Dict[str, Any]) -> bool:
        """Send appointment confirmation email"""
        
        appointment_data = {
            'date': confirmation_record['appointment_slot']['date'],
            'time': confirmation_record['appointment_slot']['time'],
            'doctor': confirmation_record['appointment_slot']['doctor'],
            'location': confirmation_record['appointment_slot']['location'],
            'duration': confirmation_record['appointment_slot']['duration_available']
        }
        
        return self.notification_service.send_appointment_confirmation(
            patient_email, patient_name, appointment_data
        )
    
    def _send_confirmation_sms(self, 
                               patient_phone: str, 
                               confirmation_record: Dict[str, Any]) -> bool:
        """Send appointment confirmation SMS"""
        
        slot = confirmation_record['appointment_slot']
        message = (
            f"✅ Appointment Confirmed!\n"
            f"Date: {slot['date']}\n"
            f"Time: {slot['time']}\n"
            f"Doctor: {slot['doctor']}\n"
            f"Location: {slot['location']}\n"
            f"ID: {confirmation_record['appointment_id']}"
        )
        
        return self.notification_service.send_sms_reminder(patient_phone, message)
    
    def _get_confirmation_message(self, confirmation_record: Dict[str, Any]) -> str:
        """Generate user-friendly confirmation message"""
        
        slot = confirmation_record['appointment_slot']
        patient_name = confirmation_record['patient_info']['patient_name']
        
        message = (
            f"🎉 **Appointment Confirmed!**\n\n"
            f"Hi **{patient_name}**! Your appointment has been successfully booked.\n\n"
            f"📅 **Appointment Details:**\n"
            f"• **Date**: {slot['date']}\n"
            f"• **Time**: {slot['time']}\n"
            f"• **Doctor**: {slot['doctor']}\n"
            f"• **Location**: {slot['location']}\n"
            f"• **Duration**: {slot['duration_available']} minutes\n"
            f"• **Appointment ID**: {confirmation_record['appointment_id']}\n\n"
            f"📧 **Confirmations Sent:**\n"
            f"• Email confirmation: {'✅ Sent' if confirmation_record['email_sent'] else '❌ Failed'}\n"
            f"• SMS confirmation: {'✅ Sent' if confirmation_record['sms_sent'] else '❌ Failed'}"
        )
        
        return message
    
    def export_to_excel(self, confirmation_record: Dict[str, Any]) -> Tuple[str, bool]:
        """Export appointment data to Excel"""
        try:
            from utils.excel_export import ExcelExportService
            
            excel_service = ExcelExportService()
            
            # Export appointment data
            response_message, success = excel_service.export_appointment_data(confirmation_record)
            
            if success:
                # Update confirmation record
                confirmation_record['excel_exported'] = True
                
                # 🆕 ADD THIS: Update admin report after successful export
                self._update_admin_report()
                
                # Store export record
                export_data = {
                    'appointment_id': confirmation_record['appointment_id'],
                    'patient_name': confirmation_record['patient_info']['patient_name'],
                    'exported_at': datetime.now().isoformat(),
                    'status': 'success'
                }
                self.excel_exports.append(export_data)
            
            return response_message, success
            
        except Exception as e:
            print(f"❌ Error exporting to Excel: {e}")
            return f"❌ Error exporting to Excel: {str(e)}", False
    
    def _update_admin_report(self):
        """Update admin review report with latest data"""
        try:
            from utils.excel_export import ExcelExportService
            
            excel_service = ExcelExportService()
            
            # Get all confirmed appointments for comprehensive admin report
            all_appointments = []
            for appointment in self.confirmed_appointments:
                all_appointments.append(appointment)
            
            # Generate updated admin report with ALL data
            admin_response, admin_success = excel_service.generate_admin_review_report(all_appointments)
            
            if admin_success:
                print(f"✅ Admin report updated successfully")
                print(f"   Total appointments: {len(all_appointments)}")
                print(f"   Report file: {excel_service.admin_report_file}")
                
                # Log the update for tracking
                self._log_admin_report_update(len(all_appointments))
            else:
                print(f"❌ Admin report update failed: {admin_response}")
                
        except Exception as e:
            print(f"❌ Error updating admin report: {e}")
            # Don't fail the appointment confirmation if admin report fails

    def _log_admin_report_update(self, appointment_count: int):
        """Log admin report updates for tracking"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'admin_report_updated',
            'appointments_count': appointment_count,
            'status': 'success'
        }
        
        # You could save this to a log file or database
        print(f"📊 Admin report update logged: {log_entry}")
    
    def get_confirmation_summary(self) -> str:
        """Get summary of all confirmed appointments"""
        
        if not self.confirmed_appointments:
            return "📋 **Confirmation Summary**: No appointments confirmed yet."
        
        summary = f"�� **Appointment Confirmation Summary**\n\n"
        summary += f"**Total Confirmed**: {len(self.confirmed_appointments)}\n"
        summary += f"**Total Excel Exports**: {len(self.excel_exports)}\n\n"
        
        summary += "**Recent Confirmations**:\n"
        for appointment in self.confirmed_appointments[-5:]:  # Show last 5
            summary += (
                f"• {appointment['appointment_id']} - "
                f"{appointment['patient_info']['patient_name']} - "
                f"{appointment['appointment_slot']['date']} - "
                f"{appointment['status']}\n"
            )
        
        return summary
    
    def get_excel_export_data(self) -> List[Dict[str, Any]]:
        """Get all Excel export data for admin review"""
        return self.excel_exports.copy()
    
    def clear_confirmation_history(self):
        """Clear confirmation and export history"""
        self.confirmed_appointments = []
        self.excel_exports = []

# Test function
def test_confirmation_agent():
    """Test the confirmation agent functionality"""
    print("🧪 Testing Confirmation Agent...\n")
    
    agent = ConfirmationAgent(mock_mode=True)
    
    # Test data
    appointment_data = {
        'date': '2025-01-15',
        'time': '14:00',
        'doctor': 'Dr. Naveen',
        'location': 'Gachibowli'
    }
    
    patient_info = {
        'patient_name': 'John Smith',
        'email': 'john.smith@fakeemail.com',
        'phone': '(555) 123-4567',
        'date_of_birth': '12/25/1990'
    }
    
    insurance_info = {
        'primary_carrier': 'Blue Cross Blue Shield',
        'member_id': 'BC123456789',
        'group_number': 'GRP001'
    }
    
    selected_slot = {
        'date': '2025-01-15',
        'time': '14:00',
        'doctor': 'Dr. Naveen',
        'location': 'Gachibowli',
        'duration_available': 60
    }
    
    print("=== Testing Appointment Confirmation ===")
    response, success, confirmation_record = agent.confirm_appointment(
        appointment_data, patient_info, insurance_info, selected_slot
    )
    print(f"Confirmation Result: {'✅ Success' if success else '❌ Failed'}")
    print(f"Response: {response}")
    
    if success:
        print("\n=== Testing Excel Export ===")
        export_response, export_success = agent.export_to_excel(confirmation_record)
        print(f"Excel Export Result: {'✅ Success' if export_success else '❌ Failed'}")
        print(f"Export Response: {export_response}")
        
        print("\n=== Testing Confirmation Summary ===")
        print(agent.get_confirmation_summary())
        
        print("\n=== Testing Excel Export Data ===")
        export_data = agent.get_excel_export_data()
        print(f"Export Data: {export_data}")

if __name__ == "__main__":
    test_confirmation_agent()