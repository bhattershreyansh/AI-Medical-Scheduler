#!/usr/bin/env python3
"""Test that confirmation agent uses the correct patient ID"""

import sys
sys.path.append('.')

def test_confirmation_patient_id():
    print("🧪 Testing Confirmation Agent Patient ID...\n")
    
    try:
        from agents.confirmation_agent import ConfirmationAgent
        from agents.lookup_agent import LookupAgent
        
        # Create agents
        lookup_agent = LookupAgent()
        confirmation_agent = ConfirmationAgent()
        
        # Step 1: Create a new patient and get their ID
        print("1. Creating new patient...")
        patient_data = {
            'patient_name': 'Test Confirmation Patient',
            'date_of_birth': '01/01/1996',
            'phone': '5558888888',
            'email': 'testconf@example.com'
        }
        
        response, lookup_result = lookup_agent.search_patient(patient_data)
        patient_id_from_lookup = lookup_result.patient_id
        print(f"Patient ID from lookup: {patient_id_from_lookup}")
        
        # Step 2: Create appointment data
        appointment_data = {
            'appointment_type': 'consultation',
            'date': '2025-09-05',
            'time': '10:00:00',
            'doctor': 'Dr. Test',
            'location': 'Test Office'
        }
        
        # Step 3: Create patient info with the correct patient ID
        patient_info = {
            'patient_name': patient_data['patient_name'],
            'email': patient_data['email'],
            'phone': patient_data['phone'],
            'date_of_birth': patient_data['date_of_birth'],
            'patient_id': patient_id_from_lookup  # Pass the correct patient ID
        }
        
        insurance_info = {
            'primary_carrier': 'Test Insurance',
            'member_id': 'TEST123',
            'group_number': 'GRP999'
        }
        
        selected_slot = {
            'date': '2025-09-05',
            'time': '10:00:00',
            'doctor': 'Dr. Test',
            'location': 'Test Office',
            'duration_available': 60
        }
        
        # Step 4: Confirm appointment
        print("\n2. Confirming appointment...")
        response, success, confirmation_record = confirmation_agent.confirm_appointment(
            appointment_data, patient_info, insurance_info, selected_slot
        )
        
        if success and confirmation_record:
            patient_id_in_appointment = confirmation_record.get('patient_id')
            print(f"Patient ID in appointment: {patient_id_in_appointment}")
            
            if patient_id_from_lookup == patient_id_in_appointment:
                print("✅ SUCCESS: Patient IDs match! Appointment uses correct patient ID from lookup.")
                print(f"✅ Both use: {patient_id_from_lookup}")
                return True
            else:
                print(f"❌ FAILED: Patient ID mismatch!")
                print(f"  Lookup: {patient_id_from_lookup}")
                print(f"  Appointment: {patient_id_in_appointment}")
                return False
        else:
            print("❌ FAILED: Appointment confirmation failed")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_confirmation_patient_id()
    print(f"\n{'🎉 ALL TESTS PASSED' if success else '❌ TESTS FAILED'}")