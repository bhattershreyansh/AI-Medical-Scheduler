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
        min-height: 2.5rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0px 4px 12px rgba(44, 82, 130, 0.3);
        background: linear-gradient(135deg, #2a4365 0%, #2c5282 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* Secondary button styling */
    .stButton > button[kind="secondary"] {
        background: #ffffff;
        color: #2c5282;
        border: 2px solid #3182ce;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #f7fafc;
        border-color: #2c5282;
    }

    /* Suggestion Cards */
    .suggestion-card {
        background: #f7fafc;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    
    .suggestion-card:hover {
        background: #edf2f7;
        transform: translateY(-1px);
        box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Selection section styling */
    .selection-section {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    }
    
    .selection-section h3 {
        color: #2d3748;
        margin-bottom: 1rem;
        font-weight: 600;
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
            <div style="font-size: 3rem;">🏥</div>
            <div>
                <h1 style="margin: 0; font-size: 2.8rem; font-weight: 700;">MedSchedule AI</h1>
                <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">Intelligent Medical Appointment Scheduling</p>
                <p style="margin: 0; font-size: 0.9rem; opacity: 0.7;">Powered by LangGraph + LangChain Multi-Agent Architecture</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display clean sidebar focused on user experience"""
    st.markdown("### 🏥 Appointment Assistant")
    
    # Enhanced Current State
    if hasattr(st.session_state, 'app'):
        state_summary = st.session_state.app.get_state_summary()
        
        st.markdown("#### 📋 Current Status")
        
        # Current step with visual indicator
        current_step = state_summary.get('current_step', 'Not started')
        step_display = {
            'greeting': '💬 Collecting Information',
            'slot_selection': '📅 Selecting Time Slot',
            'insurance': '🏥 Processing Insurance',
            'completed': '✅ Appointment Complete'
        }
        
        step_text = step_display.get(current_step, current_step.replace('_', ' ').title())
        
        st.markdown(f"""
        <div class="suggestion-card" style="background: linear-gradient(135deg, #2c5282 0%, #3182ce 100%); color: white;">
            <h4 style="margin: 0; color: white;">{step_text}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if state_summary.get('patient_name'):
            # Get patient type from app state
            patient_type = "Unknown"
            if hasattr(st.session_state.app, 'state') and st.session_state.app.state.get('lookup_result'):
                patient_type = st.session_state.app.state['lookup_result'].patient_type.title()
            
            st.markdown(f"""
            <div class="suggestion-card">
                <h4> Patient: {state_summary['patient_name']}</h4>
                <p style="margin: 0.5rem 0 0 0; color: #4a5568; font-size: 0.9rem;">
                    Type: {patient_type} Patient
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # User-focused Progress indicators (only show what matters to user)
        if current_step != 'greeting':
            st.markdown("#### ✅ Progress")
            progress_items = [
                ("👤 Personal Info", state_summary.get('patient_name') is not None),
                ("📅 Appointment Slot", current_step in ['insurance', 'completed']),
                ("🏥 Insurance Details", current_step == 'completed'),
                ("✅ Confirmation", state_summary.get('reminders_scheduled', False))
            ]
            
            for item, completed in progress_items:
                status_icon = "✅" if completed else "⏳"
                
                st.markdown(f"""
                <div class="progress-item">
                    <span style="margin-right: 0.5rem; font-size: 1.1rem;">{status_icon}</span>
                    <span style="color: {'#2d3748' if completed else '#718096'};">{item}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # Enhanced Controls
    st.markdown("#### 🎮 Controls")
    
    if st.button("🔄 Start New Appointment", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Available Services (User-focused)
    st.markdown("#### 🏥 Available Services")
    
    services = [
        ("👨‍⚕️ Doctors", "4 specialists available"),
        ("📍 Locations", "3 convenient locations"),
        ("📅 Scheduling", "Same-day appointments"),
        ("🏥 Insurance", "Most carriers accepted"),
        ("📋 Digital Forms", "Paperless check-in"),
        ("⏰ Reminders", "Automated notifications")
    ]
    
    for service, description in services:
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 0.75rem; margin: 0.25rem 0; background: #f7fafc; border-radius: 6px; border-left: 3px solid #3182ce;">
            <div>
                <span style="font-weight: 500; color: #2d3748;">{service}</span><br>
                <small style="color: #718096;">{description}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Help Section
    st.markdown("####  Need Help?")
    
    if st.button("💡 How It Works", type="primary", use_container_width=True):
        st.info("""
        **Simple 4-Step Process:**
        1. 👤 Share your basic information
        2. 📅 Choose your preferred appointment slot
        3. 🏥 Provide insurance details
        4. ✅ Get confirmation & forms via email
        """)
    
    # Contact Info
    st.markdown("#### 📞 Contact")
    st.markdown("""
    <div style="background: #f7fafc; padding: 1rem; border-radius: 8px; text-align: center;">
        <p style="margin: 0; color: #2d3748;"><strong>📞 (555) 123-4567</strong></p>
        <p style="margin: 0; color: #718096;"><small>For assistance or changes</small></p>
    </div>
    """, unsafe_allow_html=True)

def display_chat_interface():
    """Display the enhanced chat interface with clickable options"""
    st.subheader("🤖 AI Agent Conversation")
    
    # Chat container with better styling
    chat_container = st.container()
    
    with chat_container:
        # Display conversation history
        if st.session_state.messages:
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
                        <strong>🤖 AI Agent:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Welcome message when no conversation started
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #f7fafc; border-radius: 12px; margin: 1rem 0;">
                <h3 style="color: #2d3748; margin-bottom: 1rem;">👋 Welcome to Medical Scheduling AI</h3>
                <p style="color: #4a5568; margin-bottom: 1.5rem;">I'm here to help you schedule your medical appointment quickly and easily.</p>
                <p style="color: #718096; font-size: 0.9rem;">Click "Start Appointment Booking" below to begin!</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Input area with smart suggestions
    if not st.session_state.appointment_completed:
        if not st.session_state.conversation_started:
            st.markdown("###  Ready to Schedule Your Appointment?")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🏥 Start Appointment Booking", type="primary", use_container_width=True):
                    greeting = st.session_state.app.start_conversation()
                    st.session_state.messages.append({"role": "agent", "content": greeting})
                    st.session_state.conversation_started = True
                    st.rerun()
            with col2:
                if st.button("⚡ Quick Demo", type="secondary", use_container_width=True):
                    demo_response = "Hello! I'm your AI scheduling assistant. Let me help you book an appointment. I'll need some basic information from you. Let's start with your full name."
                    st.session_state.messages.append({"role": "agent", "content": demo_response})
                    st.session_state.conversation_started = True
                    st.rerun()
        else:
            # Show smart suggestions based on conversation context
            current_step = st.session_state.app.state.get("current_step", "greeting")
            display_smart_suggestions(current_step)
            
            # Always show text input for manual entry
            st.markdown("---")
            user_input = st.chat_input(" Type your message here or use the buttons above...")
            
            if user_input:
                process_user_input(user_input)
    else:
        display_completion_summary()

def display_smart_suggestions(current_step):
    """Display context-aware selection options based on AI conversation"""
    
    if not st.session_state.messages:
        return
    
    # Get the last agent message to understand what input is needed
    last_agent_message = ""
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "agent":
            last_agent_message = msg["content"].lower()
            break
    
    # Check if we're waiting for user input (no selection buttons should show if agent is still processing)
    if "✅" in last_agent_message or "confirmed" in last_agent_message or "selected" in last_agent_message:
        return  # Don't show selection options if something was already selected
    
    # Only show suggestions if the agent is specifically asking for that information
    if ("which doctor" in last_agent_message or "preferred doctor" in last_agent_message or 
        "doctor would you prefer" in last_agent_message or "choose a doctor" in last_agent_message):
        
        # Check if doctor was already selected in conversation
        doctor_selected = any("dr." in msg["content"].lower() and msg["role"] == "user" 
                             for msg in st.session_state.messages[-5:])  # Check last 5 messages
        
        if not doctor_selected:
            st.markdown("""
            <div class="selection-section">
                <h3> Select Your Preferred Doctor</h3>
            </div>
            """, unsafe_allow_html=True)
            
            doctors = ["Dr. Naveen", "Dr. Aish", "Dr. Shreyansh", "Dr. Naresh"]
            cols = st.columns(2)
            for i, doctor in enumerate(doctors):
                with cols[i % 2]:
                    if st.button(f" {doctor}", key=f"doc_{doctor}", use_container_width=True, type="secondary"):
                        process_user_input(doctor)
    
    elif ("which location" in last_agent_message or "preferred location" in last_agent_message or 
          "location would you prefer" in last_agent_message or "choose a location" in last_agent_message):
        
        # Check if location was already selected
        location_selected = any(loc in msg["content"].lower() and msg["role"] == "user" 
                               for msg in st.session_state.messages[-5:] 
                               for loc in ["gachibowli", "jubliee hills", "banjara hills"])
        
        if not location_selected:
            st.markdown("""
            <div class="selection-section">
                <h3>📍 Select Your Preferred Location</h3>
            </div>
            """, unsafe_allow_html=True)
            
            locations = ["Gachibowli", "Jubliee Hills", "Banjara Hills"]
            cols = st.columns(3)
            for i, location in enumerate(locations):
                with cols[i]:
                    if st.button(f"🏥 {location}", key=f"loc_{location}", use_container_width=True, type="secondary"):
                        process_user_input(location)
    
    elif current_step == "slot_selection" and st.session_state.app.state.get("available_slots"):
        available_slots = st.session_state.app.state.get("available_slots", [])
        
        # Get patient type for duration display
        patient_type = "new"
        if st.session_state.app.state.get('lookup_result'):
            patient_type = st.session_state.app.state['lookup_result'].patient_type
        duration = 60 if patient_type == "new" else 30
        
        # Check if slot was already selected
        slot_selected = any(("slot" in msg["content"].lower() or msg["content"].isdigit()) and msg["role"] == "user" 
                           for msg in st.session_state.messages[-3:])
        
        if (available_slots and not slot_selected and 
            ("select" in last_agent_message or "choose" in last_agent_message or 
             "slot" in last_agent_message or "appointment" in last_agent_message)):
            
            st.markdown(f"""
            <div class="selection-section">
                <h3> Select Your Appointment Slot</h3>
                <p style="color: #4a5568; margin-bottom: 1rem;">
                    Duration: {duration} minutes ({patient_type.title()} Patient)
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display slots in a clean card format
            for i, slot in enumerate(available_slots):
                slot_number = i + 1
                
                # Create a card-like display for each slot
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="padding: 1.2rem; border: 2px solid #e2e8f0; border-radius: 10px; margin: 0.5rem 0; background: #ffffff; box-shadow: 0px 2px 4px rgba(0,0,0,0.05);">
                        <h4 style="margin: 0 0 0.5rem 0; color: #2d3748; font-weight: 600;">📋 Slot {slot_number}</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                            <p style="margin: 0; color: #4a5568;"><strong> Date:</strong> {slot.date}</p>
                            <p style="margin: 0; color: #4a5568;"><strong> Time:</strong> {slot.time}</p>
                            <p style="margin: 0; color: #4a5568;"><strong> Doctor:</strong> {slot.doctor}</p>
                            <p style="margin: 0; color: #4a5568;"><strong> Location:</strong> {slot.location}</p>
                            <p style="margin: 0; color: #4a5568;"><strong> Duration:</strong> {duration} minutes</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f" Select", key=f"slot_{slot_number}", use_container_width=True, type="primary"):
                        process_user_input(str(slot_number))
    
    elif ("insurance" in last_agent_message and ("carrier" in last_agent_message or "provider" in last_agent_message or
                                                "company" in last_agent_message)):
        
        # Check if insurance was already selected
        insurance_selected = any("insurance" in msg["content"].lower() and msg["role"] == "user" 
                                for msg in st.session_state.messages[-3:])
        
        if not insurance_selected:
            st.markdown("""
            <div class="selection-section">
                <h3> Select Your Insurance Carrier</h3>
            </div>
            """, unsafe_allow_html=True)
            
            carriers = ["Blue Cross Blue Shield", "Aetna", "Cigna"]
            cols = st.columns(2)
            for i, carrier in enumerate(carriers):
                with cols[i % 2]:
                    if st.button(f"🏥 {carrier}", key=f"ins_{carrier}", use_container_width=True, type="secondary"):
                        process_user_input(carrier)

def process_user_input(user_input):
    """Process user input and update conversation"""
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.spinner("🤖 Processing your request..."):
        try:
            response = st.session_state.app.process_user_input(user_input)
            
            # Clean up response for presentation (remove technical details)
            clean_response = clean_response_for_presentation(response)
            st.session_state.messages.append({"role": "agent", "content": clean_response})
            
            if st.session_state.app.state.get("current_step") == "completed":
                st.session_state.appointment_completed = True
                st.balloons()  # Celebration for completed appointment
                
        except Exception as e:
            # Log technical error to console but show user-friendly message
            print(f" Technical Error: {str(e)}")
            error_msg = "I apologize, but I encountered an issue. Please try again or contact our support team."
            st.session_state.messages.append({"role": "agent", "content": error_msg})
    
    st.rerun()

def clean_response_for_presentation(response):
    """Clean up agent response for better presentation"""
    # Remove technical markers and logs
    lines = response.split('\n')
    clean_lines = []
    
    for line in lines:
        # Skip technical log lines
        if any(marker in line for marker in ['✅', '📊', '📧', '🔄', 'Updated', 'exported', 'logged']):
            continue
        # Skip lines that start with technical indicators
        if line.strip().startswith(('✅', '📊', '📧', '🔄')):
            continue
        # Keep user-relevant content
        clean_lines.append(line)
    
    clean_response = '\n'.join(clean_lines).strip()
    
    # If response is too short after cleaning, return original
    if len(clean_response) < 50:
        return response
    
    return clean_response

def display_completion_summary():
    """Display enhanced completion summary"""
    st.markdown("""
    <div class="celebration-box">
         Appointment Successfully Booked! 🎉
        <br><br>
        Your appointment has been confirmed and all systems have been updated.
        <br>
        <small style="opacity: 0.8;">Thank you for choosing our medical practice!</small>
    </div>
    """, unsafe_allow_html=True)
    
    state_summary = st.session_state.app.get_state_summary()
    
    # Enhanced metrics display
    st.markdown("###  Booking Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = " Success" if state_summary.get('excel_exported') else " Failed"
        color = "#38a169" if state_summary.get('excel_exported') else "#e53e3e"
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: {color}; color: white; border-radius: 8px;">
            <h3 style="margin: 0; color: white;">📊</h3>
            <p style="margin: 0; color: white;">Excel Export</p>
            <small style="color: white; opacity: 0.9;">{status}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status = " Sent" if state_summary.get('form_sent') else " Failed"
        color = "#38a169" if state_summary.get('form_sent') else "#e53e3e"
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: {color}; color: white; border-radius: 8px;">
            <h3 style="margin: 0; color: white;">📋</h3>
            <p style="margin: 0; color: white;">Forms</p>
            <small style="color: white; opacity: 0.9;">{status}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        status = " Scheduled" if state_summary.get('reminders_scheduled') else " Not Set"
        color = "#38a169" if state_summary.get('reminders_scheduled') else "#e53e3e"
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: {color}; color: white; border-radius: 8px;">
            <h3 style="margin: 0; color: white;">⏰</h3>
            <p style="margin: 0; color: white;">Reminders</p>
            <small style="color: white; opacity: 0.9;">{status}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: #38a169; color: white; border-radius: 8px;">
            <h3 style="margin: 0; color: white;">✅</h3>
            <p style="margin: 0; color: white;">Status</p>
            <small style="color: white; opacity: 0.9;">Complete</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 🚀 Next Steps")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(" View Email Confirmation", type="secondary", use_container_width=True):
            st.success(" Email confirmation sent to your registered email address")
    
    with col2:
        if st.button(" Download Forms", type="secondary", use_container_width=True):
            st.success(" Intake forms are available in your email")
    
    with col3:
        if st.button(" Book Another Appointment", type="primary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def display_quick_demo():
    """Display presentation-focused demo section"""
    with st.expander("Quick Demo Guide", expanded=False):
        
        st.markdown("""
        <div class="suggestion-card" style="background: linear-gradient(135deg, #2c5282 0%, #3182ce 100%); color: white;">
            <h3 style="color: white; margin-bottom: 1rem;">🎯 Demo Flow (2-3 minutes)</h3>
            <p style="color: white; opacity: 0.9;">Follow this sequence for a complete demonstration:</p>
        </div>
        """, unsafe_allow_html=True)
        
        demo_steps = [
            ("1️⃣ Start", "Click 'Start Appointment Booking'", "Begin the AI conversation"),
            ("2️⃣ Name", "Enter: 'John Smith'", "AI will guide you through each step"),
            ("3️⃣ Details", "Provide DOB, Phone, Email", "Use natural language or buttons"),
            ("4️⃣ Preferences", "Select Doctor & Location", "Click the suggestion buttons"),
            ("5️⃣ Schedule", "Choose appointment slot", "Pick from available times"),
            ("6️⃣ Insurance", "Select insurance carrier", "Quick selection options"),
            ("7️⃣ Complete", "Automatic confirmation", "System handles the rest")
        ]
        
        for step, action, tip in demo_steps:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 0.75rem 0; padding: 1rem; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0px 2px 4px rgba(0,0,0,0.05);">
                <div style="margin-right: 1rem; font-size: 1.5rem;">{step}</div>
                <div style="flex: 1;">
                    <div style="font-weight: 500; color: #2d3748;">{action}</div>
                    <div style="font-size: 0.9rem; color: #718096;">{tip}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #f0fff4; border: 1px solid #9ae6b4; border-radius: 8px; padding: 1rem; margin-top: 1rem;">
            <h4 style="color: #2f855a; margin: 0 0 0.5rem 0;">💡 Presentation Tips</h4>
            <ul style="margin: 0; color: #2f855a;">
                <li>Use the colored buttons for quick selections</li>
                <li>Watch the progress tracker in the sidebar</li>
                <li>Natural language input works too</li>
                <li>System automatically handles backend processes</li>
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
    
    # Main layout - focus on chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        display_chat_interface()
        
        # Only show demo section if appointment not completed
        if not st.session_state.appointment_completed:
            display_quick_demo()
    
    with col2:
        display_sidebar()
    
    # Show Excel data only after completion for presentation
    if st.session_state.appointment_completed:
        st.markdown("---")
        display_excel_data()
        st.markdown("---")
        display_system_features()
    
    # Clean footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; padding: 1rem;">
        🏥 <strong>MedSchedule AI</strong> - Intelligent Medical Appointment Scheduling
        <br>
        <small>Powered by LangGraph + LangChain Multi-Agent Architecture</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()