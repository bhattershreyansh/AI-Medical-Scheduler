#!/usr/bin/env python3
"""
Test the improved date validation
"""

import sys
sys.path.append('.')

def test_date_validation():
    """Test various date formats"""
    
    print("🧪 Testing Date Validation...\n")
    
    # Mock the date validation method
    import re
    from datetime import datetime, date
    
    def validate_dob(dob_input: str):
        """Validate date of birth with flexible format support"""
        dob_input = dob_input.strip()
        
        # Try different date formats
        date_formats = [
            # MM/DD/YYYY (US format)
            (r'^\d{1,2}/\d{1,2}/\d{4}$', '/'),
            # MM-DD-YYYY
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
                        
                        # Check if date is reasonable
                        today = date.today()
                        if birth_date > today:
                            return False, "Date of birth cannot be in the future."
                        
                        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                        if age > 120:
                            return False, "Age seems too high."
                        
                        # Format as MM/DD/YYYY for consistency
                        formatted_dob = f"{month:02d}/{day:02d}/{year}"
                        
                        return True, f"✅ Got it! Your date of birth is **{formatted_dob}** (you're {age} years old)."
                        
                    except ValueError:
                        # Try the other format if first one failed
                        if parts[1] <= 12 and parts[0] <= 31:  # Try DD/MM/YYYY
                            try:
                                day, month, year = parts
                                birth_date = date(year, month, day)
                                
                                today = date.today()
                                if birth_date > today:
                                    return False, "Date of birth cannot be in the future."
                                
                                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                                if age > 120:
                                    return False, "Age seems too high."
                                
                                formatted_dob = f"{month:02d}/{day:02d}/{year}"
                                
                                return True, f"✅ Got it! Your date of birth is **{formatted_dob}** (you're {age} years old)."
                                
                            except ValueError:
                                continue
                        else:
                            continue
                            
                except (ValueError, IndexError):
                    continue
        
        return False, "Invalid date format. Please use MM/DD/YYYY or DD/MM/YYYY."
    
    # Test various date formats
    test_dates = [
        "20/06/2004",  # DD/MM/YYYY (should work now)
        "06/20/2004",  # MM/DD/YYYY
        "20-06-2004",  # DD-MM-YYYY
        "06-20-2004",  # MM-DD-YYYY
        "12/25/1990",  # MM/DD/YYYY
        "25/12/1990",  # DD/MM/YYYY
        "invalid",     # Invalid format
        "32/13/2000",  # Invalid date
    ]
    
    for test_date in test_dates:
        print(f"Testing: {test_date}")
        success, message = validate_dob(test_date)
        status = "✅" if success else "❌"
        print(f"{status} {message}\n")
    
    return True

if __name__ == "__main__":
    test_date_validation()