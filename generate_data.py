import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def generate_patient_data():
    """Generate 50 synthetic patients with Pydantic-compatible data"""
    patients = []
    
    for i in range(50):
        has_visit_history = i < 30
        last_visit = None
        
        if has_visit_history:
            last_visit = fake.date_between(start_date='-2y', end_date='-30d')
        
        # Generate proper phone number (10 digits, no negative)
        phone_digits = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        phone = f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
        
        # Generate DOB in MM/DD/YYYY format - ensure consistency
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)
        dob = f"{birth_date.month:02d}/{birth_date.day:02d}/{birth_date.year}"
        
        patient = {
            'patient_id': f'PAT_{i+1:03d}',
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'dob': dob,  # Now guaranteed MM/DD/YYYY format
            'phone': phone,  # Now guaranteed (XXX) XXX-XXXX format
            'email': fake.email(),
            'address': fake.address().replace('\n', ', '),
            'last_visit': last_visit.strftime('%Y-%m-%d') if last_visit else None,
            'patient_type': 'returning' if has_visit_history else 'new',
            'insurance_carrier': random.choice(['Blue Cross Blue Shield', 'Aetna', 'Cigna', 'UnitedHealth', 'Kaiser']),
            'member_id': fake.bothify(text='###########'),
            'group_number': fake.bothify(text='GRP####')
        }
        patients.append(patient)
    
    df = pd.DataFrame(patients)
    df.to_csv('data/patients.csv', index=False)
    print(f"✅ Generated {len(patients)} patients")
    return df

def generate_doctor_schedule():
    """Generate doctor availability schedule"""
    doctors = ['Dr. Naveen', 'Dr. Naresh', 'Dr. Aish', 'Dr. Shreyansh']
    locations = ['Gachibowli', 'Jubliee Hills', 'Banjara Hills']
    schedule_data = []
    
    for i in range(14):
        date = datetime.now() + timedelta(days=i+1)
        if date.weekday() >= 5:  # Skip weekends
            continue
            
        for doctor in doctors:
            for location in locations:
                for hour in range(9, 17):  # 9 AM to 5 PM
                    for minute in [0, 30]:  # Every 30 minutes
                        slot_time = datetime.combine(date.date(), datetime.min.time().replace(hour=hour, minute=minute))
                        is_available = random.random() < 0.8
                        
                        schedule_data.append({
                            'doctor': doctor,
                            'location': location,
                            'date': date.strftime('%Y-%m-%d'),
                            'time': slot_time.strftime('%H:%M'),
                            'available': is_available,
                            'duration_available': 60 if is_available else 0
                        })
    
    df = pd.DataFrame(schedule_data)
    df.to_excel('data/doctors_schedule.xlsx', index=False)
    print(f"Generated doctor schedules")
    return df

def create_appointments_file():
    """Create empty appointments file"""
    appointments = pd.DataFrame(columns=[
        'appointment_id', 'patient_id', 'patient_name', 'doctor', 'location',
        'date', 'time', 'duration', 'status', 'insurance_carrier', 
        'member_id', 'group_number', 'created_at', 'form_sent', 'reminders_sent'
    ])
    appointments.to_excel('data/appointments.xlsx', index=False)
    print("✅ Created appointments file")

if __name__ == "__main__":
    print(" Generating synthetic data...")
    
    import os
    os.makedirs('data', exist_ok=True)
    
    patients_df = generate_patient_data()
    schedule_df = generate_doctor_schedule()
    create_appointments_file()
    
    print(f"\n Data Summary:")
    print(f"Patients: {len(patients_df)} (30 returning, 20 new)")
    print(f"Available slots: {len(schedule_df[schedule_df['available']==True])}")
    print("\n Data generation complete! Ready for agent development.")