#!/usr/bin/env python3
"""
Test that new patients are properly saved to CSV
"""

import sys
import os
sys.path.append('.')

def test_new_patient_csv_save():
    """Test that new patients are saved to CSV and become returning patients"""
    
    print("🧪 Testing New Patient CSV Save Functionality...\n")
    
    try:
        from agents.lookup_agent import LookupAgent
        import pandas as pd
        
        # Create lookup agent
        lookup_agent = LookupAgent()
        
        # Check initial patient count
        initial_count = len(lookup_agent.patients_df)
        print(f"Initial patient count: {initial_count}")
        
        # Test new patient data
        new_patient_data = {
            'patient_name': 'Jane Smith Test',
            'date_of_birth': '05/15/1990',
            'phone': '5551234567',
            'email': 'jane.test@example.com',
            'address': '123 Test St',
            'insurance_provider': 'Test Insurance'
        }
        
        print(f"Testing with patient: {new_patient_data['patient_name']}")
        
        # First search - should be new patient
        response1, lookup_result1 = lookup_agent.search_patient(new_patient_data)
        
        print(f"First search result: {lookup_result1.patient_type}")
        print(f"Patient ID: {lookup_result1.patient_id}")
        
        # Check if patient count increased
        new_count = len(lookup_agent.patients_df)
        print(f"Patient count after first search: {new_count}")
        
        if new_count > initial_count:
            print("✅ New patient was added to in-memory database")
            
            # Check if CSV was updated
            try:
                df = pd.read_csv("data/patients.csv")
                if 'Jane Smith Test' in df['first_name'].values or 'Jane Smith Test' in (df['first_name'] + ' ' + df['last_name']).values:
                    print("✅ New patient was saved to CSV file")
                    
                    # Now test second search - should be returning patient
                    print("\n--- Testing Second Search (Should be Returning Patient) ---")
                    
                    # Create a fresh lookup agent to simulate new session
                    lookup_agent2 = LookupAgent()
                    
                    response2, lookup_result2 = lookup_agent2.search_patient(new_patient_data)
                    
                    print(f"Second search result: {lookup_result2.patient_type}")
                    
                    if lookup_result2.patient_type == "returning":
                        print("✅ Patient is now correctly identified as returning patient!")
                        return True
                    else:
                        print("❌ Patient should be returning but is still marked as new")
                        return False
                        
                else:
                    print("❌ New patient not found in CSV file")
                    return False
            except Exception as e:
                print(f"❌ Error reading CSV: {e}")
                return False
        else:
            print("❌ New patient was not added to database")
            return False
            
    except Exception as e:
        print(f"❌ Error testing new patient CSV save: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing New Patient CSV Save Functionality\n")
    
    success = test_new_patient_csv_save()
    
    print(f"\n📊 Test Result: {'✅ Pass' if success else '❌ Fail'}")
    
    if success:
        print("\n🎉 New patient CSV save functionality is working correctly!")
        print("New patients will now become returning patients on their next visit.")
    else:
        print("\n❌ There's still an issue with the new patient CSV save functionality.")