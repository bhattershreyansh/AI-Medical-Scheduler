import sys
import os
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Safe path handling
try:
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir.parent))
except NameError:
    sys.path.append('..')

from models import InsuranceInfo

class InsuranceAgent:
    """Assignment-accurate insurance agent for collecting insurance information"""
    
    def __init__(self):
        self.required_fields = ['primary_carrier', 'member_id', 'group_number']
        self.current_field_index = 0
        self.collected_data = {}
    
    def get_insurance_greeting(self, patient_name: str) -> str:
        """Initial greeting for insurance collection"""
        return (
            f"**Insurance Information Collection**\n\n"
            f"Hi {patient_name}! Now I need to collect your insurance information "
            f"to complete your appointment booking.\n\n"
            f"Please provide your **primary insurance carrier** (e.g., Blue Cross Blue Shield, Aetna, Cigna)."
        )
    
    def process_input(self, user_input: str) -> Tuple[str, bool, Optional[Dict]]:
        """
        Process user input and collect insurance information
        
        Returns:
            - response_message: What to say to the user
            - is_complete: Whether all required info is collected
            - collected_data: Raw insurance data
        """
        # Handle None input
        if user_input is None:
            return "I didn't catch that. Could you please repeat?", False, None
            
        user_input = user_input.strip()
        
        if not user_input:
            return "I didn't catch that. Could you please repeat?", False, None
        
        # Handle the current field being collected
        current_field = self.required_fields[self.current_field_index]
        response, success = self._collect_field(current_field, user_input)
        
        if success:
            self.current_field_index += 1
            
            # Check if we have all required information
            if self.current_field_index >= len(self.required_fields):
                return self._get_completion_message(), True, self.collected_data.copy()
            else:
                # Ask for the next field
                next_field = self.required_fields[self.current_field_index]
                return self._get_next_field_prompt(next_field), False, None
        else:
            return response, False, None
    
    def _collect_field(self, field_name: str, value: str) -> Tuple[str, bool]:
        """Collect and validate a specific insurance field"""
        
        if field_name == 'primary_carrier':
            return self._validate_carrier(value)
        elif field_name == 'member_id':
            return self._validate_member_id(value)
        elif field_name == 'group_number':
            return self._validate_group_number(value)
        else:
            return f"Unknown field: {field_name}", False
    
    def _validate_carrier(self, carrier: str) -> Tuple[str, bool]:
        """Validate insurance carrier"""
        carrier = carrier.strip()
        if len(carrier) < 2:
            return "Please provide a valid insurance carrier name.", False
        
        # Store the carrier
        self.collected_data['primary_carrier'] = carrier
        return f"✅ Got it! Your primary carrier is {carrier}.", True
    
    def _validate_member_id(self, member_id: str) -> Tuple[str, bool]:
        """Validate member ID"""
        member_id = member_id.strip()
        if len(member_id) < 5:
            return "Member ID must be at least 5 characters long.", False
        
        # Clean the member ID (remove spaces and hyphens)
        clean_id = member_id.replace(' ', '').replace('-', '')
        if not clean_id.isalnum():
            return "Member ID must contain only letters and numbers.", False
        
        self.collected_data['member_id'] = clean_id
        return f"Got it! Your member ID is {clean_id}.", True
    
    def _validate_group_number(self, group_number: str) -> Tuple[str, bool]:
        """Validate group number"""
        group_number = group_number.strip()
        if len(group_number) < 3:
            return "Group number must be at least 3 characters long.", False
        
        # Clean the group number (remove spaces and hyphens)
        clean_group = group_number.replace(' ', '').replace('-', '')
        if not clean_group.isalnum():
            return "Group number must contain only letters and numbers.", False
        
        self.collected_data['group_number'] = clean_group
        return f"Got it! Your group number is {clean_group}.", True
    
    def _get_next_field_prompt(self, field_name: str) -> str:
        """Get the prompt for the next field to collect"""
        prompts = {
            'primary_carrier': "Please provide your **primary insurance carrier** (e.g., Blue Cross Blue Shield, Aetna, Cigna).",
            'member_id': "What is your **member ID**? (This is usually found on your insurance card)",
            'group_number': "Finally, what is your **group number**? (Also found on your insurance card)"
        }
        return prompts.get(field_name, f"Please provide your {field_name}.")
    
    def _get_completion_message(self) -> str:
        """Get the completion message when all fields are collected"""
        return (
            "Perfect! I have all your insurance information:\n\n"
            f"**Primary Carrier**: {self.collected_data['primary_carrier']}\n"
            f"**Member ID**: {self.collected_data['member_id']}\n"
            f"**Group Number**: {self.collected_data['group_number']}\n\n"
            "Now let me confirm your complete appointment booking..."
        )
    
    def create_insurance_info(self) -> InsuranceInfo:
        """Create an InsuranceInfo object from collected data"""
        return InsuranceInfo(
            primary_carrier=self.collected_data['primary_carrier'],
            member_id=self.collected_data['member_id'],
            group_number=self.collected_data['group_number']
        )
    
    def reset(self):
        """Reset the agent state for a new conversation"""
        self.current_field_index = 0
        self.collected_data = {}

# Test function
def test_insurance_agent():
    """Test the insurance agent functionality"""
    print("🧪 Testing Insurance Agent...\n")
    
    agent = InsuranceAgent()
    
    print(agent.get_insurance_greeting("John Smith"))
    
    # Test the conversation flow
    test_inputs = [
        "Blue Cross Blue Shield",
        "BC123456789",
        "GRP001"
    ]
    
    for user_input in test_inputs:
        print(f"\nUser: {user_input}")
        response, is_complete, collected_data = agent.process_input(user_input)
        print(f"Agent: {response}")
        
        if is_complete:
            print(f"\nInsurance Data Collected: {collected_data}")
            
            # Test creating InsuranceInfo object
            try:
                insurance_info = agent.create_insurance_info()
                print(f"InsuranceInfo Created: {insurance_info}")
            except Exception as e:
                print(f"Error creating InsuranceInfo: {e}")
            break

if __name__ == "__main__":
    test_insurance_agent()