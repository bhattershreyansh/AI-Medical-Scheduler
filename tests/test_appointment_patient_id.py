#!/usr/bin/env python3
"""Test that appointments use the correct patient ID from lookup"""

import sys
sys.path.append('.')

def test_appointment_patient_id():
    print("🧪 Testing Appointment Patient ID...\n")
    
    try:
        from main_simple import MedicalSchedulerApp
        
        # Create workflow
        workflow = MedicalSchedulerApp()
        
        print("=== Testing New Patient Appointment ===")
        
        # Step 1: Patient lookup (new patient)
        print("\n1. Patient Lookup...")
        response = workflow.handle_patient_lookup({
            'patient_name': 'Test Patient ID',
            'date_of_birth': '01/01/1995',
            'phone': '5559999999',
            'email': 'testid@example.com'
        })
        
        patient_id_from_lookup = workflow.state["lookup_result"].patient_id
        print(f"Patient ID from lookup: {patient_id_from_lookup}")
        
        # Step 2: Get available slots
        print("\n2. Getting available slots...")
        response = workflow.handle_scheduling({
            'preferred_doctor': 'Dr. Smith',
            'location': 'Main Office'
        })
        
        # Step 3: Select a slot (simulate user selection)
        if workflow.state.get("available_slots"):
            workflow.state["selected_slot"] = workflow.state["available_slots"][0]
            print(f"Selected slot: {workflow.state['selected_slot'].date} at {workflow.state['selected_slot'].time}")
        
        # Step 4: Insurance info
        print("\n3. Insurance info...")
        response = workflow.handle_insurance({
            'primary_carrier': 'Test Insurance',
            'member_id': 'TEST123',
            'group_number': 'GRP999'
        })
        
        # Step 5: Confirm appointment
        print("\n4. Confirming appointment...")
        response = workflow.handle_confirmation()
        
        # Check the patient ID in the confirmation record
        if workflow.state.get("confirmation_record"):
            patient_id_in_appointment = workflow.state["confirmation_record"].get('patient_id')
            print(f"Patient ID in appointment: {patient_id_in_appointment}")
            
            if patient_id_from_lookup == patient_id_in_appointment:
                print("✅ Patient IDs match! Appointment uses correct patient ID from lookup.")
                return True
            else:
                print(f"❌ Patient ID mismatch!")
                print(f"  Lookup: {patient_id_from_lookup}")
                print(f"  Appointment: {patient_id_in_appointment}")
                return False
        else:
            print("❌ No confirmation record found")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_appointment_patient_id()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Patient ID consistency test")