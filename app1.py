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

# Custom CSS for better styling
# ------------------------
# 🌟 Enhanced Styling
# ------------------------
st.markdown("""
<style>
    /* General */
    body {
        background-color: #fafafa;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1a73e8;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #ffffff, #eaf3ff);
        border-radius: 16px;
        border: 1px solid #d6e4ff;
        box-shadow: 0px 4px 12px rgba(26, 115, 232, 0.1);
    }

    /* Step Headers */
    .step-header {
        font-size: 1.3rem;
        color: #2e7d32;
        margin: 1rem 0;
        padding: 0.5rem 1rem;
        background: #f1fdf3;
        border-left: 4px solid #2e7d32;
        border-radius: 6px;
        font-weight: 500;
    }

    /* Chat */
    .chat-message {
        padding: 0.8rem 1rem;
        margin: 0.6rem 0;
        border-radius: 16px;
        max-width: 75%;
        line-height: 1.5;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        animation: fadeIn 0.4s ease-in-out;
    }
    .user-message {
        background: #e3f2fd;
        border: 1px solid #bbdefb;
        margin-left: auto;
        text-align: right;
    }
    .agent-message {
        background: #f3e5f5;
        border: 1px solid #e1bee7;
        margin-right: auto;
        text-align: left;
    }

    /* Cards */
    .info-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #eee;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    /* Success Celebration */
    .celebration-box {
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        font-size: 1.2rem;
        background: linear-gradient(135deg, #e3f2fd, #e8f5e9);
        border: 1px solid #c8e6c9;
        color: #1b5e20;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }

    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(10px);}
        to {opacity: 1; transform: translateY(0);}
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
    """Display the main header"""
    st.markdown("""
    <div class="main-header">
        🏥 Medical Appointment Scheduling AI Agent
        <br><small>LangGraph + LangChain Multi-Agent System</small>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with system information and controls"""
    with st.sidebar:
        st.header("🔧 System Information")
        
        # System status
        st.subheader("📊 System Status")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Agents", "7", help="Total number of AI agents")
            st.metric("Database", "50", help="Patients in database")
        
        with col2:
            st.metric("Doctors", "4", help="Available doctors")
            st.metric("Locations", "3", help="Available locations")
        
        # Current state
        if hasattr(st.session_state, 'app'):
            state_summary = st.session_state.app.get_state_summary()
            
            st.subheader("🎯 Current State")
            st.write(f"**Step**: {state_summary.get('current_step', 'Not started')}")
            
            if state_summary.get('patient_name'):
                st.write(f"**Patient**: {state_summary['patient_name']}")
            
            # Progress indicators
            st.subheader("✅ Progress")
            progress_items = [
                ("Patient Info", state_summary.get('patient_name') is not None),
                ("Excel Export", state_summary.get('excel_exported', False)),
                ("Forms Sent", state_summary.get('form_sent', False)),
                ("Reminders", state_summary.get('reminders_scheduled', False))
            ]
            
            for item, completed in progress_items:
                icon = "✅" if completed else "⏳"
                st.write(f"{icon} {item}")
        
        # Reset button
        st.subheader("🔄 Controls")
        if st.button("🔄 Reset Session", type="secondary"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        # Assignment info
        st.subheader("📋 Assignment Info")
        st.info("""
        **Features Implemented:**
        - Patient Greeting (LLM)
        - Patient Lookup (CSV DB)
        - Smart Scheduling (30/60 min)
        - Insurance Collection
        - Excel Export
        - Form Distribution
        - 3-Tier Reminder System
        """)

def display_chat_interface():
    """Display the main chat interface"""
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
    
    # Input area
    if not st.session_state.appointment_completed:
        # Start conversation if not started
        if not st.session_state.conversation_started:
            if st.button("🚀 Start Appointment Booking", type="primary", use_container_width=True):
                greeting = st.session_state.app.start_conversation()
                st.session_state.messages.append({"role": "agent", "content": greeting})
                st.session_state.conversation_started = True
                st.rerun()
        else:
            # User input
            user_input = st.chat_input("Type your message here...")
            
            if user_input:
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
    else:
        st.success("🎉 Appointment booking completed successfully!")
        
        # Show completion summary
        state_summary = st.session_state.app.get_state_summary()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Excel Export", "Success" if state_summary.get('excel_exported') else "Failed")
        with col2:
            st.metric("📋 Forms Sent", "Success" if state_summary.get('form_sent') else "Failed")
        with col3:
            st.metric("⏰ Reminders", "Scheduled" if state_summary.get('reminders_scheduled') else "Not Set")

def display_quick_demo():
    """Display quick demo section"""
    with st.expander("🚀 Step-by-Step Demo Guide", expanded=False):
        st.markdown("""
        **The system will guide you through each step:**
        
        **Step 1: Patient Information** (one at a time)
        1. Full name: `John Smith`
        2. Date of birth: `01/15/1990`
        3. Phone number: `5551234567`
        4. Email: `john@test.com`
        5. Doctor: `Dr. Naveen`
        6. Location: `Gachibowli`
        
        **Step 2: Appointment Selection**
        - Choose slot number: `1`
        
        **Step 3: Insurance Information** (one at a time)
        1. Insurance carrier: `Blue Cross Blue Shield`
        2. Member ID: `BC123456789`
        3. Group number: `GRP001`
        
        **The system will ask for each piece of information individually!**
        """)
        
        st.info("💡 **Tip**: The AI will guide you step-by-step. Just answer one question at a time!")

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