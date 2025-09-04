import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from agents import BookingState, create_initial_state
from agents.greeting_agent import GreetingAgent
from agents.lookup_agent import LookupAgent
from agents.scheduling_agent import SchedulingAgent
from agents.insurance_agent import InsuranceAgent
from agents.confirmation_agent import ConfirmationAgent
from agents.form_distribution import FormDistributionAgent
from agents.reminder_agent import ReminderAgent

load_dotenv()

class MedicalSchedulerApp:
    """Simplified Medical Scheduler with LangGraph-style state management"""
    
    def __init__(self):
        # Initialize all agents
        self.greeting_agent = GreetingAgent()
        self.lookup_agent = LookupAgent()
        self.scheduling_agent = SchedulingAgent()
        self.insurance_agent = InsuranceAgent()
        self.confirmation_agent = ConfirmationAgent(mock_mode=True)
        self.form_agent = FormDistributionAgent(mock_mode=True)
        self.reminder_agent = ReminderAgent(mock_mode=True)
        
        # Initialize state
        self.state = create_initial_state()
    
    def start_conversation(self) -> str:
        """Start the conversation and return greeting message"""
        greeting = self.greeting_agent.get_greeting_message()
        self.state["agent_response"] = greeting
        self.state["conversation_history"].append(f"Agent: {greeting}")
        return greeting
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input through the workflow"""
        try:
            self.state["user_input"] = user_input
            self.state["conversation_history"].append(f"User: {user_input}")
            
            current_step = self.state.get("current_step", "greeting")
            
            if current_step == "greeting":
                return self._handle_greeting(user_input)
            elif current_step == "slot_selection":
                return self._handle_slot_selection(user_input)
            elif current_step == "insurance":
                return self._handle_insurance(user_input)
            else:
                return "I'm not sure what to do next. Let me restart the process."
                
        except Exception as e:
            error_msg = f"Sorry, there was an error: {e}"
            self.state["errors"].append(str(e))
            return error_msg
    
    def _handle_greeting(self, user_input: str) -> str:
        """Handle greeting phase"""
        try:
            # Process patient information
            response, is_complete, data = self.greeting_agent.process_input(user_input, self.state)
            
            if is_complete:
                # Convert to PatientInfo model
                from models import PatientInfo
                try:
                    patient_info = PatientInfo(**data)
                    self.state["patient_info"] = patient_info
                    
                    # Move to lookup phase
                    lookup_response = self._do_lookup()
                    scheduling_response = self._do_scheduling()
                    
                    combined_response = f"{response}\n\n{lookup_response}\n\n{scheduling_response}"
                    self.state["current_step"] = "slot_selection"
                    
                    return combined_response
                    
                except Exception as e:
                    return f"Error processing patient information: {e}"
            else:
                return response
                
        except Exception as e:
            return f"Error in greeting phase: {e}"
    
    def _do_lookup(self) -> str:
        """Perform patient lookup"""
        try:
            patient_data = {
                'patient_name': self.state["patient_info"].patient_name,
                'date_of_birth': self.state["patient_info"].date_of_birth,
                'preferred_doctor': self.state["patient_info"].preferred_doctor,
                'location': self.state["patient_info"].location
            }
            
            response, lookup_result = self.lookup_agent.search_patient(patient_data)
            self.state["lookup_result"] = lookup_result
            
            print(f"✅ Patient lookup: {lookup_result.patient_type if lookup_result else 'Not found'}")
            return response
            
        except Exception as e:
            return f"Error in patient lookup: {e}"
    
    def _do_scheduling(self) -> str:
        """Find available appointment slots"""
        try:
            patient_data = {
                'patient_name': self.state["patient_info"].patient_name,
                'preferred_doctor': self.state["patient_info"].preferred_doctor,
                'location': self.state["patient_info"].location
            }
            
            response, slots = self.scheduling_agent.find_available_slots(
                patient_data, self.state["lookup_result"]
            )
            
            self.state["available_slots"] = slots
            print(f"✅ Found {len(slots)} available slots")
            
            return response
            
        except Exception as e:
            return f"Error finding appointment slots: {e}"
    
    def _handle_slot_selection(self, user_input: str) -> str:
        """Handle slot selection"""
        try:
            available_slots = self.state.get("available_slots", [])
            
            if not available_slots:
                return "No available slots found. Please try different preferences."
            
            # Auto-select first slot for demo
            if user_input.lower() in ['1', 'first', 'yes'] or user_input.strip() == "":
                selected_slot = available_slots[0]
                self.state["selected_slot"] = selected_slot
                self.state["current_step"] = "insurance"
                
                # Start insurance collection
                insurance_greeting = self.insurance_agent.get_insurance_greeting(
                    self.state["patient_info"].patient_name
                )
                
                response = (
                    f"✅ **Slot Selected!**\n\n"
                    f"**Date**: {selected_slot.date}\n"
                    f"**Time**: {selected_slot.time}\n"
                    f"**Doctor**: {selected_slot.doctor}\n"
                    f"**Location**: {selected_slot.location}\n\n"
                    f"{insurance_greeting}"
                )
                
                print(f"✅ Slot selected: {selected_slot.date} at {selected_slot.time}")
                return response
            else:
                # Handle specific slot selection
                try:
                    slot_index = int(user_input) - 1
                    if 0 <= slot_index < len(available_slots):
                        selected_slot = available_slots[slot_index]
                        self.state["selected_slot"] = selected_slot
                        self.state["current_step"] = "insurance"
                        
                        insurance_greeting = self.insurance_agent.get_insurance_greeting(
                            self.state["patient_info"].patient_name
                        )
                        
                        response = (
                            f"✅ **Slot {user_input} Selected!**\n\n"
                            f"**Date**: {selected_slot.date}\n"
                            f"**Time**: {selected_slot.time}\n"
                            f"**Doctor**: {selected_slot.doctor}\n"
                            f"**Location**: {selected_slot.location}\n\n"
                            f"{insurance_greeting}"
                        )
                        
                        return response
                    else:
                        return f"Please select a valid slot number (1-{len(available_slots)})"
                except ValueError:
                    return f"Please enter a slot number (1-{len(available_slots)}) or '1' for the first slot."
                    
        except Exception as e:
            return f"Error selecting slot: {e}"
    
    def _handle_insurance(self, user_input: str) -> str:
        """Handle insurance information collection"""
        try:
            response, is_complete, data = self.insurance_agent.process_input(user_input)
            
            if is_complete:
                # Convert to InsuranceInfo model
                from models import InsuranceInfo
                try:
                    insurance_info = InsuranceInfo(**data)
                    self.state["insurance_info"] = insurance_info
                    
                    # Update patient record with insurance information
                    if self.state.get("lookup_result"):
                        patient_id = self.state["lookup_result"].patient_id
                        insurance_data = {
                            'primary_carrier': insurance_info.primary_carrier,
                            'member_id': insurance_info.member_id,
                            'group_number': insurance_info.group_number
                        }
                        self.lookup_agent.update_patient_insurance_info(patient_id, insurance_data)
                    
                    # Complete the booking process
                    return self._complete_booking()
                    
                except Exception as e:
                    return f"Error processing insurance information: {e}"
            else:
                return response
                
        except Exception as e:
            return f"Error collecting insurance information: {e}"
    
    def _complete_booking(self) -> str:
        """Complete the entire booking process"""
        try:
            # 1. Confirm appointment
            appointment_data = {
                'date': self.state["selected_slot"].date,
                'time': self.state["selected_slot"].time,
                'doctor': self.state["selected_slot"].doctor,
                'location': self.state["selected_slot"].location
            }
            
            response, success, confirmation_record = self.confirmation_agent.confirm_appointment(
                appointment_data,
                {
                    'patient_name': self.state["patient_info"].patient_name,
                    'email': self.state["patient_info"].email,
                    'phone': self.state["patient_info"].phone,
                    'date_of_birth': self.state["patient_info"].date_of_birth,
                    'patient_id': self.state["lookup_result"].patient_id
                },
                {
                    'primary_carrier': self.state["insurance_info"].primary_carrier,
                    'member_id': self.state["insurance_info"].member_id,
                    'group_number': self.state["insurance_info"].group_number
                },
                {
                    'date': self.state["selected_slot"].date,
                    'time': self.state["selected_slot"].time,
                    'doctor': self.state["selected_slot"].doctor,
                    'location': self.state["selected_slot"].location,
                    'duration_available': self.state["selected_slot"].duration_available
                },
                self.state["lookup_result"].patient_type
            )
            
            if not success:
                return f"❌ Appointment confirmation failed: {response}"
            
            # 2. Update doctor's schedule (mark slot as booked)
            patient_type = self.state["lookup_result"].patient_type if self.state.get("lookup_result") else "new"
            schedule_updated = self.scheduling_agent.update_doctor_schedule(
                self.state["selected_slot"], 
                patient_type
            )
            
            if not schedule_updated:
                print("⚠️ Warning: Could not update doctor's schedule")
            
            # 3. Export to Excel
            export_response, export_success = self.confirmation_agent.export_to_excel(confirmation_record)
            
            # 4. Send forms
            form_response, form_success = self.form_agent.send_intake_forms(
                self.state["patient_info"].email,
                self.state["patient_info"].patient_name,
                {
                    'date': self.state["selected_slot"].date,
                    'time': self.state["selected_slot"].time
                },
                patient_type
            )
            
            # 5. Mark new patients as returning (after successful appointment)
            if self.state.get("lookup_result") and self.state["lookup_result"].patient_type == "new":
                patient_id = self.state["lookup_result"].patient_id
                self.lookup_agent.mark_patient_as_returning(patient_id)
            
            # 6. Schedule reminders
            class MockAppointment:
                def __init__(self, state):
                    self.patient_info = type('obj', (object,), {
                        'patient_name': state["patient_info"].patient_name,
                        'email': state["patient_info"].email,
                        'phone': state["patient_info"].phone
                    })()
                    self.appointment_slot = type('obj', (object,), {
                        'date': state["selected_slot"].date,
                        'time': state["selected_slot"].time,
                        'doctor': state["selected_slot"].doctor,
                        'location': state["selected_slot"].location
                    })()
            
            mock_appointment = MockAppointment(self.state)
            reminders = self.reminder_agent.schedule_reminders(mock_appointment)
            
            # Update state
            self.state["final_booking"] = confirmation_record
            self.state["excel_exported"] = export_success
            self.state["form_sent"] = form_success
            self.state["reminders_scheduled"] = True
            self.state["current_step"] = "completed"
            
            # Create user-friendly final response (hide technical details)
            final_response = (
                f"{response}\n\n"
                f"📋 **Patient Intake Forms**\n"
                f"✅ Your intake forms have been sent to your email\n"
                f"Please complete them before your appointment\n\n"
                f"⏰ **Automated Reminders**\n"
                f"✅ You'll receive {len(reminders)} reminder messages:\n"
                f"• 24 hours before your appointment\n"
                f"• 2 hours before (with form completion check)\n"
                f"• 1 hour before (final confirmation)\n\n"
                f"🎉 **Your Appointment is All Set!**\n\n"
                f"**Quick Summary:**\n"
                f"• **Patient**: {self.state['patient_info'].patient_name}\n"
                f"• **Date & Time**: {self.state['selected_slot'].date} at {self.state['selected_slot'].time}\n"
                f"• **Doctor**: {self.state['selected_slot'].doctor}\n"
                f"• **Location**: {self.state['selected_slot'].location}\n"
                f"• **Appointment ID**: {confirmation_record['appointment_id']}\n\n"
                f"**What's Next?**\n"
                f"1. Check your email for confirmation details\n"
                f"2. Complete the intake forms we sent you\n"
                f"3. Arrive 15 minutes early for check-in\n\n"
                f"**Need to make changes?** Contact our office with your Appointment ID.\n\n"
                f"Thank you for choosing our medical practice! 🏥"
            )
            
            print(f"✅ Appointment confirmed: {confirmation_record['appointment_id']}")
            print(f"✅ Excel export: {'Success' if export_success else 'Failed'}")
            print(f"✅ Forms sent: {'Success' if form_success else 'Failed'}")
            print(f"✅ Reminders scheduled: {len(reminders)}")
            print("🎉 Complete workflow finished successfully!")
            
            return final_response
            
        except Exception as e:
            return f"Error completing booking: {e}"
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get current state summary"""
        patient_info = self.state.get('patient_info')
        return {
            'current_step': self.state.get('current_step'),
            'patient_name': patient_info.patient_name if patient_info else None,
            'excel_exported': self.state.get('excel_exported', False),
            'form_sent': self.state.get('form_sent', False),
            'reminders_scheduled': self.state.get('reminders_scheduled', False),
            'errors': len(self.state.get('errors', []))
        }

# Interactive demo function
def interactive_demo():
    """Interactive demo of the simplified workflow"""
    print("🏥 Medical Appointment Scheduling System - LangGraph Demo")
    print("=" * 60)
    
    app = MedicalSchedulerApp()
    
    # Start conversation
    greeting = app.start_conversation()
    print(f"\n🤖 Agent: {greeting}")
    
    # Interactive loop
    while app.state.get("current_step") != "completed":
        user_input = input("\n👤 You: ")
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        
        # Process input
        response = app.process_user_input(user_input)
        print(f"\n🤖 Agent: {response}")
        
        # Check if workflow is complete
        if app.state.get("reminders_scheduled"):
            print("\n🎉 Appointment booking completed successfully!")
            break
    
    return app.get_state_summary()

# Test the application
if __name__ == "__main__":
    # Run interactive demo
    final_summary = interactive_demo()
    
    print(f"\n📊 Final State Summary:")
    for key, value in final_summary.items():
        print(f"{key}: {value}")