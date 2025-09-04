import sys
import os
import re
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

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
import json

class GreetingAgent:
    """LLM-powered greeting agent that collects patient information naturally"""
    
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("GROQ_MODEL", "llama3-8b-8192")
        )
        self.collected_data = {}
        self.conversation_history = []
        self.current_field = 0  # Track which field we're collecting
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
            "I'm here to help you book an appointment. Let's start step by step.\n\n"
            "First, could you please tell me your **full name** (first and last name)?"
        )
    
    def process_input(self, user_input: str, state: BookingState) -> Tuple[str, bool, Optional[Dict]]:
        """
        Process user input step by step to collect patient information
        """
        # Handle None input
        if user_input is None:
            return "I didn't catch that. Could you please repeat?", False, None
            
        user_input = user_input.strip()
        
        if not user_input:
            return "I didn't catch that. Could you please repeat?", False, None
        
        # Add to conversation history
        self.conversation_history.append(f"Patient: {user_input}")
        
        # Process current field
        current_field_name = self.fields[self.current_field]
        success, response = self._process_current_field(current_field_name, user_input)
        
        if success:
            self.current_field += 1
            
            # Check if we have all fields
            if self.current_field >= len(self.fields):
                return self._get_completion_message(), True, self.collected_data.copy()
            else:
                # Ask for next field
                next_prompt = self._get_next_field_prompt()
                return f"{response}\n\n{next_prompt}", False, None
        else:
            return response, False, None
    
    def _extract_info_with_llm(self, user_input: str) -> Optional[Dict]:
        """Use LLM to extract patient information from natural language"""
        
        system_prompt = """You are a medical scheduling assistant. Extract patient information from user input.

        Extract ONLY these fields if mentioned:
        - patient_name: Full name (first and last)
        - date_of_birth: Date in MM/DD/YYYY format (convert from natural language like "7th july 2004" to "07/07/2004")
        - preferred_doctor: One of [Dr. Naveen, Dr. Naresh, Dr. Aish, Dr. Shreyansh] (normalize variations like "DR naveen" to "Dr. Naveen")
        - location: One of [Gachibowli, Jubliee Hills, Banjara Hills] (normalize variations like "banjara hills" to "Banjara Hills")
        - phone: Phone number (any format)
        - email: Email address

        Return ONLY valid JSON with found fields. If field not mentioned, don't include it.
        Example: {"patient_name": "Aviral Gupta", "date_of_birth": "07/07/2004", "preferred_doctor": "Dr. Naveen", "location": "Banjara Hills"}
        """
        
        user_prompt = f"Extract patient information from: {user_input}"
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Try to parse JSON response
            if response_text.startswith('{') and response_text.endswith('}'):
                extracted_data = json.loads(response_text)
                
                # Validate extracted data
                validated_data = self._validate_extracted_data(extracted_data)
                return validated_data
            else:
                print(f"LLM response not in JSON format: {response_text}")
                return None
                
        except Exception as e:
            print(f"Error extracting info with LLM: {e}")
            return None
    
    def _validate_extracted_data(self, extracted_data: Dict) -> Dict:
        """Validate and clean extracted data"""
        validated = {}
        
        # Validate name
        if 'patient_name' in extracted_data:
            name = extracted_data['patient_name'].strip()
            if len(name.split()) >= 2:
                validated['patient_name'] = name
        
        # Validate DOB
        if 'date_of_birth' in extracted_data:
            dob = extracted_data['date_of_birth'].strip()
            if '/' in dob or '-' in dob:
                validated['date_of_birth'] = dob
        
        # Validate doctor with fuzzy matching
        if 'preferred_doctor' in extracted_data:
            doctor = extracted_data['preferred_doctor'].strip().lower()
            valid_doctors = ['Dr. Naveen', 'Dr. Naresh', 'Dr. Aish', 'Dr. Shreyansh']
            
            # Fuzzy matching for doctor names
            if 'naveen' in doctor:
                validated['preferred_doctor'] = 'Dr. Naveen'
            elif 'naresh' in doctor:
                validated['preferred_doctor'] = 'Dr. Naresh'
            elif 'aish' in doctor:
                validated['preferred_doctor'] = 'Dr. Aish'
            elif 'shreyansh' in doctor:
                validated['preferred_doctor'] = 'Dr. Shreyansh'
        
        # Validate location with fuzzy matching
        if 'location' in extracted_data:
            location = extracted_data['location'].strip().lower()
            
            # Fuzzy matching for locations
            if 'gachibowli' in location:
                validated['location'] = 'Gachibowli'
            elif 'jubliee' in location or 'jubilee' in location:
                validated['location'] = 'Jubliee Hills'
            elif 'banjara' in location:
                validated['location'] = 'Banjara Hills'
        
        # Validate phone
        if 'phone' in extracted_data:
            phone = extracted_data['phone'].strip()
            if len(phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) >= 10:
                validated['phone'] = phone
        
        # Validate email
        if 'email' in extracted_data:
            email = extracted_data['email'].strip().lower()
            if '@' in email and '.' in email:
                validated['email'] = email
        
        return validated
    
    def _has_all_required_info(self) -> bool:
        """Check if we have all required information"""
        required_fields = ['patient_name', 'date_of_birth', 'preferred_doctor', 'location', 'phone', 'email']
        return all(field in self.collected_data for field in required_fields)
    
    def _get_missing_fields(self) -> list:
        """Get list of missing required fields"""
        required_fields = ['patient_name', 'date_of_birth', 'preferred_doctor', 'location', 'phone', 'email']
        return [field for field in required_fields if field not in self.collected_data]
    
    def _get_missing_info_prompt(self, missing_fields: list) -> str:
        """Generate prompt for missing information"""
        field_names = {
            'patient_name': 'full name (first and last)',
            'date_of_birth': 'date of birth (MM/DD/YYYY)',
            'preferred_doctor': 'preferred doctor (Dr. Naveen, Dr. Naresh, Dr. Aish, or Dr. Shreyansh)',
            'location': 'preferred location (Gachibowli, Jubliee Hills, or Banjara Hills)',
            'phone': 'phone number',
            'email': 'email address'
        }
        
        missing_list = [field_names[field] for field in missing_fields]
        
        if len(missing_list) == 1:
            return f"Please provide your {missing_list[0]}."
        else:
            return f"Please provide your {', '.join(missing_list[:-1])} and {missing_list[-1]}."
    
    def _process_current_field(self, field_name: str, user_input: str) -> Tuple[bool, str]:
        """Process the current field being collected"""
        
        if field_name == 'patient_name':
            return self._validate_name(user_input)
        elif field_name == 'date_of_birth':
            return self._validate_dob(user_input)
        elif field_name == 'phone':
            return self._validate_phone_input(user_input)
        elif field_name == 'email':
            return self._validate_email_input(user_input)
        elif field_name == 'preferred_doctor':
            return self._validate_doctor_input(user_input)
        elif field_name == 'location':
            return self._validate_location_input(user_input)
        else:
            return False, "Unknown field"
    
    def _validate_name(self, name: str) -> Tuple[bool, str]:
        """Validate patient name"""
        name = name.strip()
        parts = name.split()
        
        if len(parts) >= 2:
            self.collected_data['patient_name'] = ' '.join(part.title() for part in parts)
            return True, f"✅ Got it! Your name is **{self.collected_data['patient_name']}**."
        else:
            return False, "Please provide both your first and last name."
    
    def _validate_dob(self, dob_input: str) -> Tuple[bool, str]:
        """Validate date of birth with flexible format support"""
        dob_input = dob_input.strip()
        
        from datetime import datetime, date
        
        # Try different date formats
        date_formats = [
            # MM/DD/YYYY (US format)
            (r'^\d{1,2}/\d{1,2}/\d{4}$', '/'),
            # DD/MM/YYYY (International format)  
            (r'^\d{1,2}/\d{1,2}/\d{4}$', '/'),
            # MM-DD-YYYY
            (r'^\d{1,2}-\d{1,2}-\d{4}$', '-'),
            # DD-MM-YYYY
            (r'^\d{1,2}-\d{1,2}-\d{4}$', '-'),
        ]
        
        for pattern, separator in date_formats:
            if re.match(pattern, dob_input):
                try:
                    parts = list(map(int, dob_input.split(separator)))
                    
                    # Try MM/DD/YYYY first
                    try:
                        if parts[0] <= 12 and parts[1] <= 31:  # Likely MM/DD/YYYY
                            month, day, year = parts
                        elif parts[1] <= 12 and parts[0] <= 31:  # Likely DD/MM/YYYY
                            day, month, year = parts
                        else:
                            # Ambiguous, default to MM/DD/YYYY
                            month, day, year = parts
                        
                        # Validate the date
                        birth_date = date(year, month, day)
                        
                        # Check if date is reasonable (not in future, not too old)
                        today = date.today()
                        if birth_date > today:
                            return False, "Date of birth cannot be in the future. Please check your input."
                        
                        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                        if age > 120:
                            return False, "Please verify the date of birth. The age seems too high."
                        
                        # Format as MM/DD/YYYY for consistency
                        formatted_dob = f"{month:02d}/{day:02d}/{year}"
                        self.collected_data['date_of_birth'] = formatted_dob
                        
                        return True, f"✅ Got it! Your date of birth is **{formatted_dob}** (you're {age} years old)."
                        
                    except ValueError as e:
                        # Try the other format if first one failed
                        if parts[1] <= 12 and parts[0] <= 31:  # Try DD/MM/YYYY
                            try:
                                day, month, year = parts
                                birth_date = date(year, month, day)
                                
                                # Same validation as above
                                today = date.today()
                                if birth_date > today:
                                    return False, "Date of birth cannot be in the future. Please check your input."
                                
                                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                                if age > 120:
                                    return False, "Please verify the date of birth. The age seems too high."
                                
                                formatted_dob = f"{month:02d}/{day:02d}/{year}"
                                self.collected_data['date_of_birth'] = formatted_dob
                                
                                return True, f"✅ Got it! Your date of birth is **{formatted_dob}** (you're {age} years old)."
                                
                            except ValueError:
                                continue
                        else:
                            continue
                            
                except (ValueError, IndexError):
                    continue
        
        # If no format worked, provide helpful error message
        return False, (
            "I couldn't understand that date format. Please try one of these formats:\n"
            "• **MM/DD/YYYY** (e.g., 06/20/2004)\n"
            "• **DD/MM/YYYY** (e.g., 20/06/2004)\n"
            "• **MM-DD-YYYY** (e.g., 06-20-2004)\n"
            "• **DD-MM-YYYY** (e.g., 20-06-2004)"
        )
    
    def _validate_phone_input(self, phone: str) -> Tuple[bool, str]:
        """Validate phone number"""
        phone = phone.strip()
        digits = re.sub(r'[^\d]', '', phone)
        
        if len(digits) >= 10:
            if len(digits) == 10:
                formatted_phone = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits[0] == '1':
                formatted_phone = f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            else:
                formatted_phone = phone
            
            self.collected_data['phone'] = formatted_phone
            return True, f"✅ Got it! Your phone number is **{formatted_phone}**."
        else:
            return False, "Please provide a valid phone number with at least 10 digits."
    
    def _validate_email_input(self, email: str) -> Tuple[bool, str]:
        """Validate email address"""
        email = email.strip().lower()
        
        if '@' in email and '.' in email:
            self.collected_data['email'] = email
            return True, f"✅ Got it! Your email is **{email}**."
        else:
            return False, "Please provide a valid email address (e.g., john@example.com)."
    
    def _validate_doctor_input(self, doctor_input: str) -> Tuple[bool, str]:
        """Validate doctor selection"""
        doctor_input = doctor_input.strip().lower()
        
        # Fuzzy matching for doctor names
        if 'naveen' in doctor_input:
            self.collected_data['preferred_doctor'] = 'Dr. Naveen'
            return True, f"✅ Great choice! You've selected **Dr. Naveen**."
        elif 'naresh' in doctor_input:
            self.collected_data['preferred_doctor'] = 'Dr. Naresh'
            return True, f"✅ Great choice! You've selected **Dr. Naresh**."
        elif 'aish' in doctor_input:
            self.collected_data['preferred_doctor'] = 'Dr. Aish'
            return True, f"✅ Great choice! You've selected **Dr. Aish**."
        elif 'shreyansh' in doctor_input:
            self.collected_data['preferred_doctor'] = 'Dr. Shreyansh'
            return True, f"✅ Great choice! You've selected **Dr. Shreyansh**."
        else:
            return False, "Please choose from our available doctors: **Dr. Naveen**, **Dr. Naresh**, **Dr. Aish**, or **Dr. Shreyansh**."
    
    def _validate_location_input(self, location_input: str) -> Tuple[bool, str]:
        """Validate location selection"""
        location_input = location_input.strip().lower()
        
        # Fuzzy matching for locations
        if 'gachibowli' in location_input:
            self.collected_data['location'] = 'Gachibowli'
            return True, f"✅ Perfect! You've selected **Gachibowli** location."
        elif 'jubliee' in location_input or 'jubilee' in location_input:
            self.collected_data['location'] = 'Jubliee Hills'
            return True, f"✅ Perfect! You've selected **Jubliee Hills** location."
        elif 'banjara' in location_input:
            self.collected_data['location'] = 'Banjara Hills'
            return True, f"✅ Perfect! You've selected **Banjara Hills** location."
        else:
            return False, "Please choose from our available locations: **Gachibowli**, **Jubliee Hills**, or **Banjara Hills**."
    
    def _get_next_field_prompt(self) -> str:
        """Get prompt for the next field"""
        field_name = self.fields[self.current_field]
        
        prompts = {
            'patient_name': "Could you please tell me your **full name** (first and last name)?",
            'date_of_birth': "What's your **date of birth**? Please use MM/DD/YYYY format (e.g., 12/25/1990).",
            'phone': "What's your **phone number**?",
            'email': "What's your **email address**?",
            'preferred_doctor': "Which **doctor** would you like to see?\n\n**Available doctors:**\n• Dr. Naveen\n• Dr. Naresh\n• Dr. Aish\n• Dr. Shreyansh",
            'location': "Which **location** would you prefer?\n\n**Available locations:**\n• Gachibowli\n• Jubliee Hills\n• Banjara Hills"
        }
        
        return prompts.get(field_name, "Please provide the requested information.")
    
    def _get_completion_message(self) -> str:
        """Get completion message when all info is collected"""
        return (
            "🎉 Perfect! I have all your information:\n\n"
            f"**Name**: {self.collected_data['patient_name']}\n"
            f"**DOB**: {self.collected_data['date_of_birth']}\n"
            f"**Phone**: {self.collected_data['phone']}\n"
            f"**Email**: {self.collected_data['email']}\n"
            f"**Doctor**: {self.collected_data['preferred_doctor']}\n"
            f"**Location**: {self.collected_data['location']}\n\n"
            "Now let me search our patient database to see if you're a new or returning patient..."
        )
    
    def reset(self):
        """Reset agent state"""
        self.collected_data = {}
        self.conversation_history = []
        self.current_field = 0

# Test function
def test_greeting_agent():
    """Test the LLM-powered greeting agent"""
    print("🧪 Testing LLM-Powered Greeting Agent...\n")
    
    agent = GreetingAgent()
    
    print(agent.get_greeting_message())
    
    # Test with natural language input
    test_inputs = [
        "Hi, I'm John Smith, born December 25th 1990, I'd like to see Dr. Naveen at the Gachibowli location",
        "My phone is (555) 123-4567 and email is john.smith@email.com"
    ]
    
    for user_input in test_inputs:
        print(f"\nUser: {user_input}")
        response, is_complete, collected_data = agent.process_input(user_input, {})
        print(f"Agent: {response}")
        
        if is_complete:
            print(f"\n✅ All Data Collected: {collected_data}")
            break

if __name__ == "__main__":
    test_greeting_agent()