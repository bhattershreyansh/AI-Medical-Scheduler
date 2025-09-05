#!/usr/bin/env python3
"""
Simple test script to test real email sending with PDF attachment
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append('.')

from utils.notification import MockNotificationService

def test_real_email():
    """Test real email sending with PDF attachment"""
    
    print("�� Testing Real Email with PDF Attachment...")
    print("=" * 50)
    
    # Check if email credentials are set
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    
    if not email_user or not email_password:
        print("❌ Email credentials not found in .env file!")
        print("Please add EMAIL_USER and EMAIL_PASSWORD to your .env file")
        return False
    
    print(f"✅ Email credentials found: {email_user}")
    
    # Create notification service with real email (mock_mode=False)
    notification_service = MockNotificationService(mock_mode=False)
    
    # Test data
    test_email = "shreyanshs070700@gmail.com"  # Change this to your test email
    test_name = "Shreyansh Bhatter"
    test_date = "2025-01-15"
    test_time = "10:00"
    
    print(f"\nSending test email to: {test_email}")
    print(f"With PDF attachment: data/New-Patient-Intake-Form.pdf")
    
    # Test 1: Send intake forms email with PDF
    print("\n=== Test 1: Intake Forms Email with PDF ===")
    success = notification_service.send_intake_forms_email(
        patient_email=test_email,
        patient_name=test_name,
        appointment_date=test_date,
        appointment_time=test_time,
        form_path="data/New-Patient-Intake-Form.pdf"
    )
    
    if success:
        print("✅ Intake forms email sent successfully!")
    else:
        print("❌ Failed to send intake forms email")
        return False
    
    # Test 2: Send appointment confirmation
    print("\n=== Test 2: Appointment Confirmation Email ===")
    appointment_data = {
        'date': test_date,
        'time': test_time,
        'doctor': 'Dr. Test',
        'location': 'Test Office',
        'duration': 60
    }
    
    success = notification_service.send_appointment_confirmation(
        patient_email=test_email,
        patient_name=test_name,
        appointment_data=appointment_data
    )
    
    if success:
        print("✅ Appointment confirmation email sent successfully!")
    else:
        print("❌ Failed to send appointment confirmation email")
        return False
    
    print("\n🎉 All email tests passed!")
    print(f"Check your email at: {test_email}")
    return True

def test_mock_email():
    """Test mock email sending (for comparison)"""
    
    print("\n�� Testing Mock Email (for comparison)...")
    print("=" * 50)
    
    # Create notification service with mock email (mock_mode=True)
    notification_service = MockNotificationService(mock_mode=True)
    
    # Test data
    test_email = "shreyanshs070700@gmail.com"
    test_name = "Shreyansh Bhatter"
    test_date = "2025-01-15"
    test_time = "10:00"
    
    # Test intake forms email
    success = notification_service.send_intake_forms_email(
        patient_email=test_email,
        patient_name=test_name,
        appointment_date=test_date,
        appointment_time=test_time
    )
    
    if success:
        print("✅ Mock email test passed!")
    else:
        print("❌ Mock email test failed!")
        return False
    
    return True

def main():
    """Main test function"""
    
    print("🏥 Medical Scheduler - Email Test Script")
    print("=" * 60)
    
    # Check if PDF file exists
    pdf_path = "data/New-Patient-Intake-Form.pdf"
    if not os.path.exists(pdf_path):
        print(f"⚠️ Warning: PDF file not found at {pdf_path}")
        print("The email will still be sent but without attachment")
    else:
        print(f"✅ PDF file found: {pdf_path}")
    
    # Ask user which test to run
    print("\nChoose test type:")
    print("1. Test Mock Email (safe, no real emails)")
    print("2. Test Real Email (sends actual emails)")
    print("3. Test Both")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        test_mock_email()
    elif choice == "2":
        test_real_email()
    elif choice == "3":
        test_mock_email()
        test_real_email()
    else:
        print("Invalid choice. Running mock test only.")
        test_mock_email()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()