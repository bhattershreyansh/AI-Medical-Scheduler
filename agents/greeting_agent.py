import sys
import os
import re
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json

# Safe path handling
try:
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir.parent))
except NameError:
    sys.path.append('..')

from models import PatientInfo
from agents import BookingState
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
load_dotenv()

class GreetingAgent:
    """LLM-powered greeting agent with step-by-step data collection"""
    
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("GROQ_MODEL", "llama3-8b-8192")
        )
        self.collected_data = {}
        self.conversation_history = []
        self.current_field = 0
        self.fields = [
            'patient_name',
            'date_of_birth', 
            'phone',
            'email',
            'preferred_doctor',
            'location'
        ]
    
    def get_greeting_message(self) -> str:
        """Initial greeting message"""
        return (
            "👋 Welcome to our Medical Scheduling System!\n\n"
            "I'm here to help you book an appointment step by step.\n\n"
            "Let's start - **What's your full name?** (first and last name)"
        )
    
    def process_input(self, user_input: str, state: BookingState) -> Tuple[str, bool, Optional[Dict]]:
        """Process user input with LLM validation and step-by-step collection"""
        
        # Handle empty input
        if not user_input or not user_input.strip():
            current_field_name = self.fields[self.current_field] if self.current_field < len(self.fields) else "information"
            return self._generate_retry_message(current_field_name), False, None
            
        user_input = user_input.strip()
        self.conversation_history.append(f"Patient: {user_input}")
        
        # Extract and validate current field with LLM
        extracted_data = self._extract_current_field_with_llm(user_input)
        
        if extracted_data:
            # Update collected data
            self.collected_data.update(extracted_data)
            
            # Move to next field
            self._advance_to_next_field()
            
            # Check if all fields collected
            if self.current_field >= len(self.fields):
                return self._get_completion_message(), True, self.collected_data
            else:
                # Ask for next field
                success_msg = self._generate_success_message(extracted_data)
                next_prompt = self._get_next_field_prompt_with_llm()
                return f"{success_msg}\n\n{next_prompt}", False, None
        else:
            # Validation failed, ask for correction
            current_field_name = self.fields[self.current_field]
            return self._generate_error_message_with_llm(user_input, current_field_name), False, None
    
    def _extract_current_field_with_llm(self, user_input: str) -> Optional[Dict]:
        """Use LLM to extract and validate the current field"""
        
        current_field = self.fields[self.current_field]
        
        system_prompt = f"""You are a medical scheduling assistant. Extract and validate the {current_field} from user input.

CURRENT FIELD: {current_field}

VALIDATION RULES:
- patient_name: Must have first AND last name, normalize to Title Case
- date_of_birth: Convert ANY format to MM/DD/YYYY (e.g., "July 4th 1990" → "07/04/1990"), must be valid past date
- phone: Any format acceptable, normalize if possible (e.g., "5551234567" → "(555) 123-4567")
- email: Must contain @ and valid domain
- preferred_doctor: Must be exactly one of ["Dr. Naveen", "Dr. Naresh", "Dr. Aish", "Dr. Shreyansh"]
- location: Must be exactly one of ["Gachibowli", "Jubliee Hills", "Banjara Hills"]

RETURN FORMAT:
If valid: {{"field_name": "validated_value"}}
If invalid: {{}}

EXAMPLES:
Input: "john smith" for patient_name → {{"patient_name": "John Smith"}}
Input: "july 4th 1990" for date_of_birth → {{"date_of_birth": "07/04/1990"}}  
Input: "dr naveen" for preferred_doctor → {{"preferred_doctor": "Dr. Naveen"}}
Input: "john" for patient_name → {{}} (missing last name)
"""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Extract {current_field} from: {user_input}")
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            if response_text.startswith('{') and response_text.endswith('}'):
                extracted = json.loads(response_text)
                
                # Validate that we got the expected field
                if current_field in extracted and extracted[current_field]:
                    return {current_field: extracted[current_field]}
                
        except Exception as e:
            print(f"LLM extraction error: {e}")
        
            return None
    
    def _advance_to_next_field(self):
        """Move to the next field that hasn't been collected"""
        self.current_field += 1
        
        # Skip fields we already have
        while (self.current_field < len(self.fields) and 
               self.fields[self.current_field] in self.collected_data):
            self.current_field += 1
    
    def _generate_success_message(self, extracted_data: Dict) -> str:
        """Generate confirmation message for successfully collected data"""
        
        field_name = list(extracted_data.keys())[0]
        field_value = list(extracted_data.values())[0]
        
        system_prompt = f"""Generate a brief, friendly confirmation message for collecting {field_name}: {field_value}

Make it natural and encouraging. Examples:
- For name: "Perfect! Hi John Smith."  
- For date: "Got it! Born on 07/04/1990."
- For doctor: "Excellent choice! Dr. Naveen it is."

Keep it short (1 line) and positive."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt)])
            return f"✅ {response.content.strip()}"
        except:
            return f"✅ Got it! {field_name.replace('_', ' ').title()}: {field_value}"
    
    def _get_next_field_prompt_with_llm(self) -> str:
        """Generate contextual prompt for next field using LLM"""
        
        if self.current_field >= len(self.fields):
            return ""
        
        next_field = self.fields[self.current_field]
        
        # Use reliable fallback prompts instead of LLM
        fallback_prompts = {
            'patient_name': "What's your full name (first and last)?",
            'date_of_birth': "What's your date of birth? Please use MM/DD/YYYY format.",
            'phone': "What's your phone number?",
            'email': "What's your email address?",
            'preferred_doctor': "Which doctor would you like to see?\n• Dr. Naveen\n• Dr. Naresh\n• Dr. Aish\n• Dr. Shreyansh",
            'location': "Which location works best for you?\n• Gachibowli\n• Jubliee Hills\n• Banjara Hills"
        }
        return fallback_prompts.get(next_field, "Please provide the requested information.")
    
    def _generate_error_message_with_llm(self, user_input: str, field_name: str) -> str:
        """Generate helpful error message using LLM"""
        
        system_prompt = f"""The user provided "{user_input}" for {field_name} but it's not valid.

Generate a helpful, empathetic error message explaining what's wrong and how to fix it.

FIELD REQUIREMENTS:
- patient_name: Need both first AND last name
- date_of_birth: Need valid date in MM/DD/YYYY format, must be in the past
- phone: Need valid phone number with at least 10 digits
- email: Need valid email with @ and domain
- preferred_doctor: Must choose exactly: Dr. Naveen, Dr. Naresh, Dr. Aish, or Dr. Shreyansh
- location: Must choose exactly: Gachibowli, Jubliee Hills, or Banjara Hills

Be encouraging and specific about what's needed."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt)])
            return f"❌ {response.content.strip()}"
        except:
            return f"I couldn't validate that {field_name.replace('_', ' ')}. Could you please try again?"
    
    def _generate_retry_message(self, field_name: str) -> str:
        """Generate retry message for empty input"""
        return f"I didn't catch that. Could you please provide your {field_name.replace('_', ' ')}?"
    
    def _get_completion_message(self) -> str:
        """Generate completion message when all data is collected"""
        
        system_prompt = f"""Generate a professional completion message for collected patient data:
        
        {self.collected_data}
        
        Confirm all details in a structured format and transition to the next step (patient lookup).
        Make it warm and professional."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt)])
            return f"🎉 {response.content.strip()}"
        except:
            # Fallback completion message
        return (
                f"🎉 **Perfect! I have all your information:**\n\n"
                f"• **Name**: {self.collected_data.get('patient_name')}\n"
                f"• **DOB**: {self.collected_data.get('date_of_birth')}\n"
                f"• **Phone**: {self.collected_data.get('phone')}\n"
                f"• **Email**: {self.collected_data.get('email')}\n"
                f"• **Doctor**: {self.collected_data.get('preferred_doctor')}\n"
                f"• **Location**: {self.collected_data.get('location')}\n\n"
                f"Now let me search our patient database to see if you're a new or returning patient..."
        )
    
    def reset(self):
        """Reset agent state for new conversation"""
        self.collected_data = {}
        self.conversation_history = []
        self.current_field = 0
    
    def get_progress_summary(self) -> str:
        """Get summary of collection progress"""
        total_fields = len(self.fields)
        collected_count = len(self.collected_data)
        
        return (
            f"**Progress**: {collected_count}/{total_fields} fields collected\n"
            f"**Collected**: {', '.join(self.collected_data.keys())}\n"
            f"**Current Step**: {self.current_field + 1}/{total_fields}"
        )

# Test function
def test_greeting_agent():
    """Test the LLM-powered greeting agent"""
    print("🧪 Testing LLM-Powered Greeting Agent with Step-by-Step Collection...\n")
    
    agent = GreetingAgent()
    
    print("Initial Message:")
    print(agent.get_greeting_message())
    print("\n" + "="*50 + "\n")
    
    # Test inputs (one at a time)
    test_inputs = [
        "John Smith",
        "March 15, 1985", 
        "555-123-4567",
        "john.smith@email.com",
        "Dr. Naveen",
        "Gachibowli"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"Step {i}:")
        print(f"User: {user_input}")
        
        response, is_complete, collected_data = agent.process_input(user_input, {})
        print(f"Agent: {response}")
        print(f"Progress: {agent.get_progress_summary()}")
        
        if is_complete:
            print(f"\n✅ **COLLECTION COMPLETE!**")
            print(f"Final Data: {collected_data}")
            break
        
        print("\n" + "-"*30 + "\n")

if __name__ == "__main__":
    test_greeting_agent()
