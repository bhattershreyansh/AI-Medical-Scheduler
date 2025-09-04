#!/usr/bin/env python3
"""
Test the fixed greeting agent
"""

import sys
sys.path.append('.')

from agents.greeting_agent import GreetingAgent
from agents import create_initial_state
from dotenv import load_dotenv
load_dotenv()

def test_greeting_fix():
    """Test the greeting agent with the problematic input"""
    
    print("🧪 Testing Fixed Greeting Agent...\n")
    
    agent = GreetingAgent()
    state = create_initial_state()
    
    # Test the problematic input
    user_input = "im aviral gupta and my dob is 7th july 2004 preferred is DR naveen and location is banjara hills phone is 9876543210 email is aviral@test.com"
    
    print(f"User Input: {user_input}")
    
    response, is_complete, data = agent.process_input(user_input, state)
    
    print(f"Response: {response}")
    print(f"Is Complete: {is_complete}")
    print(f"Extracted Data: {data}")
    
    if is_complete:
        # Try to create PatientInfo model
        try:
            from models import PatientInfo
            patient_info = PatientInfo(**data)
            print(f"✅ PatientInfo created successfully: {patient_info}")
            return True
        except Exception as e:
            print(f"❌ Error creating PatientInfo: {e}")
            return False
    else:
        print("❌ Information collection not complete")
        return False

if __name__ == "__main__":
    success = test_greeting_fix()
    print(f"\nTest Result: {'✅ Success' if success else '❌ Failed'}")