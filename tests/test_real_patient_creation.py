#!/usr/bin/env python3
"""Test actual patient creation with proper ID incrementing"""

import sys
sys.path.append('.')

def test_real_patient_creation():
    print("🧪 Testing Real Patient Creation with ID Incrementing...\n")
    
    try:
        from agents.lookup_agent import LookupAgent
        
        lookup_agent = LookupAgent()
        
        print(f"Initial patient count: {len(lookup_agent.patients_df)}")
        
        # Test patients
        test_patients = [
            {
                'patient_name': 'Alice Test',
                'date_of_birth': '01/01/1990',
                'phone': '5551111111',
                'email': 'alice@test.com'
            },
            {
                'patient_name': 'Bob Test',
                'date_of_birth': '02/02/1991', 
                'phone': '5552222222',
                'email': 'bob@test.com'
            },
            {
                'patient_name': 'Charlie Test',
                'date_of_birth': '03/03/1992',
                'phone': '5553333333', 
                'email': 'charlie@test.com'
            }
        ]
        
        created_ids = []
        
        for i, patient_data in enumerate(test_patients):
            print(f"\n--- Creating Patient {i+1}: {patient_data['patient_name']} ---")
            
            # This will create the patient and add to database
            response, lookup_result = lookup_agent.search_patient(patient_data)
            
            patient_id = lookup_result.patient_id
            created_ids.append(patient_id)
            
            print(f"Created patient ID: {patient_id}")
            print(f"Patient count now: {len(lookup_agent.patients_df)}")
        
        print(f"\n📊 Summary:")
        print(f"Created patient IDs: {created_ids}")
        
        # Check if IDs are incrementing properly
        if len(set(created_ids)) == len(created_ids):
            print("✅ All patient IDs are unique")
            
            # Check if they're incrementing
            numbers = []
            for pid in created_ids:
                if pid.startswith('PAT_'):
                    num = int(pid.split('_')[1])
                    numbers.append(num)
            
            if numbers == sorted(numbers) and all(numbers[i] == numbers[i-1] + 1 for i in range(1, len(numbers))):
                print("✅ Patient IDs are incrementing correctly")
                return True
            else:
                print(f"❌ Patient IDs not incrementing properly: {numbers}")
                return False
        else:
            print(f"❌ Duplicate patient IDs found: {created_ids}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_real_patient_creation()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")