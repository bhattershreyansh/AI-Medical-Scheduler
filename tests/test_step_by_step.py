#!/usr/bin/env python3
"""
Test the step-by-step greeting agent
"""

import sys
sys.path.append('.')

from agents.greeting_agent import GreetingAgent
from agents import create_initial_state

def test_step_by_step():
    """Test the step-by-step conversation flow"""
    
    print("🧪 Testing Step-by-Step Greeting Agent...\n")
    
    agent = GreetingAgent()
    state = create_initial_state()
    
    # Start with greeting
    greeting = agent.get_greeting_message()
    print(f"🤖 Agent: {greeting}\n")
    
    # Test step-by-step inputs
    test_inputs = [
        "John Smith",           # Name
        "01/15/1990",          # DOB
        "5551234567",          # Phone
        "john@test.com",       # Email
        "Dr. Naveen",          # Doctor
        "Gachibowli"           # Location
    ]
    
    for i, user_input in enumerate(test_inputs):
        print(f"👤 User: {user_input}")
        response, is_complete, data = agent.process_input(user_input, state)
        print(f"🤖 Agent: {response}\n")
        
        if is_complete:
            print(f"✅ All Data Collected: {data}")
            
            # Try to create PatientInfo model
            try:
                from models import PatientInfo
                patient_info = PatientInfo(**data)
                print(f"✅ PatientInfo created successfully: {patient_info.patient_name}")
                return True
            except Exception as e:
                print(f"❌ Error creating PatientInfo: {e}")
                return False
    
    print("❌ Conversation not completed")
    return False

if __name__ == "__main__":
    success = test_step_by_step()
    print(f"\nTest Result: {'✅ Success' if success else '❌ Failed'}")