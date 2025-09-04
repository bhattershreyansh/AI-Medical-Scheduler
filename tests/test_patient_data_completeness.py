#!/usr/bin/env python3
"""Test that patient data is saved completely with all details"""

import sys
sys.path.append('.')

def test_patient_data_completeness():
    print("🧪 Testing Patient Data Completeness...\n")
    
    try:
        from agents.lookup_agent import LookupAgent
        import pandas as pd
        
        # Create lookup agent
        lookup_agent = LookupAgent()
        
        # Test patient data with all fields
        patient_data = {
            'patient_name': 'Complete Test Patient',
            'date_of_birth': '01/01/1997',
            'phone': '5557777777',
            'email': 'complete@test.com',
            'address': '123 Complete St, Test City, TC 12345',
            'emergency_contact': 'Emergency Contact (555) 888-9999'
        }
        
        print("1. Creating new patient with complete data...")
        response, lookup_result = lookup_agent.search_patient(patient_data)
        
        patient_id = lookup_result.patient_id
        print(f"Created patient ID: {patient_id}")
        
        # Check if patient was added to in-memory dataframe
        patient_row = lookup_agent.patients_df[lookup_agent.patients_df['patient_id'] == patient_id]
        
        if len(patient_row) > 0:
            patient_record = patient_row.iloc[0]
            print(f"\n📋 Patient Record in Database:")
            print(f"  Patient ID: {patient_record['patient_id']}")
            print(f"  Name: {patient_record['first_name']} {patient_record['last_name']}")
            print(f"  DOB: {patient_record['dob']}")
            print(f"  Phone: {patient_record['phone']}")
            print(f"  Email: {patient_record['email']}")
            print(f"  Address: {patient_record['address']}")
            print(f"  Emergency Contact: {patient_record['emergency_contact']}")
            print(f"  Patient Type: {patient_record['patient_type']}")
            print(f"  Last Visit: {patient_record['last_visit']}")
            
            # Check completeness
            missing_fields = []
            if not patient_record['phone']: missing_fields.append('phone')
            if not patient_record['email']: missing_fields.append('email')
            if not patient_record['address']: missing_fields.append('address')
            if not patient_record['patient_type']: missing_fields.append('patient_type')
            
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
                return False
            else:
                print("✅ All basic patient fields are populated")
            
            # Test insurance update
            print(f"\n2. Testing insurance info update...")
            insurance_info = {
                'primary_carrier': 'Complete Insurance Co',
                'member_id': 'COMP123456',
                'group_number': 'GRP999'
            }
            
            lookup_agent.update_patient_insurance_info(patient_id, insurance_info)
            
            # Check updated record
            updated_row = lookup_agent.patients_df[lookup_agent.patients_df['patient_id'] == patient_id]
            if len(updated_row) > 0:
                updated_record = updated_row.iloc[0]
                print(f"  Insurance Carrier: {updated_record['insurance_carrier']}")
                print(f"  Member ID: {updated_record['member_id']}")
                print(f"  Group Number: {updated_record['group_number']}")
                
                if (updated_record['insurance_carrier'] == 'Complete Insurance Co' and
                    updated_record['member_id'] == 'COMP123456' and
                    updated_record['group_number'] == 'GRP999'):
                    print("✅ Insurance information updated successfully")
                else:
                    print("❌ Insurance information not updated properly")
                    return False
            
            # Test patient type update
            print(f"\n3. Testing patient type update to returning...")
            lookup_agent.mark_patient_as_returning(patient_id)
            
            # Check updated patient type
            final_row = lookup_agent.patients_df[lookup_agent.patients_df['patient_id'] == patient_id]
            if len(final_row) > 0:
                final_record = final_row.iloc[0]
                print(f"  Patient Type: {final_record['patient_type']}")
                
                if final_record['patient_type'] == 'returning':
                    print("✅ Patient type updated to returning successfully")
                    return True
                else:
                    print("❌ Patient type not updated properly")
                    return False
            
        else:
            print("❌ Patient not found in database")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_patient_data_completeness()
    print(f"\n{'🎉 ALL TESTS PASSED' if success else '❌ TESTS FAILED'}: Patient data completeness")