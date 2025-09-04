#!/usr/bin/env python3
"""Test patient ID generation"""

import sys
sys.path.append('.')

def test_patient_id():
    print("🧪 Testing Patient ID Generation...\n")
    
    try:
        from agents.lookup_agent import LookupAgent
        
        lookup_agent = LookupAgent()
        
        # Check existing patient IDs
        print("Sample existing patient IDs:")
        for i, (_, row) in enumerate(lookup_agent.patients_df.head(5).iterrows()):
            print(f"  {row['patient_id']}")
        
        # Test ID generation
        print("\nTesting new patient ID generation:")
        
        for i in range(3):
            new_id = lookup_agent._generate_next_patient_id()
            print(f"Generated ID {i+1}: {new_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_patient_id()