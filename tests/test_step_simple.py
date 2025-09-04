#!/usr/bin/env python3
"""
Test the step-by-step conversation without LLM
"""

import sys
sys.path.append('.')

def test_step_by_step_logic():
    """Test the step-by-step logic without LLM"""
    
    print("🧪 Testing Step-by-Step Logic...\n")
    
    # Mock the greeting agent logic
    class MockGreetingAgent:
        def __init__(self):
            self.collected_data = {}
            self.current_field = 0
            self.fields = ['patient_name', 'date_of_birth', 'phone', 'email', 'preferred_doctor', 'location']
        
        def get_greeting_message(self):
            return "👋 Welcome! Let's start step by step.\n\nFirst, could you please tell me your **full name** (first and last name)?"
        
        def _validate_name(self, name):
            name = name.strip()
            parts = name.split()
            if len(parts) >= 2:
                self.collected_data['patient_name'] = ' '.join(part.title() for part in parts)
                return True, f"✅ Got it! Your name is **{self.collected_data['patient_name']}**."
            else:
                return False, "Please provide both your first and last name."
        
        def _get_next_field_prompt(self):
            field_name = self.fields[self.current_field]
            prompts = {
                'date_of_birth': "What's your **date of birth**? Please use MM/DD/YYYY format (e.g., 12/25/1990).",
                'phone': "What's your **phone number**?",
                'email': "What's your **email address**?",
                'preferred_doctor': "Which **doctor** would you like to see?\n\n**Available doctors:**\n• Dr. Naveen\n• Dr. Naresh\n• Dr. Aish\n• Dr. Shreyansh",
                'location': "Which **location** would you prefer?\n\n**Available locations:**\n• Gachibowli\n• Jubliee Hills\n• Banjara Hills"
            }
            return prompts.get(field_name, "Please provide the requested information.")
        
        def process_step(self, user_input):
            if self.current_field == 0:  # Name
                success, response = self._validate_name(user_input)
                if success:
                    self.current_field += 1
                    if self.current_field < len(self.fields):
                        next_prompt = self._get_next_field_prompt()
                        return f"{response}\n\n{next_prompt}", False
                    else:
                        return "🎉 All information collected!", True
                return response, False
            else:
                # For demo, just accept other inputs
                field_name = self.fields[self.current_field]
                self.collected_data[field_name] = user_input
                self.current_field += 1
                
                if self.current_field < len(self.fields):
                    next_prompt = self._get_next_field_prompt()
                    return f"✅ Got it! **{user_input}**\n\n{next_prompt}", False
                else:
                    return "🎉 All information collected!", True
    
    agent = MockGreetingAgent()
    
    # Test the flow
    print(f"🤖 Agent: {agent.get_greeting_message()}\n")
    
    test_inputs = [
        "John Smith",
        "01/15/1990", 
        "5551234567",
        "john@test.com",
        "Dr. Naveen",
        "Gachibowli"
    ]
    
    for user_input in test_inputs:
        print(f"👤 User: {user_input}")
        response, is_complete = agent.process_step(user_input)
        print(f"🤖 Agent: {response}\n")
        
        if is_complete:
            print(f"✅ Collected Data: {agent.collected_data}")
            return True
    
    return False

if __name__ == "__main__":
    success = test_step_by_step_logic()
    print(f"\nTest Result: {'✅ Success' if success else '❌ Failed'}")