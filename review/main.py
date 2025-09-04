import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
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
    """Main application orchestrating all agents with LangGraph"""
    
    def __init__(self):
        # Initialize all agents
        self.greeting_agent = GreetingAgent()
        self.lookup_agent = LookupAgent()
        self.scheduling_agent = SchedulingAgent()
        self.insurance_agent = InsuranceAgent()
        self.confirmation_agent = ConfirmationAgent(mock_mode=True)
        self.form_agent = FormDistributionAgent(mock_mode=True)
        self.reminder_agent = ReminderAgent(mock_mode=True)
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
    
    def _create_workflow(self):
        """Create the LangGraph workflow with conditional routing"""
        
        # Define the workflow
        workflow = StateGraph(BookingState)
        
        # Add nodes
        workflow.add_node("greeting", self._greeting_node)
        workflow.add_node("lookup", self._lookup_node)
        workflow.add_node("scheduling", self._scheduling_node)
        workflow.add_node("slot_selection", self._slot_selection_node)
        workflow.add_node("insurance", self._insurance_node)
        workflow.add_node("confirmation", self._confirmation_node)
        workflow.add_node("form_distribution", self._form_distribution_node)
        workflow.add_node("reminder_setup", self._reminder_setup_node)
        
        # Define edges with conditional routing
        workflow.set_entry_point("greeting")
        
        # Conditional routing based on completion status
        workflow.add_conditional_edges(
            "greeting",
            self._should_continue_from_greeting,
            {
                "continue": "lookup",
                "stay": "greeting"
            }
        )
        
        workflow.add_edge("lookup", "scheduling")
        
        workflow.add_conditional_edges(
            "scheduling",
            self._should_continue_from_scheduling,
            {
                "continue": "slot_selection",
                "no_slots": END
            }
        )
        
        workflow.add_conditional_edges(
            "slot_selection",
            self._should_continue_from_slot_selection,
            {
                "continue": "insurance",
                "stay": "slot_selection"
            }
        )
        
        workflow.add_conditional_edges(
            "insurance",
            self._should_continue_from_insurance,
            {
                "continue": "confirmation",
                "stay": "insurance"
            }
        )
        
        workflow.add_edge("confirmation", "form_distribution")
        workflow.add_edge("form_distribution", "reminder_setup")
        workflow.add_edge("reminder_setup", END)
        
        return workflow.compile()
    
    def _greeting_node(self, state: BookingState) -> BookingState:
        """Greeting agent node - Collect patient information"""
        try:
            user_input = state.get("user_input")
            
            # If no user input and first time, show greeting
            if (user_input is None or user_input == "") and not state.get("conversation_history"):
                response = self.greeting_agent.get_greeting_message()
                state["agent_response"] = response
                state["conversation_history"].append(f"Agent: {response}")
                return state
            
            # Skip processing if no valid user input
            if user_input is None or user_input.strip() == "":
                return state
            
            # Process user input
            response, is_complete, data = self.greeting_agent.process_input(user_input, state)
            
            if is_complete:
                # Convert to PatientInfo model
                from models import PatientInfo
                try:
                    patient_info = PatientInfo(**data)
                    state["patient_info"] = patient_info
                    state["current_step"] = "lookup"
                    print(f"✅ Patient info collected: {patient_info.patient_name}")
                except Exception as e:
                    print(f"❌ Error creating PatientInfo: {e}")
                    response = f"Error processing patient information: {e}"
            
            state["agent_response"] = response
            if user_input and user_input.strip():
                state["conversation_history"].append(f"User: {user_input}")
            state["conversation_history"].append(f"Agent: {response}")
            
        except Exception as e:
            print(f"❌ Error in greeting node: {e}")
            state["agent_response"] = f"Sorry, there was an error processing your information: {e}"
            state["errors"].append(str(e))
        
        return state
    
    def _lookup_node(self, state: BookingState) -> BookingState:
        """Lookup agent node - Search patient database"""
        try:
            if state.get("current_step") == "lookup" and state.get("patient_info"):
                # Convert PatientInfo to dict for lookup
                patient_data = {
                    'patient_name': state["patient_info"].patient_name,
                    'date_of_birth': state["patient_info"].date_of_birth,
                    'preferred_doctor': state["patient_info"].preferred_doctor,
                    'location': state["patient_info"].location
                }
                
                response, lookup_result = self.lookup_agent.search_patient(patient_data)
                
                state["lookup_result"] = lookup_result
                state["current_step"] = "scheduling"
                state["agent_response"] = response
                state["conversation_history"].append(f"Agent: {response}")
                
                print(f"✅ Patient lookup completed: {lookup_result.patient_type if lookup_result else 'Not found'}")
                
        except Exception as e:
            print(f"❌ Error in lookup node: {e}")
            state["agent_response"] = f"Error looking up patient information: {e}"
            state["errors"].append(str(e))
        
        return state
    
    def _scheduling_node(self, state: BookingState) -> BookingState:
        """Scheduling agent node - Find available slots"""
        try:
            if state.get("current_step") == "scheduling" and state.get("patient_info") and state.get("lookup_result"):
                patient_data = {
                    'patient_name': state["patient_info"].patient_name,
                    'preferred_doctor': state["patient_info"].preferred_doctor,
                    'location': state["patient_info"].location
                }
                
                response, slots = self.scheduling_agent.find_available_slots(
                    patient_data, state["lookup_result"]
                )
                
                state["available_slots"] = slots
                state["current_step"] = "slot_selection"
                state["agent_response"] = response
                state["conversation_history"].append(f"Agent: {response}")
                
                print(f"✅ Found {len(slots)} available slots")
                
        except Exception as e:
            print(f"❌ Error in scheduling node: {e}")
            state["agent_response"] = f"Error finding available slots: {e}"
            state["errors"].append(str(e))
        
        return state
    
    def _slot_selection_node(self, state: BookingState) -> BookingState:
        """Handle slot selection from user"""
        try:
            user_input = state.get("user_input", "")
            available_slots = state.get("available_slots", [])
            
            if not available_slots:
                state["agent_response"] = "No available slots found. Please try different preferences."
                return state
            
            # For demo purposes, auto-select first slot if no specific input
            if not user_input or user_input.lower() in ['1', 'first', 'yes']:
                selected_slot = available_slots[0]
                state["selected_slot"] = selected_slot
                state["current_step"] = "insurance"
                
                response = f"✅ **Slot Selected!**\n\nYou've selected:\n**Date**: {selected_slot.date}\n**Time**: {selected_slot.time}\n**Doctor**: {selected_slot.doctor}\n**Location**: {selected_slot.location}\n\nNow let's collect your insurance information..."
                state["agent_response"] = response
                state["conversation_history"].append(f"Agent: {response}")
                
                print(f"✅ Slot selected: {selected_slot.date} at {selected_slot.time}")
            else:
                # Handle specific slot selection
                try:
                    slot_index = int(user_input) - 1
                    if 0 <= slot_index < len(available_slots):
                        selected_slot = available_slots[slot_index]
                        state["selected_slot"] = selected_slot
                        state["current_step"] = "insurance"
                        
                        response = f"✅Slot Selected!\n\nYou've selected slot {user_input}:\n*Date**: {selected_slot.date}\n**Time**: {selected_slot.time}\n**Doctor**: {selected_slot.doctor}\n**Location**: {selected_slot.location}\n\nNow let's collect your insurance information..."
                        state["agent_response"] = response
                        state["conversation_history"].append(f"Agent: {response}")
                    else:
                        state["agent_response"] = f"Please select a valid slot number (1-{len(available_slots)})"
                except ValueError:
                    state["agent_response"] = f"Please enter a slot number (1-{len(available_slots)}) or say 'first' for the first available slot."
                
        except Exception as e:
            print(f"❌ Error in slot selection node: {e}")
            state["agent_response"] = f"Error selecting slot: {e}"
            state["errors"].append(str(e))
        
        return state
    
    def _insurance_node(self, state: BookingState) -> BookingState:
        """Insurance agent node - Collect insurance information"""
        try:
            user_input = state.get("user_input", "")
            
            # Initialize insurance agent if needed
            if not hasattr(state, "_insurance_started"):
                greeting = self.insurance_agent.get_insurance_greeting(state["patient_info"].patient_name)
                state["agent_response"] = greeting
                state["conversation_history"].append(f"Agent: {greeting}")
                state["_insurance_started"] = True
                return state
            
            # Process insurance input
            response, is_complete, data = self.insurance_agent.process_input(user_input)
            
            if is_complete:
                # Convert to InsuranceInfo model
                from models import InsuranceInfo
                try:
                    insurance_info = InsuranceInfo(**data)
                    state["insurance_info"] = insurance_info
                    state["current_step"] = "confirmation"
                    print(f"✅ Insurance info collected: {insurance_info.primary_carrier}")
                except Exception as e:
                    print(f"❌ Error creating InsuranceInfo: {e}")
                    response = f"Error processing insurance information: {e}"
            
            state["agent_response"] = response
            state["conversation_history"].append(f"User: {user_input}")
            state["conversation_history"].append(f"Agent: {response}")
            
        except Exception as e:
            print(f"❌ Error in insurance node: {e}")
            state["agent_response"] = f"Error collecting insurance information: {e}"
            state["errors"].append(str(e))
        
        return state
    
    def _confirmation_node(self, state: BookingState) -> BookingState:
        """Confirmation node - Complete appointment booking with Excel export"""
        try:
            # Prepare appointment data
            appointment_data = {
                'date': state["selected_slot"].date,
                'time': state["selected_slot"].time,
                'doctor': state["selected_slot"].doctor,
                'location': state["selected_slot"].location
            }
            
            # Confirm appointment
            response, success, confirmation_record = self.confirmation_agent.confirm_appointment(
                appointment_data,
                {
                    'patient_name': state["patient_info"].patient_name,
                    'email': state["patient_info"].email,
                    'phone': state["patient_info"].phone,
                    'date_of_birth': state["patient_info"].date_of_birth
                },
                {
                    'primary_carrier': state["insurance_info"].primary_carrier,
                    'member_id': state["insurance_info"].member_id,
                    'group_number': state["insurance_info"].group_number
                },
                {
                    'date': state["selected_slot"].date,
                    'time': state["selected_slot"].time,
                    'doctor': state["selected_slot"].doctor,
                    'location': state["selected_slot"].location,
                    'duration_available': state["selected_slot"].duration_available
                }
            )
            
            if success:
                # Export to Excel
                export_response, export_success = self.confirmation_agent.export_to_excel(confirmation_record)
                
                state["final_booking"] = confirmation_record
                state["excel_exported"] = export_success
                state["current_step"] = "form_distribution"
                
                combined_response = f"{response}\n\n{export_response}"
                state["agent_response"] = combined_response
                
                print(f"✅ Appointment confirmed: {confirmation_record['appointment_id']}")
                print(f"✅ Excel export: {'Success' if export_success else 'Failed'}")
            else:
                state["agent_response"] = f"❌ Appointment confirmation failed: {response}"
                state["errors"].append(response)
            
            state["conversation_history"].append(f"Agent: {state['agent_response']}")
            
        except Exception as e:
            print(f"❌ Error in confirmation node: {e}")
            state["agent_response"] = f"Error confirming appointment: {e}"
            state["errors"].append(str(e))
        
        return state
    
    def _form_distribution_node(self, state: BookingState) -> BookingState:
        """Form distribution node - Send intake forms"""
        try:
            if state.get("final_booking"):
                patient_type = state["lookup_result"].patient_type if state.get("lookup_result") else "new"
                
                appointment_data = {
                    'date': state["selected_slot"].date,
                    'time': state["selected_slot"].time
                }
                
                response, success = self.form_agent.send_intake_forms(
                    state["patient_info"].email,
                    state["patient_info"].patient_name,
                    appointment_data,
                    patient_type
                )
                
                state["form_sent"] = success
                state["current_step"] = "reminder_setup"
                state["agent_response"] = response
                state["conversation_history"].append(f"Agent: {response}")
                
                print(f"✅ Forms sent: {'Success' if success else 'Failed'}")
            
        except Exception as e:
            print(f"❌ Error in form distribution node: {e}")
            state["agent_response"] = f"Error sending forms: {e}"
            state["errors"].append(str(e))
        
        return state
    
    def _reminder_setup_node(self, state: BookingState) -> BookingState:
        """Reminder setup node - Schedule automated reminders"""
        try:
            if state.get("final_booking"):
                # Create mock appointment object for reminder scheduling
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
                
                mock_appointment = MockAppointment(state)
                reminders = self.reminder_agent.schedule_reminders(mock_appointment)
                
                state["reminders_scheduled"] = True
                
                response = (
                    f"✅ **Reminder System Activated!**\n\n"
                    f"**{len(reminders)} automated reminders scheduled:**\n"
                    f"• Reminder 1: 24 hours before (Regular confirmation)\n"
                    f"• Reminder 2: 2 hours before (Form completion check)\n"
                    f"• Reminder 3: 1 hour before (Final confirmation)\n\n"
                    f"🎉 **Complete Appointment Booking Successful!**\n\n"
                    f"**Summary:**\n"
                    f"• Patient: {state['patient_info'].patient_name}\n"
                    f"• Appointment: {state['selected_slot'].date} at {state['selected_slot'].time}\n"
                    f"• Doctor: {state['selected_slot'].doctor}\n"
                    f"• Location: {state['selected_slot'].location}\n"
                    f"• Appointment ID: {state['final_booking']['appointment_id']}\n"
                    f"• Excel Export: ✅ Completed\n"
                    f"• Forms Sent: ✅ Completed\n"
                    f"• Reminders: ✅ Scheduled\n\n"
                    f"Thank you for using our Medical Scheduling System!"
                )
                
                state["agent_response"] = response
                state["conversation_history"].append(f"Agent: {response}")
                
                print(f"✅ Reminders scheduled: {len(reminders)}")
                print("🎉 Complete workflow finished successfully!")
            
        except Exception as e:
            print(f"❌ Error in reminder setup node: {e}")
            state["agent_response"] = f"Error setting up reminders: {e}"
            state["errors"].append(str(e))
        
        return state
    
    # Conditional routing functions
    def _should_continue_from_greeting(self, state: BookingState) -> str:
        """Determine if we should continue from greeting"""
        return "continue" if state.get("patient_info") else "stay"
    
    def _should_continue_from_scheduling(self, state: BookingState) -> str:
        """Determine if we should continue from scheduling"""
        slots = state.get("available_slots", [])
        return "continue" if slots else "no_slots"
    
    def _should_continue_from_slot_selection(self, state: BookingState) -> str:
        """Determine if we should continue from slot selection"""
        return "continue" if state.get("selected_slot") else "stay"
    
    def _should_continue_from_insurance(self, state: BookingState) -> str:
        """Determine if we should continue from insurance"""
        return "continue" if state.get("insurance_info") else "stay"
    
    def process_user_input(self, user_input: str, current_state: Optional[BookingState] = None) -> BookingState:
        """Process user input through the LangGraph workflow"""
        if current_state is None:
            current_state = create_initial_state()
        
        # Update state with user input
        current_state["user_input"] = user_input
        
        # Run the workflow
        result = self.workflow.invoke(current_state)
        
        return result
    
    def start_conversation(self) -> BookingState:
        """Start the conversation flow"""
        initial_state = create_initial_state()
        
        # Run the workflow with empty input to get greeting
        result = self.workflow.invoke(initial_state)
        
        return result

# Interactive demo function
def interactive_demo():
    """Interactive demo of the LangGraph workflow"""
    print("🏥 Medical Appointment Scheduling System - LangGraph Demo")
    print("=" * 60)
    
    app = MedicalSchedulerApp()
    
    # Start conversation
    state = app.start_conversation()
    print(f"\n🤖 Agent: {state['agent_response']}")
    
    # Interactive loop
    while state.get("current_step") != "completed":
        user_input = input("\n👤 You: ")
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        
        # Process input through workflow
        state = app.process_user_input(user_input, state)
        print(f"\n🤖 Agent: {state['agent_response']}")
        
        # Check if workflow is complete
        if state.get("reminders_scheduled"):
            print("\n🎉 Appointment booking completed successfully!")
            break
    
    return state

# Test the application
if __name__ == "__main__":
    # Run interactive demo
    final_state = interactive_demo()
    
    print(f"\n📊 Final State Summary:")
    print(f"Patient: {final_state.get('patient_info', {}).get('patient_name', 'N/A') if final_state.get('patient_info') else 'N/A'}")
    print(f"Excel Exported: {final_state.get('excel_exported', False)}")
    print(f"Forms Sent: {final_state.get('form_sent', False)}")
    print(f"Reminders Scheduled: {final_state.get('reminders_scheduled', False)}")
    print(f"Errors: {len(final_state.get('errors', []))}")