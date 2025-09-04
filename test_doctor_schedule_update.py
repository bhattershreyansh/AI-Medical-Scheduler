#!/usr/bin/env python3
"""Test that doctor schedule gets updated after appointment booking"""

import sys
sys.path.append('.')

def test_doctor_schedule_update():
    print("🧪 Testing Doctor Schedule Update After Appointment...\n")
    
    try:
        from agents.scheduling_agent import SchedulingAgent
        from models.appointment_models import AppointmentSlot
        import pandas as pd
        
        # Create scheduling agent
        scheduling_agent = SchedulingAgent()
        
        # Check initial schedule
        print("1. Checking initial doctor schedule...")
        initial_df = pd.read_excel("data/doctors_schedule.xlsx")
        available_slots_before = len(initial_df[initial_df['available'] == True])
        print(f"Available slots before booking: {available_slots_before}")
        
        # Find an available slot
        available_mask = initial_df['available'] == True
        if not available_mask.any():
            print("❌ No available slots found for testing")
            return False
        
        # Get first available slot
        first_available = initial_df[available_mask].iloc[0]
        print(f"Testing with slot: {first_available['doctor']} - {first_available['date']} {first_available['time']}")
        
        # Create AppointmentSlot object
        test_slot = AppointmentSlot(
            doctor=first_available['doctor'],
            location=first_available['location'],
            date=first_available['date'],
            time=first_available['time'],
            duration_available=int(first_available['duration_available'])
        )
        
        # Test with new patient (should use 60 minutes)
        print(f"\n2. Booking appointment for NEW patient...")
        success = scheduling_agent.update_doctor_schedule(test_slot, "new")
        
        if success:
            print("✅ Schedule update method executed successfully")
            
            # Check if schedule was actually updated
            updated_df = pd.read_excel("data/doctors_schedule.xlsx")
            
            # Find the slot we just booked
            slot_mask = (
                (updated_df['doctor'] == test_slot.doctor) &
                (updated_df['location'] == test_slot.location) &
                (updated_df['date'] == test_slot.date) &
                (updated_df['time'] == test_slot.time)
            )
            
            if slot_mask.any():
                updated_slot = updated_df[slot_mask].iloc[0]
                print(f"Updated slot details:")
                print(f"  Available: {updated_slot['available']}")
                print(f"  Duration Available: {updated_slot['duration_available']}")
                
                # For new patient (60 min), slot should be fully booked
                if updated_slot['available'] == False and updated_slot['duration_available'] == 0:
                    print("✅ Slot correctly marked as fully booked for new patient")
                    
                    # Count available slots after booking
                    available_slots_after = len(updated_df[updated_df['available'] == True])
                    print(f"Available slots after booking: {available_slots_after}")
                    
                    if available_slots_after < available_slots_before:
                        print("✅ Total available slots decreased correctly")
                        return True
                    else:
                        print("❌ Total available slots did not decrease")
                        return False
                else:
                    print("❌ Slot not properly updated")
                    print(f"Expected: available=False, duration=0")
                    print(f"Actual: available={updated_slot['available']}, duration={updated_slot['duration_available']}")
                    return False
            else:
                print("❌ Could not find the updated slot in schedule")
                return False
        else:
            print("❌ Schedule update method failed")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_returning_patient_booking():
    """Test booking for returning patient (30 minutes)"""
    print("\n🧪 Testing Returning Patient Booking (30 minutes)...\n")
    
    try:
        from agents.scheduling_agent import SchedulingAgent
        from models.appointment_models import AppointmentSlot
        import pandas as pd
        
        scheduling_agent = SchedulingAgent()
        
        # Find a slot with 60+ minutes available
        df = pd.read_excel("data/doctors_schedule.xlsx")
        suitable_slots = df[(df['available'] == True) & (df['duration_available'] >= 60)]
        
        if len(suitable_slots) == 0:
            print("❌ No suitable slots found for returning patient test")
            return False
        
        test_slot_data = suitable_slots.iloc[0]
        original_duration = test_slot_data['duration_available']
        
        test_slot = AppointmentSlot(
            doctor=test_slot_data['doctor'],
            location=test_slot_data['location'],
            date=test_slot_data['date'],
            time=test_slot_data['time'],
            duration_available=int(original_duration)
        )
        
        print(f"Testing returning patient with slot: {test_slot.doctor} - {test_slot.date} {test_slot.time}")
        print(f"Original duration available: {original_duration} minutes")
        
        # Book for returning patient (30 minutes)
        success = scheduling_agent.update_doctor_schedule(test_slot, "returning")
        
        if success:
            # Check updated schedule
            updated_df = pd.read_excel("data/doctors_schedule.xlsx")
            slot_mask = (
                (updated_df['doctor'] == test_slot.doctor) &
                (updated_df['location'] == test_slot.location) &
                (updated_df['date'] == test_slot.date) &
                (updated_df['time'] == test_slot.time)
            )
            
            if slot_mask.any():
                updated_slot = updated_df[slot_mask].iloc[0]
                expected_remaining = max(0, original_duration - 30)
                
                print(f"Expected remaining duration: {expected_remaining} minutes")
                print(f"Actual remaining duration: {updated_slot['duration_available']} minutes")
                print(f"Slot still available: {updated_slot['available']}")
                
                if updated_slot['duration_available'] == expected_remaining:
                    print("✅ Returning patient booking correctly updated schedule")
                    return True
                else:
                    print("❌ Schedule not updated correctly for returning patient")
                    return False
            else:
                print("❌ Could not find updated slot")
                return False
        else:
            print("❌ Returning patient booking failed")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Doctor Schedule Update Functionality\n")
    
    # Test new patient booking
    new_patient_test = test_doctor_schedule_update()
    
    # Test returning patient booking
    returning_patient_test = test_returning_patient_booking()
    
    print(f"\n📊 Test Results:")
    print(f"New Patient Booking: {'✅ Pass' if new_patient_test else '❌ Fail'}")
    print(f"Returning Patient Booking: {'✅ Pass' if returning_patient_test else '❌ Fail'}")
    
    if new_patient_test and returning_patient_test:
        print("\n🎉 All doctor schedule update tests passed!")
        print("Doctor schedules will now be properly updated after appointments!")
    else:
        print("\n❌ Some tests failed. Check the implementation.")