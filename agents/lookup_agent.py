import sys
import os
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Safe path handling
try:
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir.parent))
except NameError:
    # Running in interactive environment
    sys.path.append('..')

from models import PatientLookupResult

class LookupAgent:
    """Assignment-accurate lookup agent that searches EMR and detects new vs returning patients"""
    
    def __init__(self, patients_csv_path: str = "data/patients.csv"):
        self.patients_csv_path = patients_csv_path
        self.patients_df = None
        self.load_patient_database()
    
    def load_patient_database(self):
        """Load the patient database from CSV (simulating EMR)"""
        try:
            # Try to load the actual CSV file
            if os.path.exists(self.patients_csv_path):
                self.patients_df = pd.read_csv(self.patients_csv_path)
                print(f"Loaded {len(self.patients_df)} patients from database")
            else:
                # If CSV doesn't exist, try to find it in different locations
                possible_paths = [
                    "data/patients.csv",
                    "../data/patients.csv",
                    "../../data/patients.csv",
                    os.path.join(os.path.dirname(__file__), "..", "data", "patients.csv")
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        self.patients_df = pd.read_csv(path)
                        print(f"Loaded {len(self.patients_df)} patients from {path}")
                        break
                else:
                    print("Patient database not found. Please run generate_data.py first!")
                    print(f"Looked in: {possible_paths}")
                    self.patients_df = pd.DataFrame()
                
        except Exception as e:
            print(f"Error loading patient database: {e}")
            self.patients_df = pd.DataFrame()
    
    def search_patient(self, patient_data: Dict[str, Any]) -> Tuple[str, Optional[PatientLookupResult]]:
        """Search for patient in database and determine if new or returning"""
        if self.patients_df is None or self.patients_df.empty:
            return "Patient database is not available. Please run generate_data.py first!", None
        
        patient_name = patient_data.get('patient_name', '').lower()
        dob = patient_data.get('date_of_birth', '')
        
        if not patient_name or not dob:
            return "Missing patient information for lookup.", None
        
        found_patient = self._find_patient_by_name_and_dob(patient_name, dob)
        
        if found_patient is not None:
            return self._handle_returning_patient(found_patient, patient_data)
        else:
            return self._handle_new_patient(patient_data)
    
    def _find_patient_by_name_and_dob(self, patient_name: str, dob: str) -> Optional[Dict]:
        """Find patient by name and DOB in the database"""
        try:
            normalized_dob = self._normalize_dob_for_search(dob)
            
            for _, row in self.patients_df.iterrows():
                db_name = f"{row['first_name']} {row['last_name']}".lower()
                db_dob = self._normalize_dob_for_search(str(row['dob']))
                
                if patient_name in db_name and normalized_dob == db_dob:
                    return row.to_dict()
            
            return None
            
        except Exception as e:
            print(f"Error searching patient database: {e}")
            return None
    
    def _normalize_dob_for_search(self, dob: str) -> str:
        """Normalize DOB format for comparison"""
        try:
            dob = str(dob).strip()
            
            # Handle MM/DD/YYYY format
            if '/' in dob:
                parts = dob.split('/')
                if len(parts) == 3 and all(part.isdigit() for part in parts):
                    month, day, year = parts
                    return f"{year}{month.zfill(2)}{day.zfill(2)}"
            
            # Handle MM-DD-YYYY format
            elif '-' in dob:
                parts = dob.split('-')
                if len(parts) == 3 and all(part.isdigit() for part in parts):
                    month, day, year = parts
                    return f"{year}{month.zfill(2)}{day.zfill(2)}"
            
            # Handle YYYY-MM-DD format
            elif len(dob) == 10 and dob.count('-') == 2:
                parts = dob.split('-')
                if len(parts) == 3 and all(part.isdigit() for part in parts):
                    year, month, day = parts
                    return f"{year}{month.zfill(2)}{day.zfill(2)}"
            
            # Handle YYYYMMDD format (already normalized)
            elif len(dob) == 8 and dob.isdigit():
                return dob
                
            return dob  # Return as-is if format not recognized
            
        except Exception as e:
            print(f"Error normalizing DOB {dob}: {e}")
            return dob
    
    def _handle_returning_patient(self, db_patient: Dict, current_data: Dict) -> Tuple[str, PatientLookupResult]:
        """Handle returning patient found in database"""
        last_visit = db_patient.get('last_visit', 'Unknown')
        patient_id = db_patient.get('patient_id', 'Unknown')
        
        lookup_result = PatientLookupResult(
            patient_id=patient_id,
            patient_type="returning",
            appointment_duration=30,
            last_visit=last_visit,
            existing_insurance={
                'carrier': db_patient.get('insurance_carrier', 'Unknown'),
                'member_id': db_patient.get('member_id', 'Unknown'),
                'group_number': db_patient.get('group_number', 'Unknown')
            }
        )
        
        response_message = (
            f"Welcome back, {current_data['patient_name']}!\n\n"
            f"**Patient Status**: Returning Patient\n"
            f"**Patient ID**: {patient_id}\n"
            f"**Appointment Duration**: 30 minutes\n"
            f"**Last Visit**: {last_visit}\n\n"
            f"Great to see you again! Let me check available appointment slots for you..."
        )
        
        return response_message, lookup_result
    
    def _handle_new_patient(self, current_data: Dict) -> Tuple[str, PatientLookupResult]:
        """Handle new patient not found in database and add them to CSV"""
        new_patient_id = self._generate_next_patient_id()
        
        # Create new patient record for database with all available fields
        new_patient_record = {
            'patient_id': new_patient_id,
            'first_name': current_data.get('patient_name', '').split()[0] if current_data.get('patient_name') else '',
            'last_name': ' '.join(current_data.get('patient_name', '').split()[1:]) if len(current_data.get('patient_name', '').split()) > 1 else '',
            'dob': current_data.get('date_of_birth', ''),
            'phone': current_data.get('phone', ''),
            'email': current_data.get('email', ''),
            'address': current_data.get('address', ''),
            'last_visit': datetime.now().strftime('%Y-%m-%d'),
            'patient_type': 'new',  # Mark as new patient initially
            'insurance_carrier': '',  # Will be updated later when insurance info is collected
            'member_id': '',  # Will be updated later
            'group_number': '',  # Will be updated later
            'emergency_contact': current_data.get('emergency_contact', ''),
            'insurance_provider': '',  # Will be updated later
            'policy_number': '',  # Will be updated later
            'notes': f'New patient registered on {datetime.now().strftime("%Y-%m-%d")}'
        }
        
        # Add to in-memory dataframe first (so next ID generation sees it)
        import pandas as pd
        new_row = pd.DataFrame([new_patient_record])
        self.patients_df = pd.concat([self.patients_df, new_row], ignore_index=True)
        
        # Save new patient to CSV
        self._save_new_patient_to_csv(new_patient_record)
        
        lookup_result = PatientLookupResult(
            patient_id=new_patient_id,
            patient_type="new",
            appointment_duration=60,
            last_visit=None,
            existing_insurance=None
        )
        
        response_message = (
            f"Welcome, {current_data['patient_name']}!\n\n"
            f"**Patient Status**: New Patient\n"
            f"**Patient ID**: {new_patient_id}\n"
            f"**Appointment Duration**: 60 minutes\n\n"
            f"As a new patient, you'll have a comprehensive 60-minute appointment. "
            f"Let me check available appointment slots for you..."
        )
        
        print(f"✅ New patient registered and saved: {new_patient_id}")
        return response_message, lookup_result
    
    def _save_new_patient_to_csv(self, patient_record: Dict):
        """Save new patient to CSV file"""
        try:
            import pandas as pd
            
            # Read existing CSV
            try:
                df = pd.read_csv(self.patients_csv_path)
            except FileNotFoundError:
                # Create new DataFrame with proper columns if file doesn't exist
                df = pd.DataFrame(columns=[
                    'patient_id', 'first_name', 'last_name', 'dob', 'phone', 'email',
                    'address', 'last_visit', 'patient_type', 'insurance_carrier', 
                    'member_id', 'group_number','notes'
                ])
            
            # Add new patient
            new_row = pd.DataFrame([patient_record])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save back to CSV
            df.to_csv(self.patients_csv_path, index=False)
            print(f"✅ Patient saved to {self.patients_csv_path}")
            
            # Also update the in-memory dataframe
            self.patients_df = df
            
        except Exception as e:
            print(f"❌ Error saving patient to CSV: {e}")
    
    def _generate_next_patient_id(self) -> str:
        """Generate the next available patient ID by finding the highest existing number"""
        try:
            # Extract all existing patient numbers
            existing_numbers = []
            
            for _, row in self.patients_df.iterrows():
                patient_id = str(row['patient_id'])
                if patient_id.startswith('PAT_'):
                    # Extract the number part
                    parts = patient_id.split('_')
                    if len(parts) >= 2:
                        try:
                            # Handle both PAT_001 and PAT_20250903_001 formats
                            number_part = parts[-1]  # Get the last part
                            if number_part.isdigit():
                                existing_numbers.append(int(number_part))
                        except ValueError:
                            continue
            
            # Find the next available number
            if existing_numbers:
                next_number = max(existing_numbers) + 1
            else:
                next_number = 1
            
            # Generate new patient ID in simple format: PAT_XXX
            new_patient_id = f"PAT_{next_number:03d}"
            
            print(f"Generated new patient ID: {new_patient_id} (next number: {next_number})")
            return new_patient_id
            
        except Exception as e:
            print(f"❌ Error generating patient ID: {e}")
            # Fallback to simple increment
            return f"PAT_{len(self.patients_df) + 1:03d}"
    
    def update_patient_insurance_info(self, patient_id: str, insurance_info: dict):
        """Update patient record with insurance information"""
        try:
            import pandas as pd
            
            # Update in-memory dataframe
            mask = self.patients_df['patient_id'] == patient_id
            if mask.any():
                self.patients_df.loc[mask, 'insurance_carrier'] = insurance_info.get('primary_carrier', '')
                self.patients_df.loc[mask, 'member_id'] = insurance_info.get('member_id', '')
                self.patients_df.loc[mask, 'group_number'] = insurance_info.get('group_number', '')
                self.patients_df.loc[mask, 'insurance_provider'] = insurance_info.get('primary_carrier', '')
                
                # Save updated dataframe to CSV
                self.patients_df.to_csv(self.patients_csv_path, index=False)
                print(f"✅ Updated insurance info for patient {patient_id}")
            else:
                print(f"❌ Patient {patient_id} not found for insurance update")
                
        except Exception as e:
            print(f"❌ Error updating patient insurance info: {e}")
    
    def mark_patient_as_returning(self, patient_id: str):
        """Mark a patient as returning after their first completed appointment"""
        try:
            import pandas as pd
            
            # Update in-memory dataframe
            mask = self.patients_df['patient_id'] == patient_id
            if mask.any():
                self.patients_df.loc[mask, 'patient_type'] = 'returning'
                self.patients_df.loc[mask, 'last_visit'] = datetime.now().strftime('%Y-%m-%d')
                
                # Save updated dataframe to CSV
                self.patients_df.to_csv(self.patients_csv_path, index=False)
                print(f"✅ Marked patient {patient_id} as returning")
            else:
                print(f"❌ Patient {patient_id} not found for status update")
                
        except Exception as e:
            print(f"❌ Error marking patient as returning: {e}")
    
    def get_patient_summary(self, lookup_result: PatientLookupResult) -> str:
        """Get a summary of the patient lookup result"""
        if lookup_result.patient_type == "returning":
            return (
                f"**Patient Summary**\n"
                f"Type: Returning Patient\n"
                f"Duration: {lookup_result.appointment_duration} minutes\n"
                f"Last Visit: {lookup_result.last_visit or 'Unknown'}"
            )
        else:
            return (
                f"**Patient Summary**\n"
                f"Type: New Patient\n"
                f"Duration: {lookup_result.appointment_duration} minutes\n"
                f"Status: First-time visit"
            )


# Test function
def test_lookup_agent():
    """Test the lookup agent functionality"""
    print("Testing Lookup Agent...\n")
    
    agent = LookupAgent()
    
    # Test with returning patient (should exist in your generated data)
    print("=== Testing Returning Patient ===")
    test_data = {
        'patient_name': 'Lucas Ho',
        'date_of_birth': '04/24/1988',
        'preferred_doctor': 'Dr. Johnson',
        'location': 'Main Office'
    }
    
    response, result = agent.search_patient(test_data)
    print(f"Response: {response}")
    if result:
        print(f"Lookup Result: {result}")
        print(agent.get_patient_summary(result))
    
    print("\n=== Testing New Patient ===")
    # Test with new patient (should not exist)
    new_test_data = {
        'patient_name': 'Jane Doe',
        'date_of_birth': '05/15/1995',
        'preferred_doctor': 'Dr. Johnson',
        'location': 'Main Office'
    }
    
    response, result = agent.search_patient(new_test_data)
    print(f"Response: {response}")
    if result:
        print(f"Lookup Result: {result}")
        print(agent.get_patient_summary(result))


if __name__ == "__main__":
    test_lookup_agent()
