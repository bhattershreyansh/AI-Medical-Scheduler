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

# Phase 3: Enhanced Professional Styling
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        box-shadow: 0px 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.1;
    }
    
    .main-header > * {
        position: relative;
        z-index: 1;
    }

    /* Enhanced Chat Messages */
    .chat-message {
        font-family: 'Inter', sans-serif;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 20px;
        max-width: 80%;
        line-height: 1.6;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
        animation: slideIn 0.5s ease-out;
        position: relative;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        text-align: right;
        border-bottom-right-radius: 5px;
    }
    
    .agent-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: auto;
        text-align: left;
        border-bottom-left-radius: 5px;
    }

    /* Enhanced Buttons */
    .stButton > button {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.15);
    }

    /* Suggestion Cards */
    .suggestion-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .suggestion-card:hover {
        transform: translateY(-2px);
        box-shadow: 0px 8px 25px rgba(0,0,0,0.1);
    }

    /* Enhanced Metrics */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(240, 147, 251, 0.3);
        margin-bottom: 1rem;
    }

    /* Success Celebration Enhanced */
    .celebration-box {
        font-family: 'Inter', sans-serif;
        padding: 3rem;
        border-radius: 24px;
        text-align: center;
        font-size: 1.4rem;
        font-weight: 600;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0px 10px 40px rgba(102, 126, 234, 0.3);
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .celebration-box::before {
        content: '🎉';
        position: absolute;
        font-size: 4rem;
        top: -1rem;
        right: -1rem;
        opacity: 0.2;
        animation: bounce 2s infinite;
    }

    /* Progress Indicators */
    .progress-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        margin: 0.5rem 0;
        background: #f8fafc;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .progress-item:hover {
        background: #e2e8f0;
        transform: translateX(5px);
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            padding: 1.5rem;
        }
        
        .chat-message {
            max-width: 95%;
            padding: 0.75rem 1rem;
        }
        
        .celebration-box {
            padding: 2rem;
            font-size: 1.2rem;
        }
    }

    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
        60% {
            transform: translateY(-5px);
        }
    }
    
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(10px);}
        to {opacity: 1; transform: translateY(0);}
    }
    
    /* Loading Spinner Enhancement */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Input Enhancement */
    .stChatInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e2e8f0;
        padding: 1rem 1.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .stChatInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
            <div style="font-size: 3rem;">🏥</div>
            <div>
                <h1 style="margin: 0; font-size: 2.8rem; font-weight: 700;">MedSchedule AI</h1>
                <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">Intelligent Medical Appointment Scheduling System</p>
                <p style="margin: 0; font-size: 0.9rem; opacity: 0.7;">Powered by LangGraph + LangChain Multi-Agent Architecture</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display enhanced sidebar with system information and controls"""
    st.markdown("### 🔧 System Dashboard")
    
    # Enhanced System Status
    st.markdown("#### 📊 System Status")
    
    # Create metrics in a more visual way
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
            <h3>50</h3>
            <p>Patients</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>4</h3>
            <p>Doctors</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h3>3</h3>
            <p>Locations</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Current State
    if hasattr(st.session_state, 'app'):
        state_summary = st.session_state.app.get_state_summary()
        
        st.markdown("#### 🎯 Current Session")
        
        # Current step with visual indicator
        current_step = state_summary.get('current_step', 'Not started')
        step_emoji = {
            'greeting': '👋',
            'slot_selection': '⏰',
            'insurance': '🏥',
            'completed': '✅'
        }
        
        st.markdown(f"""
        <div class="suggestion-card">
            <h4>{step_emoji.get(current_step, '🔄')} {current_step.replace('_', ' ').title()}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if state_summary.get('patient_name'):
            st.markdown(f"""
            <div class="suggestion-card">
                <h4>👤 {state_summary['patient_name']}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced Progress indicators
        st.markdown("#### ✅ Progress Tracker")
        progress_items = [
            ("👤 Patient Info", state_summary.get('patient_name') is not None),
            ("📊 Excel Export", state_summary.get('excel_exported', False)),
            ("📋 Forms Sent", state_summary.get('form_sent', False)),
            ("⏰ Reminders", state_summary.get('reminders_scheduled', False))
        ]
        
        for item, completed in progress_items:
            status_color = "#10b981" if completed else "#6b7280"
            status_icon = "✅" if completed else "⏳"
            
            st.markdown(f"""
            <div class="progress-item" style="border-left-color: {status_color};">
                <span style="margin-right: 0.5rem;">{status_icon}</span>
                <span>{item}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced Controls
    st.markdown("#### 🔄 Session Controls")
    
    if st.button("🔄 Reset Session", type="secondary", use_container_width=True):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Enhanced Assignment Info
    st.markdown("#### 📋 System Features")
    
    features = [
        ("🤖 AI Agents", "7 specialized agents"),
        ("💾 Database", "50 synthetic patients"),
        ("⏰ Scheduling", "Smart 30/60 min logic"),
        ("🏥 Insurance", "Multi-carrier support"),
        ("📊 Export", "Professional Excel reports"),
        ("📧 Forms", "Automated distribution"),
        ("🔔 Reminders", "3-tier system")
    ]
    
    for feature, description in features:
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0;">
            <span style="margin-right: 0.75rem; font-size: 1.2rem;">{feature.split()[0]}</span>
            <div>
                <span style="font-weight: 500;">{feature.split(' ', 1)[1]}</span><br>
                <small style="color: #6b7280;">{description}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("#### ⚡ Quick Actions")
    
    if st.button("🚀 Demo Mode", type="primary", use_container_width=True):
        st.info("💡 Use the suggestion buttons above for quick demo!")
    
    if st.button("📖 Help Guide", type="secondary", use_container_width=True):
        st.info("""
        **How to use:**
        1. Click 'Start Appointment Booking'
        2. Use suggestion buttons or type naturally
        3. Follow the AI agent's guidance
        4. Complete all steps for full demo
        """)

def display_chat_interface():
    """Display the enhanced chat interface with clickable options"""
    st.subheader("💬 AI Agent Conversation")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display conversation history
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message agent-message">
                    <strong>🤖 Agent:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Input area with smart suggestions
    if not st.session_state.appointment_completed:
        # Start conversation if not started
        if not st.session_state.conversation_started:
            st.markdown("### 🚀 Ready to Schedule Your Appointment?")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🚀 Start Appointment Booking", type="primary", use_container_width=True):
                    greeting = st.session_state.app.start_conversation()
                    st.session_state.messages.append({"role": "agent", "content": greeting})
                    st.session_state.conversation_started = True
                    st.rerun()
            with col2:
                if st.button("📋 Quick Demo", type="secondary", use_container_width=True):
                    demo_response = "Hi! I'm your AI scheduling assistant. Let me help you book an appointment. I'll need some basic information from you. Let's start with your full name."
                    st.session_state.messages.append({"role": "agent", "content": demo_response})
                    st.session_state.conversation_started = True
                    st.rerun()
        else:
            # Clean selection options only when needed
            current_step = st.session_state.app.state.get("current_step", "greeting")
            display_smart_suggestions(current_step)
            
            # Clean input area
            user_input = st.chat_input("Type your message here...")
            
            if user_input:
                process_user_input(user_input)
    else:
        display_completion_summary()

def display_smart_suggestions(current_step):
    """Display context-aware selection options based on AI conversation"""
    
    # Check the last agent message to determine what to show
    if st.session_state.messages:
        last_agent_message = ""
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "agent":
                last_agent_message = msg["content"].lower()
                break
        
        # Show doctor selection only when AI asks for doctor
        if "doctor" in last_agent_message and "prefer" in last_agent_message:
            st.markdown("👨‍⚕️ Select Doctor")
            doctors = ["Dr. Naveen", "Dr. Smith", "Dr. Johnson", "Dr. Williams"]
            cols = st.columns(len(doctors))
            for i, doctor in enumerate(doctors):
                with cols[i]:
                    if st.button(doctor, key=f"doc_{doctor}", use_container_width=True):
                        process_user_input(doctor)
        
        # Show location selection only when AI asks for location
        elif "location" in last_agent_message and ("prefer" in last_agent_message or "where" in last_agent_message):
            st.markdown("📍 Select Location")
            locations = ["Gachibowli", "Hitech City", "Banjara Hills"]
            cols = st.columns(len(locations))
            for i, location in enumerate(locations):
                with cols[i]:
                    if st.button(location, key=f"loc_{location}", use_container_width=True):
                        process_user_input(location)
        
        # Show available slots when AI presents slot options
        elif current_step == "slot_selection" and st.session_state.app.state.get("available_slots"):
            st.markdown("⏰ Select Appointment Slot")
            available_slots = st.session_state.app.state.get("available_slots", [])
            
            # Display all available slots as buttons with clear time display
            if available_slots:
                # Create columns based on number of slots (max 3 per row)
                slots_per_row = 3
                for i in range(0, len(available_slots), slots_per_row):
                    row_slots = available_slots[i:i+slots_per_row]
                    cols = st.columns(len(row_slots))
                    
                    for j, slot in enumerate(row_slots):
                        with cols[j]:
                            # Format the slot display
                            slot_number = i + j + 1
                            date_str = slot.date
                            time_str = slot.time
                            doctor_str = slot.doctor
                            
                            # Create a nice button label
                            button_label = f"Slot {slot_number}\n{date_str}\n{time_str}\n{doctor_str}"
                            
                            if st.button(button_label, key=f"slot_{slot_number}", use_container_width=True):
                                process_user_input(str(slot_number))

def process_user_input(user_input):
    """Process user input and update conversation"""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Process with AI agent
    with st.spinner("🤖 AI Agent is processing..."):
        try:
            response = st.session_state.app.process_user_input(user_input)
            st.session_state.messages.append({"role": "agent", "content": response})
            
            # Check if appointment is completed
            if st.session_state.app.state.get("reminders_scheduled"):
                st.session_state.appointment_completed = True
                st.balloons()  # Celebration animation!
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            st.session_state.messages.append({"role": "agent", "content": error_msg})
    
    st.rerun()

def display_completion_summary():
    """Display enhanced completion summary"""
    st.markdown("""
    <div class="celebration-box">
        🎉 <strong>Appointment Successfully Booked!</strong> 🎉
        <br><br>
        Your appointment has been confirmed and all systems have been updated.
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced metrics
    state_summary = st.session_state.app.get_state_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status = "✅ Success" if state_summary.get('excel_exported') else "❌ Failed"
        st.metric("📊 Excel Export", status)
    with col2:
        status = "✅ Sent" if state_summary.get('form_sent') else "❌ Failed"
        st.metric("📋 Forms", status)
    with col3:
        status = "✅ Scheduled" if state_summary.get('reminders_scheduled') else "❌ Not Set"
        st.metric("⏰ Reminders", status)
    with col4:
        st.metric("🏥 Status", "Complete")
    
    # Action buttons
    st.markdown("### 🎯 What's Next?")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 View Email Confirmation", type="secondary", use_container_width=True):
            st.info("📧 Email confirmation sent to your registered email address!")
    
    with col2:
        if st.button("📋 Download Forms", type="secondary", use_container_width=True):
            st.info("📋 Intake forms are available in your email. Please complete before your visit!")
    
    with col3:
        if st.button("🔄 Book Another", type="primary", use_container_width=True):
            # Reset for new booking
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def display_quick_demo():
    """Display enhanced quick demo section"""
    with st.expander("🚀 Complete Demo Walkthrough", expanded=False):
        
        # Demo steps with visual indicators
        st.markdown("""
        <div class="suggestion-card">
            <h3>🎯 Complete Demo Flow</h3>
            <p>Follow this sequence for a full system demonstration:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Step-by-step guide
        demo_steps = [
            {
                "step": "1️⃣ Start Conversation",
                "action": "Click 'Start Appointment Booking'",
                "tip": "Initiates the AI agent conversation"
            },
            {
                "step": "2️⃣ Patient Information",
                "action": "Use suggestion buttons or type: 'John Smith'",
                "tip": "AI will ask for each detail individually"
            },
            {
                "step": "3️⃣ Contact Details",
                "action": "Provide: DOB, Phone, Email one by one",
                "tip": "Use quick-fill buttons for faster demo"
            },
            {
                "step": "4️⃣ Doctor & Location",
                "action": "Select: 'Dr. Naveen' and 'Gachibowli'",
                "tip": "Click the suggestion buttons for instant selection"
            },
            {
                "step": "5️⃣ Appointment Slot",
                "action": "Choose slot number: '1', '2', or '3'",
                "tip": "Use the quick slot buttons above chat"
            },
            {
                "step": "6️⃣ Insurance Information",
                "action": "Select carrier, member ID, group number",
                "tip": "Use insurance quick-fill options"
            },
            {
                "step": "7️⃣ Confirmation",
                "action": "System automatically completes booking",
                "tip": "Watch for Excel export and form distribution"
            }
        ]
        
        for step_info in demo_steps:
            st.markdown(f"""
            <div style="margin: 1rem 0; padding: 1rem; background: #f8fafc; border-radius: 12px; border-left: 4px solid #667eea;">
                <h4 style="margin: 0 0 0.5rem 0; color: #1a365d;">{step_info['step']}</h4>
                <p style="margin: 0 0 0.5rem 0; font-weight: 500;">{step_info['action']}</p>
                <small style="color: #6b7280;">💡 {step_info['tip']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick demo tips
        st.markdown("""
        <div class="suggestion-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <h4>⚡ Pro Tips for Quick Demo</h4>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>Use the colored suggestion buttons for instant input</li>
                <li>The AI responds to natural language - type freely!</li>
                <li>Watch the progress tracker in the sidebar</li>
                <li>Each step builds on the previous one</li>
                <li>Full demo takes about 2-3 minutes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def display_system_features():
    """Display system features and capabilities"""
    st.subheader("🎯 System Features & Capabilities")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🤖 AI Agents**
        - Greeting Agent (LLM)
        - Patient Lookup Agent
        - Scheduling Agent
        - Insurance Agent
        - Confirmation Agent
        - Form Distribution Agent
        - Reminder Agent
        """)
    
    with col2:
        st.markdown("""
        **📊 Data Management**
        - 50 Synthetic Patients (CSV)
        - Doctor Schedules (Excel)
        - Smart Duration Logic
        - Excel Export for Admin
        - Professional Formatting
        """)
    
    with col3:
        st.markdown("""
        **🔄 Workflow Features**
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
        st.subheader("📊 Excel Export Data")
        
        # Try to read the appointments Excel file
        try:
            appointments_df = pd.read_excel("data/appointments.xlsx")
            
            if not appointments_df.empty:
                st.success(f"✅ Found {len(appointments_df)} appointments in Excel file")
                
                # Show the most recent appointment
                latest_appointment = appointments_df.iloc[-1]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Latest Appointment:**")
                    st.write(f"**ID**: {latest_appointment.get('appointment_id', 'N/A')}")
                    st.write(f"**Patient**: {latest_appointment.get('patient_name', 'N/A')}")
                    st.write(f"**Doctor**: {latest_appointment.get('doctor', 'N/A')}")
                    st.write(f"**Date**: {latest_appointment.get('appointment_date', 'N/A')}")
                    st.write(f"**Time**: {latest_appointment.get('appointment_time', 'N/A')}")
                
                with col2:
                    st.markdown("**Status:**")
                    st.write(f"**Excel Exported**: {'✅' if latest_appointment.get('excel_exported') else '❌'}")
                    st.write(f"**Forms Sent**: {'✅' if latest_appointment.get('form_sent') else '❌'}")
                    st.write(f"**Insurance**: {latest_appointment.get('insurance_carrier', 'N/A')}")
                    st.write(f"**Status**: {latest_appointment.get('status', 'N/A')}")
                
                # Show full data table
                with st.expander("📋 View Full Excel Data", expanded=False):
                    st.dataframe(appointments_df, width='stretch')
            else:
                st.info("📊 Excel file exists but is empty")
                
        except FileNotFoundError:
            st.warning("📊 Excel file not found. Complete an appointment booking to generate data.")
        except Exception as e:
            st.error(f"❌ Error reading Excel file: {e}")

def main():
    """Main Streamlit application"""
    # Initialize session state
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Create main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Main chat interface
        display_chat_interface()
        
        # Quick demo section
        display_quick_demo()
        
        # Excel data display
        display_excel_data()
    
    with col2:
        # Sidebar content in main area for better visibility
        display_sidebar()
    
    # System features at the bottom
    st.markdown("---")
    display_system_features()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🏥 Medical Appointment Scheduling AI Agent<br>
        <small>Built with LangGraph + LangChain | Streamlit UI | Assignment Demo</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()