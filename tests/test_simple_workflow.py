#!/usr/bin/env python3
"""
Test the simple workflow with manual data
"""

import sys
sys.path.append('.')

from main_simple import MedicalSchedulerApp
from agents import create_initial_state

def test_simple_workflow():
    """Test the workflow with manual data injection"""
    
    print("🧪 Testing Simple Workflow...\n")
    
    app = MedicalSchedulerApp()
    
    # Manually inject patient data to bypass LLM issues
    from models import PatientInfo
    
    try:
        patient_info = PatientInfo(
            patient_name="Aviral Gupta",
            date_of_birth="07/07/2004",
            preferred_doctor="Dr. Naveen",
            location="Banjara Hills",
            phone="9876543210",
            email="aviral@test.com"
        )
        
        print(f"✅ PatientInfo created: {patient_info.patient_name}")
        
        # Inject into state
        app.state["patient_info"] = patient_info
        app.state["current_step"] = "lookup"
        
        # Test lookup
        lookup_response = app._do_lookup()
        print(f"Lookup Response: {lookup_response}")
        
        # Test scheduling
        scheduling_response = app._do_scheduling()
        print(f"Scheduling Response: {scheduling_response}")
        
        # Check if slots were found
        slots = app.state.get("available_slots", [])
        print(f"Available Slots: {len(slots)}")
        
        if slots:
            print("✅ Workflow test successful - slots found!")
            return True
        else:
            print("❌ No slots found")
            return False
            
    except Exception as e:
        print(f"❌ Error in workflow test: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_workflow()
    print(f"\nTest Result: {'✅ Success' if success else '❌ Failed'}")