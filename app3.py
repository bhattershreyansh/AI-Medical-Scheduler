#!/usr/bin/env python3
"""
Streamlit UI for Medical Appointment Scheduling AI Agent
Assignment: AI Scheduling Agent Case Study - Intern
"""

import streamlit as st
import sys
import os
from datetime import datetime
import pandas as pd

# Add project root to path
sys.path.append('.')

# Import our main application
from main_simple import MedicalSchedulerApp

# Page configuration
st.set_page_config(
    page_title="Medical Appointment Scheduler",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Professional Styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Enhanced Header */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #1a365d;
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem;
        background: linear-gradient(135deg, #2c5282 0%, #3182ce 100%);
        color: white;
        border-radius: 12px;
        box-shadow: 0px 8px 25px rgba(44, 82, 130, 0.2);
    }
    
    /* Enhanced Chat Messages */
    .chat-message {
        font-family: 'Inter', sans-serif;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        max-width: 80%;
        line-height: 1.6;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
        animation: slideIn 0.3s ease-out;
        position: relative;
        border: 1px solid #e2e8f0;
    }
    
    .user-message {
        background: linear-gradient(135deg, #2c5282 0%, #3182ce 100%);
        color: white;
        margin-left: auto;
        text-align: right;
        border-bottom-right-radius: 5px;
    }
    
    .agent-message {
        background: #ffffff;
        color: #2d3748;
        margin-right: auto;
        text-align: left;
        border-bottom-left-radius: 5px;
        border-left: 4px solid #3182ce;
    }

    /* Enhanced Buttons */
    .stButton > button {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1.5rem;
        transition: all 0.2s ease;
        background: linear-gradient(135deg, #2c5282 0%, #3182ce 100%);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0px 4px 12px rgba(44, 82, 130, 0.3);
    }

    /* Suggestion Cards */
    .suggestion-card {
        background: #f7fafc;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .suggestion-card:hover {
        background: #edf2f7;
        transform: translateY(-1px);
    }

    /* Enhanced Metrics */
    .metric-card {
        background: linear-gradient(135deg, #2c5282 0%, #3182ce 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* Success Celebration */
    .celebration-box {
        font-family: 'Inter', sans-serif;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        background: linear-gradient(135deg, #2c5282 0%, #3182ce 100%);
        color: white;
        margin: 2rem 0;
    }

    /* Progress Indicators */
    .progress-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        margin: 0.5rem 0;
        background: #f7fafc;
        border-radius: 8px;
        border-left: 4px solid #3182ce;
        transition: all 0.2s ease;
    }
    
    .progress-item:hover {
        background: #edf2f7;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            padding: 1.5rem;
        }
        
        .chat-message {
            max-width: 95%;
            padding: 1rem;
        }
    }

    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Input Enhancement */
    .stChatInput > div > div > input {
        border-radius: 20px;
        border: 2px solid #e2e8f0;
        padding: 1rem 1.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .stChatInput > div > div > input:focus {
        border-color: #3182ce;
        box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
    }
    
    /* Remove default markdown styling */
    .stMarkdown {
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom metric styling */
    .stMetric {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'app' not in st.session_state:
        st.session_state.app = MedicalSchedulerApp()
    
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = "greeting"
    
    if 'appointment_completed' not in st.session_state:
        st.session_state.appointment_completed = False

def display_header():
    """Display the enhanced professional header"""
    st.markdown("""
    <div class="main-header">
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem;">
            <div>
                <h1 style="margin: 0; font-size: 2.8rem; font-weight: 700;">Medical Scheduling System</h1>
                <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">Intelligent Appointment Scheduling</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display enhanced sidebar with system information and controls"""
    st.markdown("### System Dashboard")
    
    # Enhanced System Status
    st.markdown("#### System Status")
    
    # Create metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>7</h3>
            <p>AI Agents</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h3>4</h3>
            <p>Doctors</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>3</h3>
            <p>Locations</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Current State
    if hasattr(st.session_state, 'app'):
        state_summary = st.session_state.app.get_state_summary()
        
        st.markdown("#### Current Session")
        
        # Current step with visual indicator
        current_step = state_summary.get('current_step', 'Not started')
        step_display = {
            'greeting': 'Initial Conversation',
            'slot_selection': 'Time Selection',
            'insurance': 'Insurance Processing',
            'completed': 'Appointment Complete'
        }
        
        st.markdown(f"""
        <div class="suggestion-card">
            <h4>{step_display.get(current_step, current_step.replace('_', ' ').title())}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if state_summary.get('patient_name'):
            st.markdown(f"""
            <div class="suggestion-card">
                <h4>Patient: {state_summary['patient_name']}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced Progress indicators
        st.markdown("#### Progress Tracker")
        progress_items = [
            ("Patient Info", state_summary.get('patient_name') is not None),
            ("Excel Export", state_summary.get('excel_exported', False)),
            ("Forms Sent", state_summary.get('form_sent', False)),
            ("Reminders", state_summary.get('reminders_scheduled', False))
        ]
        
        for item, completed in progress_items:
            status_color = "#38a169" if completed else "#718096"
            status_icon = "✓" if completed else "⋯"
            
            st.markdown(f"""
            <div class="progress-item" style="border-left-color: {status_color};">
                <span style="margin-right: 0.5rem; color: {status_color}; font-weight: 500;">{status_icon}</span>
                <span>{item}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced Controls
    st.markdown("#### Session Controls")
    
    if st.button("Reset Session", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # System Features
    st.markdown("#### System Features")
    
    features = [
        ("AI Agents", "7 specialized agents"),
        ("Scheduling", "Smart time logic"),
        ("Insurance", "Multi-carrier support"),
        ("Export", "Professional reports"),
        ("Forms", "Automated distribution"),
        ("Reminders", "3-tier system")
    ]
    
    for feature, description in features:
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0;">
            <div>
                <span style="font-weight: 500;">{feature}</span><br>
                <small style="color: #718096;">{description}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("#### Quick Actions")
    
    if st.button("Demo Mode", type="primary", use_container_width=True):
        st.info("Use the suggestion buttons for quick demonstration")

def display_chat_interface():
    """Display the enhanced chat interface with clickable options"""
    st.subheader("AI Agent Conversation")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display conversation history
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message agent-message">
                    <strong>Agent:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Input area with smart suggestions
    if not st.session_state.appointment_completed:
        if not st.session_state.conversation_started:
            st.markdown("### Ready to Schedule Your Appointment?")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Start Appointment Booking", type="primary", use_container_width=True):
                    greeting = st.session_state.app.start_conversation()
                    st.session_state.messages.append({"role": "agent", "content": greeting})
                    st.session_state.conversation_started = True
                    st.rerun()
            with col2:
                if st.button("Quick Demo", type="secondary", use_container_width=True):
                    demo_response = "Hello! I'm your scheduling assistant. Let me help you book an appointment. I'll need some basic information from you. Let's start with your full name."
                    st.session_state.messages.append({"role": "agent", "content": demo_response})
                    st.session_state.conversation_started = True
                    st.rerun()
        else:
            current_step = st.session_state.app.state.get("current_step", "greeting")
            display_smart_suggestions(current_step)
            
            user_input = st.chat_input("Type your message here...")
            
            if user_input:
                process_user_input(user_input)
    else:
        display_completion_summary()

def display_smart_suggestions(current_step):
    """Display context-aware selection options based on AI conversation"""
    
    if st.session_state.messages:
        last_agent_message = ""
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "agent":
                last_agent_message = msg["content"].lower()
                break
        
        if "doctor" in last_agent_message and "prefer" in last_agent_message:
            st.markdown("Select Doctor")
            doctors = ["Dr. Naveen", "Dr. Aish", "Dr. Shreyansh", "Dr. Naresh"]
            cols = st.columns(len(doctors))
            for i, doctor in enumerate(doctors):
                with cols[i]:
                    if st.button(doctor, key=f"doc_{doctor}", use_container_width=True):
                        process_user_input(doctor)
        
        elif "location" in last_agent_message and ("prefer" in last_agent_message or "where" in last_agent_message):
            st.markdown("Select Location")
            locations = ["Gachibowli", "Jubliee Hills", "Banjara Hills"]
            cols = st.columns(len(locations))
            for i, location in enumerate(locations):
                with cols[i]:
                    if st.button(location, key=f"loc_{location}", use_container_width=True):
                        process_user_input(location)
        
        elif current_step == "slot_selection" and st.session_state.app.state.get("available_slots"):
            st.markdown("Select Appointment Slot")
            available_slots = st.session_state.app.state.get("available_slots", [])
            
            if available_slots:
                slots_per_row = 3
                for i in range(0, len(available_slots), slots_per_row):
                    row_slots = available_slots[i:i+slots_per_row]
                    cols = st.columns(len(row_slots))
                    
                    for j, slot in enumerate(row_slots):
                        with cols[j]:
                            slot_number = i + j + 1
                            date_str = slot.date
                            time_str = slot.time
                            doctor_str = slot.doctor
                            
                            button_label = f"Slot {slot_number}\n{date_str}\n{time_str}\n{doctor_str}"
                            
                            if st.button(button_label, key=f"slot_{slot_number}", use_container_width=True):
                                process_user_input(str(slot_number))

def process_user_input(user_input):
    """Process user input and update conversation"""
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.spinner("AI Agent is processing..."):
        try:
            response = st.session_state.app.process_user_input(user_input)
            st.session_state.messages.append({"role": "agent", "content": response})
            
            if st.session_state.app.state.get("current_step") == "completed":
                st.session_state.appointment_completed = True
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.session_state.messages.append({"role": "agent", "content": error_msg})
    
    st.rerun()

def display_completion_summary():
    """Display enhanced completion summary"""
    st.markdown("""
    <div class="celebration-box">
        Appointment Successfully Booked!
        <br><br>
        Your appointment has been confirmed and all systems have been updated.
    </div>
    """, unsafe_allow_html=True)
    
    state_summary = st.session_state.app.get_state_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status = "Success" if state_summary.get('excel_exported') else "Failed"
        st.metric("Excel Export", status)
    with col2:
        status = "Sent" if state_summary.get('form_sent') else "Failed"
        st.metric("Forms", status)
    with col3:
        status = "Scheduled" if state_summary.get('reminders_scheduled') else "Not Set"
        st.metric("Reminders", status)
    with col4:
        st.metric("Status", "Complete")
    
    st.markdown("### Next Steps")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("View Email Confirmation", type="secondary", use_container_width=True):
            st.info("Email confirmation sent to your registered email address")
    
    with col2:
        if st.button("Download Forms", type="secondary", use_container_width=True):
            st.info("Intake forms are available in your email")
    
    with col3:
        if st.button("Book Another", type="primary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def display_quick_demo():
    """Display enhanced quick demo section"""
    with st.expander("Complete Demo Walkthrough", expanded=False):
        
        st.markdown("""
        <div class="suggestion-card">
            <h3>Complete Demo Flow</h3>
            <p>Follow this sequence for a full system demonstration:</p>
        </div>
        """, unsafe_allow_html=True)
        
        demo_steps = [
            {
                "step": "Start Conversation",
                "action": "Click 'Start Appointment Booking'",
                "tip": "Initiates the AI agent conversation"
            },
            {
                "step": "Patient Information",
                "action": "Provide: 'John Smith'",
                "tip": "AI will ask for each detail individually"
            },
            {
                "step": "Contact Details",
                "action": "Provide: DOB, Phone, Email",
                "tip": "Use quick-fill buttons for faster demo"
            },
            {
                "step": "Doctor & Location",
                "action": "Select: 'Dr. Naveen' and 'Gachibowli'",
                "tip": "Click the suggestion buttons for instant selection"
            },
            {
                "step": "Appointment Slot",
                "action": "Choose slot number: '1', '2', or '3'",
                "tip": "Use the quick slot buttons above chat"
            },
            {
                "step": "Insurance Information",
                "action": "Select carrier, member ID, group number",
                "tip": "Use insurance quick-fill options"
            },
            {
                "step": "Confirmation",
                "action": "System automatically completes booking",
                "tip": "Watch for Excel export and form distribution"
            }
        ]
        
        for step_info in demo_steps:
            st.markdown(f"""
            <div style="margin: 1rem 0; padding: 1rem; background: #f7fafc; border-radius: 8px; border-left: 4px solid #3182ce;">
                <h4 style="margin: 0 0 0.5rem 0; color: #2d3748;">{step_info['step']}</h4>
                <p style="margin: 0 0 0.5rem 0; font-weight: 500;">{step_info['action']}</p>
                <small style="color: #718096;">{step_info['tip']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="suggestion-card" style="background: linear-gradient(135deg, #2c5282 0%, #3182ce 100%); color: white;">
            <h4>Pro Tips for Quick Demo</h4>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>Use the suggestion buttons for instant input</li>
                <li>The AI responds to natural language</li>
                <li>Watch the progress tracker in the sidebar</li>
                <li>Each step builds on the previous one</li>
                <li>Full demo takes about 2-3 minutes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def display_system_features():
    """Display system features and capabilities"""
    st.subheader("System Features & Capabilities")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        AI Agents
        - Greeting Agent
        - Patient Lookup Agent
        - Scheduling Agent
        - Insurance Agent
        - Confirmation Agent
        - Form Distribution Agent
        - Reminder Agent
        """)
    
    with col2:
        st.markdown("""
        Data Management
        - Synthetic Patients
        - Doctor Schedules
        - Smart Duration Logic
        - Excel Export for Admin
        - Professional Formatting
        """)
    
    with col3:
        st.markdown("""
        Workflow Features
        - Natural Language Processing
        - Multi-turn Conversations
        - State Management
        - Error Handling
        - Mock Email/SMS
        - 3-Tier Reminder System
        """)

def display_excel_data():
    """Display Excel export data if available"""
    if st.session_state.appointment_completed:
        st.subheader("Excel Export Data")
        
        try:
            appointments_df = pd.read_excel("data/appointments.xlsx")
            
            if not appointments_df.empty:
                st.success(f"Found {len(appointments_df)} appointments in Excel file")
                
                latest_appointment = appointments_df.iloc[-1]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("Latest Appointment:")
                    st.write(f"ID: {latest_appointment.get('appointment_id', 'N/A')}")
                    st.write(f"Patient: {latest_appointment.get('patient_name', 'N/A')}")
                    st.write(f"Doctor: {latest_appointment.get('doctor', 'N/A')}")
                    st.write(f"Date: {latest_appointment.get('appointment_date', 'N/A')}")
                    st.write(f"Time: {latest_appointment.get('appointment_time', 'N/A')}")
                
                with col2:
                    st.markdown("Status:")
                    st.write(f"Excel Exported: {'Yes' if latest_appointment.get('excel_exported') else 'No'}")
                    st.write(f"Forms Sent: {'Yes' if latest_appointment.get('form_sent') else 'No'}")
                    st.write(f"Insurance: {latest_appointment.get('insurance_carrier', 'N/A')}")
                    st.write(f"Status: {latest_appointment.get('status', 'N/A')}")
                
                with st.expander("View Full Excel Data", expanded=False):
                    st.dataframe(appointments_df, width='stretch')
            else:
                st.info("Excel file exists but is empty")
                
        except FileNotFoundError:
            st.warning("Excel file not found. Complete an appointment booking to generate data.")
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")

def main():
    """Main Streamlit application"""
    initialize_session_state()
    display_header()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_chat_interface()
        display_quick_demo()
        display_excel_data()
    
    with col2:
        display_sidebar()
    
    st.markdown("---")
    display_system_features()
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; padding: 1rem;">
        Medical Appointment Scheduling AI Agent
        <br>
        <small>Built with LangGraph + LangChain | Streamlit UI | Assignment Demo</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()