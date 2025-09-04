#!/usr/bin/env python3
"""
Test script to identify and fix Excel export issues
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append('.')

def test_excel_export_functionality():
    """Test the Excel export functionality step by step"""
    
    print("🧪 Testing Excel Export Functionality...\n")
    
    # Test 1: Import the ExcelExportService
    try:
        from utils.excel_export import ExcelExportService
        print("✅ Successfully imported ExcelExportService")
    except Exception as e:
        print(f"❌ Failed to import ExcelExportService: {e}")
        return False
    
    # Test 2: Create service instance
    try:
        service = ExcelExportService()
        print("✅ Successfully created ExcelExportService instance")
    except Exception as e:
        print(f"❌ Failed to create ExcelExportService instance: {e}")
        return False
    
    # Test 3: Create test appointment data
    test_appointment_data = {
        'appointment_id': 'APT_20250903_001',
        'patient_id': 'PAT_001',
        'patient_name': 'John Smith',
        'patient_email': 'john.smith@test.com',
        'patient_phone': '(555) 123-4567',
        'date_of_birth': '12/25/1990',
        'doctor': 'Dr. Naveen',
        'location': 'Gachibowli',
        'appointment_date': '2025-01-15',
        'appointment_time': '14:00',
        'duration': 60,
        'insurance_carrier': 'Blue Cross Blue Shield',
        'member_id': 'BC123456789',
        'group_number': 'GRP001',
        'status': 'confirmed',
        'confirmed_at': datetime.now().isoformat(),
        'created_at': datetime.now().isoformat(),
        'reminders_sent': 0,
        'form_sent': False
    }
    
    print("✅ Created test appointment data")
    
    # Test 4: Export single appointment
    try:
        response, success = service.export_appointment_data(test_appointment_data)
        print(f"Export Result: {'✅ Success' if success else '❌ Failed'}")
        print(f"Response: {response}")
        
        if not success:
            print("❌ Single appointment export failed")
            return False
            
    except Exception as e:
        print(f"❌ Exception during single appointment export: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Check if file was created
    appointments_file = "data/appointments.xlsx"
    if os.path.exists(appointments_file):
        print(f"✅ Excel file created: {appointments_file}")
        
        # Test reading the file back
        try:
            import pandas as pd
            df = pd.read_excel(appointments_file)
            print(f"✅ File readable, contains {len(df)} rows")
            print(f"Columns: {list(df.columns)}")
            
            if len(df) > 0:
                print("✅ Data successfully written to Excel")
                print(f"Sample data: {df.iloc[0].to_dict()}")
            else:
                print("❌ Excel file is empty")
                return False
                
        except Exception as e:
            print(f"❌ Error reading Excel file: {e}")
            return False
    else:
        print(f"❌ Excel file not created: {appointments_file}")
        return False
    
    # Test 6: Generate admin report
    try:
        admin_response, admin_success = service.generate_admin_review_report([test_appointment_data])
        print(f"Admin Report Result: {'✅ Success' if admin_success else '❌ Failed'}")
        print(f"Admin Response: {admin_response}")
        
        if not admin_success:
            print("❌ Admin report generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Exception during admin report generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 All Excel export tests passed!")
    return True

def test_confirmation_agent_integration():
    """Test the confirmation agent's Excel export integration"""
    
    print("\n🧪 Testing Confirmation Agent Excel Integration...\n")
    
    try:
        from agents.confirmation_agent import ConfirmationAgent
        print("✅ Successfully imported ConfirmationAgent")
    except Exception as e:
        print(f"❌ Failed to import ConfirmationAgent: {e}")
        return False
    
    # Create test data
    patient_info = {
        'patient_name': 'Jane Doe',
        'email': 'jane.doe@test.com',
        'phone': '(555) 987-6543',
        'date_of_birth': '05/15/1985'
    }
    
    insurance_info = {
        'primary_carrier': 'Aetna',
        'member_id': 'AT987654321',
        'group_number': 'GRP002'
    }
    
    selected_slot = {
        'date': '2025-01-16',
        'time': '10:30',
        'doctor': 'Dr. Naresh',
        'location': 'Jubliee Hills',
        'duration_available': 30
    }
    
    appointment_data = {
        'date': '2025-01-16',
        'time': '10:30',
        'doctor': 'Dr. Naresh',
        'location': 'Jubliee Hills'
    }
    
    try:
        agent = ConfirmationAgent(mock_mode=True)
        print("✅ Successfully created ConfirmationAgent instance")
        
        # Test confirmation
        response, success, confirmation_record = agent.confirm_appointment(
            appointment_data, patient_info, insurance_info, selected_slot
        )
        
        print(f"Confirmation Result: {'✅ Success' if success else '❌ Failed'}")
        
        if success:
            print("✅ Appointment confirmed successfully")
            
            # Test Excel export
            export_response, export_success = agent.export_to_excel(confirmation_record)
            print(f"Excel Export Result: {'✅ Success' if export_success else '❌ Failed'}")
            print(f"Export Response: {export_response}")
            
            if export_success:
                print("✅ Excel export from confirmation agent successful")
                return True
            else:
                print("❌ Excel export from confirmation agent failed")
                return False
        else:
            print("❌ Appointment confirmation failed")
            return False
            
    except Exception as e:
        print(f"❌ Exception during confirmation agent test: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    
    print("🔍 Checking Dependencies...\n")
    
    required_packages = [
        'pandas',
        'openpyxl',
        'langchain_groq',
        'pydantic',
        'faker'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - installed")
        except ImportError:
            print(f"❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("Please install them with: pip install " + " ".join(missing_packages))
        return False
    else:
        print("\n✅ All dependencies are installed")
        return True

if __name__ == "__main__":
    print("🚀 Excel Export Diagnostic Test\n")
    
    # Check dependencies first
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing packages.")
        sys.exit(1)
    
    # Test Excel export functionality
    if not test_excel_export_functionality():
        print("❌ Excel export functionality test failed.")
        sys.exit(1)
    
    # Test confirmation agent integration
    if not test_confirmation_agent_integration():
        print("❌ Confirmation agent integration test failed.")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Excel export is working correctly.")